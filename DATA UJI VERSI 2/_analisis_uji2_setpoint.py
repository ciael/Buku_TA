# -*- coding: utf-8 -*-
"""Analisis uji 2 (respons perubahan setpoint) -> isi tab:respons-setpoint."""
import io
import os
import numpy as np
import pandas as pd

F = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uji_NN_uji2_16juni.csv')
df = pd.read_csv(F)
df['t'] = pd.to_datetime(df['pc_timestamp'])
for c in ['pressure_bar', 'setpoint_bar', 'duty_percent', 'episode_id']:
    df[c] = pd.to_numeric(df[c], errors='coerce')
df = df.dropna(subset=['pressure_bar', 'setpoint_bar', 'episode_id'])

out = io.open('uji2_hasil.txt', 'w', encoding='utf-8')
def w(*a): s=' '.join(str(x) for x in a); print(s); out.write(s+'\n')

BAND = 0.02
for ep in sorted(df['episode_id'].unique()):
    g = df[df['episode_id'] == ep]
    # setpoint dominan pada episode ini
    sp = g['setpoint_bar'].mode().iloc[0]
    seg = g[np.isclose(g['setpoint_bar'], sp)].copy()
    if len(seg) < 3:
        continue
    seg = seg.sort_values('t')
    # mulai hitung dari saat NN aktif (nn_mode=1) agar adil (ep1 sempat NN off)
    seg['nn_mode'] = pd.to_numeric(seg['nn_mode'], errors='coerce')
    act = seg[seg['nn_mode'] == 1]
    if len(act) >= 3:
        seg = act
    t0 = seg['t'].iloc[0]
    elapsed = (seg['t'] - t0).dt.total_seconds().to_numpy()
    p = seg['pressure_bar'].to_numpy()
    p_awal = p[0]
    # stabil = rata-rata 8 detik terakhir segmen
    mask_tail = elapsed >= (elapsed[-1] - 8.0)
    p_stabil = p[mask_tail].mean()
    err = sp - p_stabil
    # settling time: waktu setelah itu p tetap di band +-0.02
    outside = np.abs(p - sp) > BAND
    if not outside.any():
        st = 0.0
    elif outside.all():
        st = None  # tak pernah masuk band
    else:
        last_out = np.where(outside)[0].max()
        st = elapsed[last_out + 1] if last_out + 1 < len(elapsed) else None
    arah = 'naik' if (sp - p_awal) > 0 else 'turun'
    w(f"Ep{int(ep)} | SP={sp:.2f} | awal={p_awal:.3f} | stabil={p_stabil:.3f} | "
      f"err={err:+.3f} | settle={'NA' if st is None else round(st,1)} s | "
      f"arah={arah} | durasi_seg={elapsed[-1]:.0f}s | n={len(seg)}")
out.close()
print('OK -> uji2_hasil.txt')
