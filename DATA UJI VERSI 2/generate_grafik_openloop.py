"""
generate_grafik_openloop.py
Membuat grafik tekanan open-loop per kondisi keran vs duty cycle
dari data training 14 Juni.
"""

import matplotlib
matplotlib.use('Agg')
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import os

OUT_DIR = r'E:\SEMESTER 8\TA\BUKU TA_YOEL\DATA UJI'

plt.rcParams.update({
    'font.family': 'Times New Roman',
    'font.size': 13,
    'axes.labelsize': 15,
    'axes.labelweight': 'bold',
    'xtick.labelsize': 13,
    'ytick.labelsize': 13,
    'legend.fontsize': 12,
    'axes.grid': True,
    'grid.linestyle': '--',
    'grid.alpha': 0.5,
})

files = [
    r'E:\SEMESTER 8\TA\BUKU TA_YOEL\DATA TRAINING 14 JUNI\14junie1.csv',
    r'E:\SEMESTER 8\TA\BUKU TA_YOEL\DATA TRAINING 14 JUNI\14junic1.csv',
    r'E:\SEMESTER 8\TA\BUKU TA_YOEL\DATA TRAINING 14 JUNI\14junic2.csv',
    r'E:\SEMESTER 8\TA\BUKU TA_YOEL\DATA TRAINING 14 JUNI\14junid1.csv',
    r'E:\SEMESTER 8\TA\BUKU TA_YOEL\DATA TRAINING 14 JUNI\14junid2.csv',
]

df = pd.concat([pd.read_csv(f) for f in files], ignore_index=True)
for c in ['pressure_bar', 'duty_percent', 'valve_open_count', 'nn_mode']:
    df[c] = pd.to_numeric(df[c], errors='coerce')

# Hanya data open-loop fase stabil
stable = df[(df['valve_phase'] == 'stable') & (df['nn_mode'] == 0)].copy()
stable['duty_bin'] = (stable['duty_percent'] / 5).round() * 5

grp = stable.groupby(['valve_open_count', 'duty_bin'])['pressure_bar'] \
            .agg(['mean', 'std', 'count']).reset_index()
grp = grp[grp['count'] >= 5]
# Mulai dari duty 75% -- di bawah itu belum semua kondisi keran (0-4) punya data
grp = grp[grp['duty_bin'] >= 75]

# ── Grafik ──────────────────────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(9, 6))

styles = {
    0: dict(color='black',     marker='s', ls='-',  label='0 keran (semua tutup)'),
    1: dict(color='steelblue', marker='o', ls='-',  label='1 keran terbuka'),
    2: dict(color='seagreen',  marker='^', ls='-',  label='2 keran terbuka'),
    3: dict(color='darkorange',marker='D', ls='-',  label='3 keran terbuka'),
    4: dict(color='crimson',   marker='v', ls='-',  label='4 keran terbuka'),
}

for keran in sorted(grp['valve_open_count'].unique()):
    sub = grp[grp['valve_open_count'] == keran].sort_values('duty_bin')
    s = styles[int(keran)]
    ax.errorbar(sub['duty_bin'], sub['mean'],
                yerr=sub['std'],
                color=s['color'], marker=s['marker'],
                linestyle=s['ls'], linewidth=1.6, markersize=6,
                capsize=4, elinewidth=1.0, label=s['label'])

# Garis setpoint 0.30 bar
ax.axhline(0.30, color='red', ls='--', lw=1.5, label='Setpoint 0,30 bar')

ax.set_xlabel('Duty Cycle (%)')
ax.set_ylabel('Tekanan (bar)')
ax.set_xlim(73, 97)
ax.set_ylim(0.05, 0.80)
ax.xaxis.set_major_locator(ticker.MultipleLocator(5))
ax.yaxis.set_major_locator(ticker.MultipleLocator(0.05))
ax.legend(fontsize=9, loc='upper left')

plt.tight_layout()
path = os.path.join(OUT_DIR, 'grafik_openloop_keran_duty.png')
plt.savefig(path, dpi=200, bbox_inches='tight')
plt.close('all')
print(f'Tersimpan: {path}')
