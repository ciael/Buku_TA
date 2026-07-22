"""
generate_gambar_nn_evaluasi.py
Menghasilkan ulang dua gambar evaluasi model MLP 3-4-1 untuk Bab 4:
  - Gambar 4.20: Kurva rugi (loss) pelatihan dan validasi
  - Gambar 4.21: Perbandingan target dan prediksi Delta duty pada data uji

Pipeline (data loading, feature engineering, split, model resmi L-BFGS,
serta model ilustratif Adam untuk kurva loss per-epoch) direplikasi persis
dari notebook master:
  DATA TRAINING 14 JUNI/training_mlp_3input_closedloop.ipynb
  (cell 5, 7, 9, 15, 17, 21, dan panel kiri cell 23)

Output: loss_curve_mlp341.png dan target_vs_prediksi_mlp341.png,
disimpan di folder yang sama dengan script ini (DATA UJI).
"""
import os
import glob
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.neural_network import MLPRegressor
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import warnings
warnings.filterwarnings('ignore')

HERE     = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(os.path.dirname(HERE), 'DATA TRAINING 14 JUNI')

# ── 1. Konfigurasi (identik dengan notebook master, cell 5) ────────────────
INCLUDE_F1   = True
HIDDEN       = (4,)
RANDOM_STATE = 42
TEST_SIZE    = 0.20
VAL_FRACTION = 0.125
FEATURES     = ['error', 'd_error', 'duty_percent']
TARGET       = 'delta_duty'

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
    'grid.alpha': 0.4,
})

# ── 2. Load & gabung semua CSV (cell 7) ─────────────────────────────────────
KEY = ['pressure_bar', 'duty_percent', 'setpoint_bar', 'episode_id', 'is_decision']
files = sorted(glob.glob(os.path.join(DATA_DIR, '14juni*.csv')))
print(f'Ditemukan {len(files)} file CSV di {DATA_DIR}')

parts, gid = [], 0
for f in files:
    d = pd.read_csv(f)
    for c in KEY:
        d[c] = pd.to_numeric(d[c], errors='coerce')
    d['valve_open_count'] = pd.to_numeric(d['valve_open_count'], errors='coerce')
    d = d.dropna(subset=KEY)
    for ep in sorted(d['episode_id'].unique()):
        gid += 1
        sub = d[d['episode_id'] == ep].copy()
        sub['global_episode'] = gid
        parts.append(sub)

df = pd.concat(parts, ignore_index=True)
print(f'Total episode global: {gid} | total baris: {len(df)}')

# ── 3. Feature engineering (cell 9) ─────────────────────────────────────────
dec = df[df['is_decision'] == 1].copy().reset_index(drop=True)
dec['error']      = dec['setpoint_bar'] - dec['pressure_bar']
dec['d_error']    = dec.groupby('global_episode')['error'].diff().fillna(0.0)
dec['delta_duty'] = dec.groupby('global_episode')['duty_percent'].diff().shift(-1)

data = dec.dropna(subset=['delta_duty']).reset_index(drop=True)
if not INCLUDE_F1:
    data = data[np.isclose(data['setpoint_bar'], 0.30)].reset_index(drop=True)
print(f'Baris siap latih: {len(data)} (INCLUDE_F1={INCLUDE_F1})')

# ── 4. Split Train/Val/Test 70:10:20 (cell 15) ──────────────────────────────
X = data[FEATURES].to_numpy(np.float32)
y = data[TARGET].to_numpy(np.float32)

idx = np.arange(len(data))
trainval_idx, test_idx = train_test_split(idx, test_size=TEST_SIZE,
                                           random_state=RANDOM_STATE, shuffle=True)
train_idx, val_idx = train_test_split(trainval_idx, test_size=VAL_FRACTION,
                                       random_state=RANDOM_STATE, shuffle=True)
X_train, X_val, X_test = X[train_idx], X[val_idx], X[test_idx]
y_train, y_val, y_test = y[train_idx], y[val_idx], y[test_idx]
print(f'Train {len(train_idx)} | Val {len(val_idx)} | Test {len(test_idx)}')

# ── 5. Model resmi: MLP 3-4-1, tanh, L-BFGS (cell 17) ───────────────────────
model = Pipeline([
    ('scaler', StandardScaler()),
    ('mlp', MLPRegressor(
        hidden_layer_sizes=HIDDEN,
        activation='tanh',
        solver='lbfgs',
        alpha=1e-3,
        max_iter=5000,
        random_state=RANDOM_STATE,
        tol=1e-7,
    )),
])
model.fit(X_train, y_train)
pred_te = model.predict(X_test)

rmse = np.sqrt(mean_squared_error(y_test, pred_te))
mae  = mean_absolute_error(y_test, pred_te)
r2   = r2_score(y_test, pred_te)
print(f'Model resmi (L-BFGS)  -> R2={r2:.3f}  MAE={mae:.3f}  RMSE={rmse:.3f}')

# ── 6. Model ilustratif Adam untuk kurva loss per-epoch (cell 21) ──────────
# L-BFGS tidak menyimpan loss per-epoch, sehingga dilatih model setara
# memakai Adam + partial_fit khusus untuk menggambarkan proses belajar.
scaler = StandardScaler().fit(X_train)
Xtr, Xva = scaler.transform(X_train), scaler.transform(X_val)

mlp_adam = MLPRegressor(hidden_layer_sizes=HIDDEN, activation='tanh', solver='adam',
                         alpha=1e-3, learning_rate_init=0.02, max_iter=1,
                         warm_start=True, random_state=RANDOM_STATE,
                         batch_size=min(32, len(Xtr)), tol=1e-9, n_iter_no_change=10**9)

tr_hist, va_hist = [], []
best, best_ep, patience, bad = np.inf, 0, 250, 0
for ep in range(1, 3001):
    mlp_adam.partial_fit(Xtr, y_train)
    tl = mean_squared_error(y_train, mlp_adam.predict(Xtr))
    vl = mean_squared_error(y_val,   mlp_adam.predict(Xva))
    tr_hist.append(tl); va_hist.append(vl)
    if vl < best - 1e-7:
        best, best_ep, bad = vl, ep, 0
    else:
        bad += 1
        if bad >= patience:
            break
print(f'Kurva loss stop di epoch {len(tr_hist)} | best val MSE {best:.4f} @ epoch {best_ep}')

# ── GAMBAR 4.20: Kurva Loss (tanpa judul) ───────────────────────────────────
fig, ax = plt.subplots(figsize=(9, 5))
ax.plot(tr_hist, color='#1f77b4', lw=1.8, label='Train Loss (MSE)')
ax.plot(va_hist, color='#d62728', lw=1.8, label='Validation Loss (MSE)')
ax.axvline(best_ep, color='green', ls='--', lw=1.3, label=f'Best Epoch = {best_ep}')
ax.plot(best_ep, best, 'o', color='green', markersize=8, zorder=5)
ax.annotate(f'Best Val Loss: {best:.4f}\nEpoch: {best_ep}',
            xy=(best_ep, best), xytext=(best_ep * 0.55, max(va_hist) * 0.55),
            fontsize=11,
            bbox=dict(boxstyle='round', fc='#d9f0d3', ec='green'),
            arrowprops=dict(arrowstyle='->', color='green'))
ax.set_xlabel('Epoch')
ax.set_ylabel('Loss (MSE $\\Delta$Duty)')
ax.legend()
plt.tight_layout()
out1 = os.path.join(HERE, 'loss_curve_mlp341.png')
plt.savefig(out1, dpi=200, bbox_inches='tight')
plt.close('all')
print('[1] Tersimpan:', out1)

# ── GAMBAR 4.21: Target vs Prediksi (tanpa judul) ───────────────────────────
fig, ax = plt.subplots(figsize=(7, 6))
ax.scatter(y_test, pred_te, alpha=0.6, s=45, color='#4c72b0',
           edgecolors='black', linewidth=0.4, label='data uji', zorder=3)
lo = min(y_test.min(), pred_te.min()) - 0.3
hi = max(y_test.max(), pred_te.max()) + 0.3
ax.plot([lo, hi], [lo, hi], 'r--', lw=1.8, label='ideal (y = x)')
ax.set_xlim(lo, hi)
ax.set_ylim(lo, hi)
ax.set_xlabel('$\\Delta$Duty Target (%)')
ax.set_ylabel('$\\Delta$Duty Prediksi (%)')
ax.legend(loc='lower right')
ax.set_aspect('equal')
plt.tight_layout()
out2 = os.path.join(HERE, 'target_vs_prediksi_mlp341.png')
plt.savefig(out2, dpi=200, bbox_inches='tight')
plt.close('all')
print('[2] Tersimpan:', out2)

print('\n=== SELESAI ===')
