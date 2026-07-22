"""Builder notebook EKSPLORASI: perbandingan fungsi aktivasi + hyperparameter tuning.
Bukan untuk skripsi (deadline pakai MLP 3-input). Jalankan: python _build_compare.py
"""
import json, os

cells = []
def md(s):  cells.append(("markdown", s))
def code(s): cells.append(("code", s))

md("""# Eksplorasi: Perbandingan Fungsi Aktivasi & Hyperparameter Tuning

> **Catatan:** notebook ini **eksplorasi** untuk menjawab rasa penasaran dosen
> (perbandingan apple-to-apple). **Tidak dipakai di skripsi** — hasil resmi tetap
> MLP 3-4-1 (tanh) pada `training_mlp_3input_closedloop.ipynb`.

Tujuan:
1. Bandingkan **fungsi aktivasi**: tanh, ReLU, logistic, dan **identity (linear)**.
2. Bandingkan terhadap **Regresi Linear** murni (apakah NN non-linear perlu?).
3. **Hyperparameter tuning** dengan **Grid Search** (apple-to-apple: tiap model di setelan terbaiknya).""")

code("""import os, glob
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.neural_network import MLPRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score

DATA_DIR = r'E:\\\\SEMESTER 8\\\\TA\\\\BUKU TA_YOEL\\\\DATA TRAINING 14 JUNI'
RS = 42""")

md("## 1. Load & gabung data + feature engineering (ΔDuty per-episode)")

code("""KEY = ['pressure_bar','duty_percent','setpoint_bar','episode_id','is_decision']
files = sorted(glob.glob(os.path.join(DATA_DIR, '*.csv')))
parts, gid = [], 0
for f in files:
    d = pd.read_csv(f)
    for c in KEY: d[c] = pd.to_numeric(d[c], errors='coerce')
    d = d.dropna(subset=KEY)
    for ep in sorted(d['episode_id'].unique()):
        gid += 1
        s = d[d['episode_id']==ep].copy(); s['ge']=gid; parts.append(s)
df = pd.concat(parts, ignore_index=True)
dec = df[df['is_decision']==1].copy().reset_index(drop=True)
dec['error']   = dec['setpoint_bar'] - dec['pressure_bar']
dec['d_error'] = dec.groupby('ge')['error'].diff().fillna(0.0)
dec['delta_duty'] = dec.groupby('ge')['duty_percent'].diff().shift(-1)
data = dec.dropna(subset=['delta_duty']).reset_index(drop=True)

X = data[['error','d_error','duty_percent']].to_numpy(np.float32)
y = data['delta_duty'].to_numpy(np.float32)
Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.20, random_state=RS, shuffle=True)
print(f'Total {len(data)} baris | Train {len(Xtr)} | Test {len(Xte)}')

def metr(yt, yp):
    return dict(RMSE=np.sqrt(mean_squared_error(yt,yp)),
               MAE=mean_absolute_error(yt,yp), R2=r2_score(yt,yp))""")

md("""## 2. Perbandingan Fungsi Aktivasi (arsitektur sama: 4 neuron hidden)

Catatan penting: **`identity` = aktivasi linear**. Bila hidden memakai identity, MLP
runtuh menjadi model linear. Ini pembanding langsung "tanh vs linear".""")

code("""rows = []
for act in ['tanh', 'relu', 'logistic', 'identity']:
    m = Pipeline([('s', StandardScaler()),
                  ('mlp', MLPRegressor(hidden_layer_sizes=(4,), activation=act,
                                       solver='lbfgs', alpha=1e-3, max_iter=5000,
                                       random_state=RS))])
    m.fit(Xtr, ytr)
    r = metr(yte, m.predict(Xte))
    rows.append({'Model': f'MLP 3-4-1 ({act})', **r})

# Regresi Linear murni (tanpa hidden)
lin = Pipeline([('s', StandardScaler()), ('lr', LinearRegression())])
lin.fit(Xtr, ytr)
rows.append({'Model': 'Regresi Linear', **metr(yte, lin.predict(Xte))})

# Baseline diam
rows.append({'Model': 'Baseline ΔDuty=0', **metr(yte, np.zeros_like(yte))})

comp = pd.DataFrame(rows).round(4).sort_values('R2', ascending=False)
print(comp.to_string(index=False))""")

md("""## 3. Hyperparameter Tuning dengan Grid Search (apple-to-apple)

Mencari kombinasi terbaik dari jumlah neuron, fungsi aktivasi, dan regularisasi
`alpha` menggunakan validasi silang (cross-validation).""")

code("""pipe = Pipeline([('s', StandardScaler()),
                 ('mlp', MLPRegressor(solver='lbfgs', max_iter=5000, random_state=RS))])
grid = {
    'mlp__hidden_layer_sizes': [(2,), (4,), (8,), (4, 4)],
    'mlp__activation': ['tanh', 'relu', 'logistic'],
    'mlp__alpha': [1e-2, 1e-3, 1e-4],
}
gs = GridSearchCV(pipe, grid, scoring='r2', cv=5, n_jobs=-1)
gs.fit(Xtr, ytr)
print('Kombinasi terbaik:')
for k, v in gs.best_params_.items():
    print(f'  {k} = {v}')
print(f'\\nR2 cross-val terbaik: {gs.best_score_:.4f}')
print('R2 di data uji      :', round(r2_score(yte, gs.predict(Xte)), 4))""")

code("""# 5 kombinasi teratas dari grid search
res = pd.DataFrame(gs.cv_results_)
top = res.sort_values('rank_test_score').head(5)[
    ['param_mlp__hidden_layer_sizes','param_mlp__activation','param_mlp__alpha','mean_test_score']]
top.columns = ['hidden', 'aktivasi', 'alpha', 'R2_cv']
print(top.round(4).to_string(index=False))""")

md("""## 4. Kesimpulan eksplorasi

- **tanh vs linear/identity**: lihat Sel 2 — bila tanh unggul jelas atas identity &
  regresi linear, berarti non-linearitas memang diperlukan (justifikasi memakai NN).
- **Hyperparameter tuning (grid search)**: Sel 3 menunjukkan setelan terbaik secara
  apple-to-apple. Jika setelan terbaik mendekati 3-4-1 tanh, maka pilihan desain Anda
  sudah baik; jika berbeda, ini bahan diskusi (tetapi untuk embedded, model kecil tetap
  dipilih demi keterbatasan STM32).
- Hasil ini **untuk diskusi dengan dosen**, bukan untuk dimasukkan ke skripsi
  (deadline tetap memakai MLP 3-4-1 tanh).""")

nb = {
 "cells": [({"cell_type":"markdown","metadata":{},"source":s.splitlines(keepends=True)} if t=="markdown"
            else {"cell_type":"code","metadata":{},"execution_count":None,"outputs":[],"source":s.splitlines(keepends=True)})
           for (t,s) in cells],
 "metadata": {"kernelspec":{"display_name":"Python 3","language":"python","name":"python3"},
              "language_info":{"name":"python","version":"3.12"}},
 "nbformat":4, "nbformat_minor":5,
}
out = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'eksplorasi_perbandingan_aktivasi.ipynb')
with open(out,'w',encoding='utf-8') as fh: json.dump(nb, fh, ensure_ascii=False, indent=1)
print('Notebook:', out)
