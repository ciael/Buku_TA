# -*- coding: utf-8 -*-
# Program pelatihan MLP 3-4-1 (controller tekanan) - data closed-loop 14 Juni 2026
# Diekstrak dari notebook training_mlp_3input_closedloop.ipynb

import os, glob
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.neural_network import MLPRegressor
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score

plt.rcParams['figure.figsize'] = (12, 5)
plt.rcParams['axes.grid'] = True
np.set_printoptions(suppress=True)

DATA_DIR = r'E:\\SEMESTER 8\\TA\\BUKU TA_YOEL\\DATA TRAINING 14 JUNI'

INCLUDE_F1   = True     # ikutkan data setpoint 0.25 (f1)?
HIDDEN       = (4,)     # MLP 3-4-1
RANDOM_STATE = 42
TEST_SIZE    = 0.20
VAL_FRACTION = 0.125    # dari trainval -> ~10% total
DUTY_MIN     = 70.0
DUTY_MAX     = 95.0

FEATURES = ['error', 'd_error', 'duty_percent']
TARGET   = 'delta_duty'

KEY = ['pressure_bar', 'duty_percent', 'setpoint_bar', 'episode_id', 'is_decision']
files = sorted(glob.glob(os.path.join(DATA_DIR, '*.csv')))
print(f'Ditemukan {len(files)} file CSV')

parts, meta, gid = [], [], 0
for f in files:
    d = pd.read_csv(f)
    for c in KEY:
        d[c] = pd.to_numeric(d[c], errors='coerce')
    d['valve_open_count'] = pd.to_numeric(d['valve_open_count'], errors='coerce')
    d = d.dropna(subset=KEY)                      # buang baris korup/catatan
    for ep in sorted(d['episode_id'].unique()):
        gid += 1
        sub = d[d['episode_id'] == ep].copy()
        sub['global_episode'] = gid
        sub['src'] = os.path.basename(f)
        parts.append(sub)
        meta.append({'file': os.path.basename(f), 'ep_lokal': int(ep),
                     'global_episode': gid,
                     'baris_keputusan': int((sub['is_decision'] == 1).sum()),
                     'valve': sorted(sub['valve_open_count'].dropna().unique().tolist()),
                     'setpoint': sorted(sub['setpoint_bar'].unique().tolist())})

df = pd.concat(parts, ignore_index=True)
meta_df = pd.DataFrame(meta)
print(f'Total episode global: {gid} | total baris: {len(df)}')
meta_df

dec = df[df['is_decision'] == 1].copy().reset_index(drop=True)

dec['error']      = dec['setpoint_bar'] - dec['pressure_bar']
dec['d_error']    = dec.groupby('global_episode')['error'].diff().fillna(0.0)
dec['delta_duty'] = dec.groupby('global_episode')['duty_percent'].diff().shift(-1)

data = dec.dropna(subset=['delta_duty']).reset_index(drop=True)
if not INCLUDE_F1:
    data = data[np.isclose(data['setpoint_bar'], 0.30)].reset_index(drop=True)

print(f'Baris keputusan : {len(dec)}')
print(f'Baris siap latih: {len(data)}  (INCLUDE_F1={INCLUDE_F1})')

print('=== Distribusi target dDuty ===')
print('  naik (>0) :', int((data[TARGET] > 0).sum()))
print('  turun (<0):', int((data[TARGET] < 0).sum()))
print('  tahan (=0):', int((data[TARGET] == 0).sum()))
print('  nilai unik:', sorted(data[TARGET].unique().tolist()))
print()
print('=== Rentang fitur ===')
print(data[FEATURES].describe().loc[['min', 'mean', 'max']].T)
print()
print('=== Baris per setpoint ===')
print(data.groupby('setpoint_bar').size())

fig, ax = plt.subplots(1, 2, figsize=(13, 4))
ax[0].hist(data[TARGET], bins=np.arange(-3.5, 4.5, 1.0), edgecolor='k', alpha=0.7)
ax[0].set_title('Distribusi dDuty (target)'); ax[0].set_xlabel('dDuty (%)')
ax[1].scatter(data['error'], data[TARGET], alpha=0.4, s=15)
ax[1].set_title(f"error vs dDuty  (corr={data['error'].corr(data[TARGET]):.3f})")
ax[1].set_xlabel('error (bar)'); ax[1].set_ylabel('dDuty (%)')
plt.tight_layout(); plt.show()

X = data[FEATURES].to_numpy(np.float32)
y = data[TARGET].to_numpy(np.float32)

idx = np.arange(len(data))
trainval_idx, test_idx = train_test_split(idx, test_size=TEST_SIZE, random_state=RANDOM_STATE, shuffle=True)
train_idx, val_idx = train_test_split(trainval_idx, test_size=VAL_FRACTION, random_state=RANDOM_STATE, shuffle=True)

X_train, X_val, X_test = X[train_idx], X[val_idx], X[test_idx]
y_train, y_val, y_test = y[train_idx], y[val_idx], y[test_idx]
print(f'Train {len(train_idx)} | Val {len(val_idx)} | Test {len(test_idx)}')

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

def metrics(yt, yp):
    return {'RMSE': np.sqrt(mean_squared_error(yt, yp)),
            'MAE': mean_absolute_error(yt, yp),
            'R2': r2_score(yt, yp)}

pred_tr, pred_va, pred_te = model.predict(X_train), model.predict(X_val), model.predict(X_test)
print('=== MLP 3-4-1 ===')
print('Train:', {k: round(v, 4) for k, v in metrics(y_train, pred_tr).items()})
print('Val  :', {k: round(v, 4) for k, v in metrics(y_val,   pred_va).items()})
print('Test :', {k: round(v, 4) for k, v in metrics(y_test,  pred_te).items()})
print()
print('Catatan: gap Train vs Test kecil = tidak overfit.')

# baseline delta=0
b0 = np.zeros_like(y_test)
# baseline proporsional: cari k via least squares di train
k = np.sum(X_train[:, 0] * y_train) / np.sum(X_train[:, 0] ** 2)
bp = k * X_test[:, 0]
print(f'Gain proporsional ter-fit: k = {k:.2f} (dDuty = {k:.1f} * error)')
print()
rows = [
    {'Model': 'MLP 3-4-1',        **metrics(y_test, pred_te)},
    {'Model': 'Baseline dDuty=0', **metrics(y_test, b0)},
    {'Model': 'Baseline P (k*err)', **metrics(y_test, bp)},
]
print(pd.DataFrame(rows).round(4).to_string(index=False))

scaler = StandardScaler().fit(X_train)
Xtr, Xva = scaler.transform(X_train), scaler.transform(X_val)

mlp = MLPRegressor(hidden_layer_sizes=HIDDEN, activation='tanh', solver='adam',
                   alpha=1e-3, learning_rate_init=0.02, max_iter=1,
                   warm_start=True, random_state=RANDOM_STATE,
                   batch_size=min(32, len(Xtr)), tol=1e-9, n_iter_no_change=10**9)

tr_hist, va_hist, best, best_ep, patience, bad = [], [], np.inf, 0, 250, 0
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

plt.figure(figsize=(11, 5))
plt.plot(tr_hist, label='Train MSE')
plt.plot(va_hist, label='Val MSE')
plt.axvline(best_ep, color='g', ls='--', label=f'best epoch {best_ep}')
plt.xlabel('Epoch'); plt.ylabel('MSE (dDuty)'); plt.title('Loss Curve MLP 3-4-1')
plt.legend(); plt.tight_layout(); plt.show()

fig, ax = plt.subplots(1, 2, figsize=(14, 5))
ax[0].scatter(y_test, pred_te, alpha=0.5)
lo, hi = min(y_test.min(), pred_te.min()), max(y_test.max(), pred_te.max())
ax[0].plot([lo, hi], [lo, hi], 'r--', label='ideal y=x')
ax[0].set_xlabel('dDuty target'); ax[0].set_ylabel('dDuty prediksi')
ax[0].set_title('Target vs Prediksi (test)'); ax[0].legend()

order = np.argsort(test_idx)
ax[1].plot(y_test[order], 'o-', ms=3, label='target')
ax[1].plot(pred_te[order], 's--', ms=3, label='prediksi')
ax[1].set_xlabel('index test'); ax[1].set_ylabel('dDuty'); ax[1].legend()
ax[1].set_title('dDuty target vs prediksi')
plt.tight_layout(); plt.show()

ep_pick = data.groupby('global_episode').size().idxmax()
epd = data[data['global_episode'] == ep_pick].reset_index(drop=True)

duty_sim = [epd['duty_percent'].iloc[0]]
for i in range(len(epd)):
    err = epd['setpoint_bar'].iloc[i] - epd['pressure_bar'].iloc[i]
    derr = epd['d_error'].iloc[i]
    x = np.array([[err, derr, duty_sim[-1]]], np.float32)
    dd = float(model.predict(x)[0])
    duty_sim.append(float(np.clip(duty_sim[-1] + dd, DUTY_MIN, DUTY_MAX)))
duty_sim = duty_sim[:-1]

fig, ax1 = plt.subplots(figsize=(12, 5))
ax1.plot(epd['pressure_bar'].values, 'b-o', ms=3, label='pressure aktual')
ax1.axhline(epd['setpoint_bar'].iloc[0], color='g', ls='--', label='setpoint')
ax1.set_ylabel('pressure (bar)', color='b'); ax1.legend(loc='upper left')
ax2 = ax1.twinx()
ax2.plot(epd['duty_percent'].values, 'k-', alpha=0.5, label='duty rekaman (manusia)')
ax2.plot(duty_sim, 'r--', label='duty simulasi MLP')
ax2.set_ylabel('duty (%)', color='r'); ax2.legend(loc='upper right')
plt.title(f'Simulasi controller MLP vs rekaman manusia (episode {ep_pick})')
plt.tight_layout(); plt.show()

scaler_f = model.named_steps['scaler']
mlp_f    = model.named_steps['mlp']
mean_, scale_ = scaler_f.mean_, scaler_f.scale_
W1, b1 = mlp_f.coefs_[0], mlp_f.intercepts_[0]   # (3,4), (4,)
W2, b2 = mlp_f.coefs_[1], mlp_f.intercepts_[1]   # (4,1), (1,)

def carr(a, name, fmt='%.8ff'):
    a = np.atleast_2d(a)
    if a.shape[0] == 1:
        body = ', '.join(fmt % v for v in a.ravel())
        return f'static const float {name}[{a.shape[1]}] = {{ {body} }};'
    rows = ',\n    '.join('{ ' + ', '.join(fmt % v for v in r) + ' }' for r in a)
    return f'static const float {name}[{a.shape[0]}][{a.shape[1]}] = {{\n    {rows}\n}};'

print('/* === MLP 3-4-1 (input: error, d_error, duty) === */')
print(carr(mean_,  'scaler_mean'))
print(carr(scale_, 'scaler_scale'))
print(carr(W1, 'W1'))
print(carr(b1, 'B1'))
print(carr(W2.T, 'W2'))
print(carr(b2, 'B2'))
print('''
/* Forward (C):
float in[3] = { error, d_error, duty };
for (i=0;i<3;i++) in[i] = (in[i]-scaler_mean[i])/scaler_scale[i];
for (j=0;j<4;j++){ float s=B1[j]; for(i=0;i<3;i++) s+=in[i]*W1[i][j]; h[j]=tanhf(s); }
float dd=B2[0]; for(j=0;j<4;j++) dd+=h[j]*W2[j];
duty = clampf(duty + dd, 70.0f, 95.0f);
*/''')

