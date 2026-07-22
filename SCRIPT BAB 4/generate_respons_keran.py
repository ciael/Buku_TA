"""
generate_respons_keran.py
Membuat grafik respons tekanan dan duty cycle per kondisi keran (Tabel 4.16)
dari uji_NN_uji1_16juni.csv. Filter nn_mode==1 saja agar fase reset operator
tidak ikut tergambar.
Output: gambar/respons_tekanan_keranX.png dan respons_duty_keranX.png
"""
import matplotlib
matplotlib.use('Agg')
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

HERE   = os.path.dirname(os.path.abspath(__file__))
ROOT   = os.path.dirname(HERE)
CSV    = os.path.join(ROOT, "DATA UJI", "uji_NN_uji1_16juni.csv")
GAMBAR = os.path.join(ROOT, "Template_agath", "gambar")

plt.rcParams.update({
    'font.family': 'Times New Roman',
    'font.size': 10,
    'axes.grid': True,
    'grid.linestyle': '--',
    'grid.alpha': 0.4,
})

df = pd.read_csv(CSV)
for c in ['pressure_bar', 'duty_percent', 'valve_open_count', 'nn_mode', 'setpoint_bar']:
    df[c] = pd.to_numeric(df[c], errors='coerce')

SP = 0.30

colors = {0: '#9467bd', 1: '#d62728', 2: '#2ca02c', 3: '#ff7f0e', 4: '#1f77b4'}

# Hanya baris nn_mode == 1
nn = df[df['nn_mode'] == 1].copy()

for keran in sorted(nn['valve_open_count'].dropna().unique()):
    seg = nn[nn['valve_open_count'] == keran].copy()
    seg = seg.sort_values('pressure_bar')  # gunakan index asli
    # reset waktu relatif dari awal segmen
    seg = seg.sort_index()
    t0 = pd.to_datetime(seg['pc_timestamp']).iloc[0]
    seg['tr'] = (pd.to_datetime(seg['pc_timestamp']) - t0).dt.total_seconds()

    k = int(keran)
    c = colors.get(k, 'k')

    # hitung steady state (rata-rata 8 dtk terakhir)
    t_end = seg['tr'].max()
    tail = seg[seg['tr'] >= t_end - 8]
    p_settle = tail['pressure_bar'].mean()
    err = SP - p_settle

    # ── Grafik Tekanan ──────────────────────────────────────────────────────
    fig, ax = plt.subplots(figsize=(5, 3))
    ax.plot(seg['tr'], seg['pressure_bar'], color=c, lw=1.8, label='Tekanan (bar)')
    ax.axhline(SP, color='red', ls='--', lw=1.3, label=f'Setpoint {SP} bar')
    ax.axhspan(SP - 0.02, SP + 0.02, color='red', alpha=0.08)

    lo = min(seg['pressure_bar'].min(), SP - 0.03) - 0.02
    hi = max(seg['pressure_bar'].max(), SP + 0.03) + 0.02
    ax.set_ylim(lo, hi)
    ax.set_xlabel('Waktu sejak NN aktif (s)', fontsize=10)
    ax.set_ylabel('Tekanan (bar)', fontsize=10)
    ax.set_title(f'Respons Tekanan — {k} keran\n(Setpoint {SP} bar)', fontsize=11, fontweight='bold')

    sign = '+' if err >= 0 else ''
    ax.text(0.02, 0.97,
            f'Steady: {p_settle:.3f} bar  |  Error: {sign}{err:.3f} bar',
            transform=ax.transAxes, va='top', fontsize=8.5,
            bbox=dict(boxstyle='round,pad=0.3', fc='lightyellow', ec='gray', alpha=0.85))
    ax.legend(fontsize=9, loc='lower right')
    plt.tight_layout()
    out_p = os.path.join(GAMBAR, f'respons_tekanan_keran{k}.png')
    plt.savefig(out_p, dpi=180, bbox_inches='tight')
    plt.close('all')
    print(f'[keran {k}] tekanan -> {out_p}  (steady={p_settle:.3f}, err={sign}{err:.3f})')

    # ── Grafik Duty Cycle ───────────────────────────────────────────────────
    fig, ax = plt.subplots(figsize=(5, 3))
    ax.plot(seg['tr'], seg['duty_percent'], color=c, lw=1.8)
    ax.axhline(95, color='gray', ls=':', lw=0.9, alpha=0.7, label='Batas atas 95%')
    ax.axhline(70, color='gray', ls=':', lw=0.9, alpha=0.7, label='Batas bawah 70%')
    ax.set_ylim(67, 98)
    ax.set_xlabel('Waktu sejak NN aktif (s)', fontsize=10)
    ax.set_ylabel('Duty Cycle (%)', fontsize=10)
    ax.set_title(f'Duty Cycle — {k} keran', fontsize=11, fontweight='bold')
    ax.legend(fontsize=9)
    plt.tight_layout()
    out_d = os.path.join(GAMBAR, f'respons_duty_keran{k}.png')
    plt.savefig(out_d, dpi=180, bbox_inches='tight')
    plt.close('all')
    print(f'[keran {k}] duty    -> {out_d}')

print('\nSelesai.')
