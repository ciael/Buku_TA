"""
generate_grafik_pengujian.py
Menghasilkan 3 grafik pengujian untuk Bab 4 Tugas Akhir:
  1. Grafik Duty Cycle vs Tegangan (Tabel 4.5 - Beban Lampu)
  2. Grafik Duty Cycle vs Tegangan (Tabel 4.6 - Beban Pompa Air)
  3. Grafik Tekanan vs Nilai Bit ADC (Tabel 4.4 - Sensor Tekanan)
Output: disimpan di folder yang sama dengan script ini.
"""

import matplotlib
matplotlib.use('Agg')  # non-interactive backend, tidak perlu layar
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import os

OUT_DIR = os.path.dirname(os.path.abspath(__file__))

plt.rcParams.update({
    'font.family': 'Times New Roman',
    'font.size': 13,
    'axes.titlesize': 12,
    'axes.titleweight': 'bold',
    'axes.labelsize': 15,
    'axes.labelweight': 'bold',
    'xtick.labelsize': 13,
    'ytick.labelsize': 13,
    'legend.fontsize': 12,
    'axes.grid': True,
    'grid.linestyle': '--',
    'grid.alpha': 0.5,
    'figure.dpi': 150,
})

# ─────────────────────────────────────────────────────────────────────────────
# DATA
# ─────────────────────────────────────────────────────────────────────────────

# Tabel 4.5 — Beban Lampu Pijar 10 W
duty_lampu    = [25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75, 80, 85, 90, 95]
v_teori_lampu = [55.00, 66.00, 77.00, 88.00, 99.00, 110.00, 121.00,
                 132.00, 143.00, 154.00, 165.00, 176.00, 187.00, 198.00, 209.00]
v_ukur_lampu  = [38.48, 65.10, 75.90, 87.00, 98.40, 109.50, 120.50,
                 131.60, 142.60, 153.70, 164.90, 176.10, 187.20, 198.30, 209.50]
error_lampu   = [30.04, 1.36, 1.43, 1.14, 0.61, 0.45, 0.41,
                 0.30, 0.28, 0.19, 0.06, 0.06, 0.11, 0.15, 0.24]

# Tabel 4.6 — Beban Pompa Air
duty_pompa    = [70, 75, 80, 85, 90, 95]
v_teori_pompa = [154.00, 165.00, 176.00, 187.00, 198.00, 209.00]
v_out_pompa   = [155.5, 164.5, 174.9, 185.7, 196.6, 207.3]
arus_pompa    = [0.808, 0.825, 0.821, 0.808, 0.774, 0.761]
error_pompa   = [0.97, 0.30, 0.62, 0.70, 0.71, 0.81]

# Tabel 4.4 — Sensor Tekanan
adc_bit  = [469, 492, 510, 500, 594]
tekanan  = [0.150, 0.256, 0.287, 0.307, 0.606]
v_adc    = [0.376, 0.399, 0.404, 0.413, 0.480]


# ─────────────────────────────────────────────────────────────────────────────
# GRAFIK 1 — Beban Lampu: Duty Cycle vs Tegangan
# ─────────────────────────────────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(8, 5))

ax.plot(duty_lampu, v_teori_lampu, 'b--o', label='$V_{teoritis}$ = D × 220 V',
        markersize=6, linewidth=1.5)
ax.plot(duty_lampu, v_ukur_lampu,  'r-s',  label='$V_{terukur}$ RMS',
        markersize=6, linewidth=1.5)
ax.axvspan(23, 27, alpha=0.12, color='orange', label='Outlier D=25%')
ax.annotate('D=25%\n(outlier)',
            xy=(25, 38.48), xytext=(33, 25),
            fontsize=10, color='darkorange',
            arrowprops=dict(arrowstyle='->', color='darkorange', lw=1.2))
ax.set_xlabel('Duty Cycle (%)')
ax.set_ylabel('Tegangan RMS (V)')
ax.set_xlim(20, 100)
ax.set_ylim(0, 230)
ax.xaxis.set_major_locator(ticker.MultipleLocator(10))
ax.yaxis.set_major_locator(ticker.MultipleLocator(20))
ax.legend(fontsize=10)

plt.tight_layout()
path1 = os.path.join(OUT_DIR, 'grafik_lampu_duty_tegangan.png')
plt.savefig(path1, dpi=200, bbox_inches='tight')
plt.close('all')
print(f'[1] Tersimpan: {path1}')


# ─────────────────────────────────────────────────────────────────────────────
# GRAFIK 2 — Beban Pompa Air: Duty Cycle vs Tegangan
# ─────────────────────────────────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(8, 5))

ax.plot(duty_pompa, v_teori_pompa, 'b--o', label='$V_{teoritis}$ = D × 220 V',
        markersize=6, linewidth=1.5)
ax.plot(duty_pompa, v_out_pompa,   'r-s',  label='$V_{out}$ RMS Terukur',
        markersize=6, linewidth=1.5)
ax.set_xlabel('Duty Cycle (%)')
ax.set_ylabel('Tegangan RMS (V)')
ax.set_xlim(67, 98)
ax.set_ylim(145, 220)
ax.xaxis.set_major_locator(ticker.MultipleLocator(5))
ax.yaxis.set_major_locator(ticker.MultipleLocator(10))
ax.legend(fontsize=10)

plt.tight_layout()
path2 = os.path.join(OUT_DIR, 'grafik_pompa_duty_tegangan.png')
plt.savefig(path2, dpi=200, bbox_inches='tight')
plt.close('all')
print(f'[2] Tersimpan: {path2}')


# ─────────────────────────────────────────────────────────────────────────────
# GRAFIK 3 — Sensor Tekanan: Tekanan (bar) vs Nilai Bit ADC
# ─────────────────────────────────────────────────────────────────────────────
coeffs = np.polyfit(tekanan, adc_bit, 1)
p      = np.poly1d(coeffs)
tekanan_fit = np.linspace(min(tekanan)-0.05, max(tekanan)+0.08, 100)
r2 = 1 - np.sum((np.array(adc_bit) - p(tekanan))**2) / \
         np.sum((np.array(adc_bit) - np.mean(adc_bit))**2)

fig, ax = plt.subplots(figsize=(8, 5))

ax.plot(tekanan, adc_bit, 'ro', markersize=8, label='Data pengukuran', zorder=5)
ax.plot(tekanan_fit, p(tekanan_fit), 'b--', linewidth=1.5,
        label=f'Regresi linear\ny = {coeffs[0]:.1f}x + {coeffs[1]:.1f}\n$R^2$ = {r2:.4f}')
for t, b in zip(tekanan, adc_bit):
    ax.annotate(f'{b}', xy=(t, b), xytext=(t+0.01, b+3),
                fontsize=10, color='darkred', fontweight='bold')
ax.set_xlabel('Tekanan (bar)')
ax.set_ylabel('Nilai Bit ADC (0–4095)')
ax.legend(fontsize=10)

plt.tight_layout()
path3 = os.path.join(OUT_DIR, 'grafik_sensor_tekanan_adc.png')
plt.savefig(path3, dpi=200, bbox_inches='tight')
plt.close('all')
print(f'[3] Tersimpan: {path3}')

print('\n=== SELESAI ===')
print(f'Semua grafik disimpan di: {OUT_DIR}')
print(f'  1. {os.path.basename(path1)}')
print(f'  2. {os.path.basename(path2)}')
print(f'  3. {os.path.basename(path3)}')
