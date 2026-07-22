# -*- coding: utf-8 -*-
"""
Loss curve (Train vs Validation) untuk model MLP 3-4-1 (data 14 Juni, 3 input).
Konsisten dengan training_mlp_3input_closedloop.ipynb.

lbfgs tidak menyimpan loss per-epoch, jadi kurva digambar dengan melatih model
yang setara memakai adam + partial_fit (persis seperti sel "Kurva Loss" di notebook).
Test TIDAK digambar sebagai kurva karena test hanya dievaluasi sekali di akhir
(satu angka), bukan per-epoch.

Output: loss_curve_mlp341.png (disimpan di folder ini).
"""
import os, glob
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.neural_network import MLPRegressor
from sklearn.metrics import mean_squared_error
import warnings
warnings.filterwarnings('ignore')

HERE = os.path.dirname(os.path.abspath(__file__))
RANDOM_STATE = 42
HIDDEN = (4,)

# ----- 1. Muat & rekayasa fitur (sama dengan notebook) -----
KEY = ['pressure_bar', 'duty_percent', 'setpoint_bar', 'episode_id', 'is_decision']
parts, gid = [], 0
for f in sorted(glob.glob(os.path.join(HERE, '*.csv'))):
    d = pd.read_csv(f)
    for c in KEY:
        d[c] = pd.to_numeric(d[c], errors='coerce')
    d = d.dropna(subset=KEY)
    for ep in sorted(d['episode_id'].unique()):
        gid += 1
        sub = d[d['episode_id'] == ep].copy()
        sub['global_episode'] = gid
        parts.append(sub)
df = pd.concat(parts, ignore_index=True)

dec = df[df['is_decision'] == 1].copy().reset_index(drop=True)
dec['error']      = dec['setpoint_bar'] - dec['pressure_bar']
dec['d_error']    = dec.groupby('global_episode')['error'].diff().fillna(0.0)
dec['delta_duty'] = dec.groupby('global_episode')['duty_percent'].diff().shift(-1)
data = dec.dropna(subset=['delta_duty']).reset_index(drop=True)

X = data[['error', 'd_error', 'duty_percent']].to_numpy(np.float32)
y = data['delta_duty'].to_numpy(np.float32)

# ----- 2. Split train/val/test (seed sama dengan notebook) -----
idx = np.arange(len(data))
trainval_idx, test_idx = train_test_split(idx, test_size=0.20, random_state=RANDOM_STATE, shuffle=True)
train_idx, val_idx = train_test_split(trainval_idx, test_size=0.125, random_state=RANDOM_STATE, shuffle=True)
X_train, X_val = X[train_idx], X[val_idx]
y_train, y_val = y[train_idx], y[val_idx]

scaler = StandardScaler().fit(X_train)
Xtr, Xva = scaler.transform(X_train), scaler.transform(X_val)

# ----- 3. Latih bertahap (adam + partial_fit) untuk merekam loss per-epoch -----
mlp = MLPRegressor(hidden_layer_sizes=HIDDEN, activation='tanh', solver='adam',
                   alpha=1e-3, learning_rate_init=0.02, max_iter=1,
                   warm_start=True, random_state=RANDOM_STATE,
                   batch_size=min(32, len(Xtr)), tol=1e-9, n_iter_no_change=10**9)

tr_hist, va_hist = [], []
best, best_ep, patience, bad = np.inf, 0, 250, 0
for ep in range(1, 3001):
    mlp.partial_fit(Xtr, y_train)
    tl = mean_squared_error(y_train, mlp.predict(Xtr))
    vl = mean_squared_error(y_val,   mlp.predict(Xva))
    tr_hist.append(tl); va_hist.append(vl)
    if vl < best - 1e-7:
        best, best_ep, bad = vl, ep, 0
    else:
        bad += 1
        if bad >= patience:
            break

print(f'Stop di epoch {len(tr_hist)} | best val MSE {best:.4f} @ epoch {best_ep}')

# ----- 4. Gambar & simpan -----
plt.figure(figsize=(11, 5))
plt.plot(tr_hist, color='#1f77b4', lw=1.8, label='Train Loss (MSE)')
plt.plot(va_hist, color='#d62728', lw=1.8, label='Validation Loss (MSE)')
plt.axvline(best_ep, color='green', ls='--', label=f'Best Epoch = {best_ep}')
plt.scatter([best_ep], [best], color='green', zorder=5)
plt.annotate(f'Best Val Loss: {best:.4f}\nEpoch: {best_ep}',
             xy=(best_ep, best), xytext=(best_ep*0.55, max(va_hist)*0.35),
             bbox=dict(boxstyle='round', fc='#d9f0d3', ec='green'),
             arrowprops=dict(arrowstyle='->', color='green'), fontsize=10)
plt.xlabel('Epoch', fontsize=12)
plt.ylabel('Loss (MSE ΔDuty)', fontsize=12)
plt.title('Training & Validation Loss Curve\nMLP 3-4-1 | Data 14 Juni | 3 fitur input', fontsize=12)
plt.legend(); plt.grid(alpha=0.35); plt.tight_layout()
out = os.path.join(HERE, 'loss_curve_mlp341.png')
plt.savefig(out, dpi=160)
print('saved:', out)
