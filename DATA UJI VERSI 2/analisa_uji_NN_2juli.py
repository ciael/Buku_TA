# -*- coding: utf-8 -*-
"""
Cleaning + analisa pengujian closed-loop NN: uji_NN_2juli.csv
Skenario: penolakan gangguan beban, keran ditutup bertahap 4 -> 3 -> 2 -> 1 -> 0.
Setpoint 0,30 bar. Semua output disimpan di folder DATA UJI ini.

Output:
  - uji_NN_2juli_clean.csv                (data bersih)
  - uji_NN_2juli_pressure_duty.png        (tekanan & duty vs waktu, fase diberi warna)
  - uji_NN_2juli_error_per_fase.png       (galat tunak per jumlah keran)
  - uji_NN_2juli_listrik.png              (tegangan & arus vs waktu)
"""
import os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
SRC  = os.path.join(HERE, 'uji_NN_2juli.csv')
SETPOINT = 0.30
DUTY_MIN = 70.0
VOLT_MIN = 50.0   # ambang motor dianggap menyala

# ================= 1. CLEANING =================
d = pd.read_csv(SRC)
n0 = len(d)

# (a) buang kolom 'event' (100% kosong)
if 'event' in d.columns and d['event'].isna().all():
    d = d.drop(columns=['event'])

# (b) pastikan numerik
numcols = ['pressure_bar','duty_percent','setpoint_bar','valve_open_count',
           'jsy_voltage_rms_v','jsy_current_rms_a','jsy_active_power_w']
for c in numcols:
    d[c] = pd.to_numeric(d[c], errors='coerce')
d = d.dropna(subset=['pressure_bar','duty_percent','valve_open_count','setpoint_bar']).reset_index(drop=True)

# (c) waktu relatif
t = pd.to_datetime(d['pc_timestamp'])
d['t_rel'] = (t - t.iloc[0]).dt.total_seconds()

# (d) buang ekor SHUTDOWN: baris pertama (di fase akhir) saat pompa dimatikan,
#     ditandai duty di bawah clamp (<70) ATAU tegangan drop (<50 V). Semua baris
#     sesudah titik itu dibuang karena bukan kendali NN, melainkan mematikan alat.
mask_shutdown = (d['duty_percent'] < DUTY_MIN) | (d['jsy_voltage_rms_v'] < VOLT_MIN)
if mask_shutdown.any():
    cut = d.index[mask_shutdown][0]
    d = d.iloc[:cut].reset_index(drop=True)

# (e) galat
d['error'] = d['setpoint_bar'] - d['pressure_bar']

d.to_csv(os.path.join(HERE, 'uji_NN_2juli_clean.csv'), index=False)
print('== CLEANING ==')
print(f'  baris awal        : {n0}')
print(f'  baris shutdown dibuang: {n0 - len(d)}')
print(f'  baris bersih      : {len(d)}')
print(f'  durasi bersih (s) : {d["t_rel"].iloc[-1]:.1f}')
print()

# ================= 2. STATISTIK PER FASE (per jumlah keran) =================
# waktu transisi (saat valve_open_count berubah)
trans = d[d['valve_open_count'].diff().fillna(0) != 0][['t_rel','valve_open_count']]
print('== TRANSISI KERAN ==')
print(trans.to_string(index=False))
print()

# steady-state: buang 5 detik pertama tiap fase (transien) lalu rata-ratakan
rows = []
segs = []
bounds = list(d['t_rel'][d['valve_open_count'].diff().fillna(0) != 0])
edges = [d['t_rel'].iloc[0]] + bounds + [d['t_rel'].iloc[-1] + 1e-6]
# bangun segmen fase berdasarkan valve_open_count kontigu
d['seg'] = (d['valve_open_count'].diff().fillna(0) != 0).cumsum()
for s, g in d.groupby('seg'):
    kv = int(g['valve_open_count'].iloc[0])
    t0, t1 = g['t_rel'].iloc[0], g['t_rel'].iloc[-1]
    ss = g[g['t_rel'] >= t0 + 5.0]           # buang 5s transien
    if len(ss) < 3: ss = g
    rows.append({
        'keran': kv, 't_mulai': round(t0,1), 't_akhir': round(t1,1), 'durasi': round(t1-t0,1),
        'n': len(g),
        'P_mean': round(ss['pressure_bar'].mean(),4),
        'P_std': round(ss['pressure_bar'].std(),4),
        'error_mean': round(ss['error'].mean(),4),
        'abs_err_mean': round(ss['error'].abs().mean(),4),
        'duty_mean': round(ss['duty_percent'].mean(),2),
        'V_mean': round(ss['jsy_voltage_rms_v'].mean(),1),
        'I_mean': round(ss['jsy_current_rms_a'].mean(),3),
    })
    segs.append((kv, t0, t1))
stat = pd.DataFrame(rows)
print('== STEADY-STATE PER FASE (transien 5s pertama dibuang) ==')
print(stat.to_string(index=False))
stat.to_csv(os.path.join(HERE, 'uji_NN_2juli_ringkasan_fase.csv'), index=False)
print()

# ================= 3. WAKTU PEMULIHAN tiap transisi =================
# setelah keran ditutup, tekanan menyimpang lalu NN mengembalikan ke band +-0.01 bar
BAND = 0.01
print('== WAKTU PEMULIHAN (kembali ke +-%.3f bar dari setpoint) =='%BAND)
tvals = trans['t_rel'].tolist(); kvals = trans['valve_open_count'].tolist()
for tt, kk in zip(tvals, kvals):
    seg = d[(d['t_rel'] >= tt) & (d['t_rel'] <= tt + 40)]
    inb = seg[seg['error'].abs() <= BAND]
    if len(inb):
        trec = inb['t_rel'].iloc[0] - tt
        peak = seg['pressure_bar'].max()
        print(f'  -> {int(kk)} keran (t={tt:.1f}s): puncak P={peak:.3f} bar, pulih dalam {trec:.1f} s')
    else:
        peak = seg['pressure_bar'].max(); ess = seg['error'].abs().iloc[-min(5,len(seg)):].mean()
        print(f'  -> {int(kk)} keran (t={tt:.1f}s): TIDAK kembali ke band (saturasi). '
              f'P~{seg["pressure_bar"].iloc[-5:].mean():.3f} bar, galat sisa ~{ess:.3f} bar')
print()

# ================= 4. PLOT (latar polos, tanpa blok warna) =================
def fase_markers(ax, ytext):
    """Tandai transisi keran dengan garis putus-putus tipis + label, latar tetap putih."""
    for kv, t0, t1 in segs:
        if t0 > d['t_rel'].iloc[0] + 1e-6:
            ax.axvline(t0, color='#888888', ls=':', lw=1.0, zorder=1)
        ax.text((t0+t1)/2, ytext, f'{kv} keran', ha='center', va='top',
                fontsize=9, color='#333')

# -- Plot utama: tekanan & duty vs waktu --
fig, ax1 = plt.subplots(figsize=(12,5.5))
fase_markers(ax1, 0.455)
ax1.plot(d['t_rel'], d['pressure_bar'], 'b-', lw=1.6, label='Tekanan aktual')
ax1.axhline(SETPOINT, color='g', ls='--', lw=1.5, label='Setpoint 0,30 bar')
ax1.set_xlabel('Waktu (s)'); ax1.set_ylabel('Tekanan (bar)', color='b')
ax1.set_ylim(0, 0.46); ax1.tick_params(axis='y', labelcolor='b')
ax2 = ax1.twinx()
ax2.plot(d['t_rel'], d['duty_percent'], color='#d62728', lw=1.3, alpha=0.8, label='Duty (NN)')
ax2.set_ylabel('Duty cycle (%)', color='#d62728'); ax2.set_ylim(65, 97)
ax2.tick_params(axis='y', labelcolor='#d62728')
l1,lab1=ax1.get_legend_handles_labels(); l2,lab2=ax2.get_legend_handles_labels()
ax1.legend(l1+l2, lab1+lab2, loc='lower left', fontsize=9)
plt.title('Respons Kendali NN: Penutupan Keran Bertahap 4 -> 0 (Setpoint 0,30 bar)')
plt.tight_layout(); plt.savefig(os.path.join(HERE,'uji_NN_2juli_pressure_duty.png'), dpi=160)
plt.close()

# -- Bar: galat tunak per fase (satu warna netral) --
fig, ax = plt.subplots(figsize=(8,5))
order = stat.sort_values('keran', ascending=False)
bars = ax.bar([f'{k} keran' for k in order['keran']], order['abs_err_mean'],
              color='#7f7f7f', edgecolor='k')
ax.axhline(0.009, color='r', ls='--', label='batas galat 0,009 bar (klaim TA)')
for b,v in zip(bars, order['abs_err_mean']):
    ax.text(b.get_x()+b.get_width()/2, v, f'{v:.3f}', ha='center', va='bottom', fontsize=10)
ax.set_ylabel('|galat| tunak rata-rata (bar)')
ax.set_title('Galat Tunak per Kondisi Beban Keran')
ax.legend(); plt.tight_layout()
plt.savefig(os.path.join(HERE,'uji_NN_2juli_error_per_fase.png'), dpi=160); plt.close()

# -- Listrik: tegangan & arus vs waktu --
fig, ax1 = plt.subplots(figsize=(12,5))
fase_markers(ax1, d['jsy_voltage_rms_v'].max())
ax1.plot(d['t_rel'], d['jsy_voltage_rms_v'], color='#8c564b', lw=1.4, label='Tegangan RMS (V)')
ax1.set_xlabel('Waktu (s)'); ax1.set_ylabel('Tegangan RMS (V)', color='#8c564b')
ax2 = ax1.twinx()
ax2.plot(d['t_rel'], d['jsy_current_rms_a'], color='#2ca02c', lw=1.2, label='Arus RMS (A)')
ax2.set_ylabel('Arus RMS (A)', color='#2ca02c')
l1,lab1=ax1.get_legend_handles_labels(); l2,lab2=ax2.get_legend_handles_labels()
ax1.legend(l1+l2, lab1+lab2, loc='lower left', fontsize=9)
plt.title('Tegangan & Arus Keluaran selama Pengujian')
plt.tight_layout(); plt.savefig(os.path.join(HERE,'uji_NN_2juli_listrik.png'), dpi=160); plt.close()

print('== FILE OUTPUT ==')
for f in ['uji_NN_2juli_clean.csv','uji_NN_2juli_ringkasan_fase.csv',
          'uji_NN_2juli_pressure_duty.png','uji_NN_2juli_error_per_fase.png','uji_NN_2juli_listrik.png']:
    print('  ', f)
