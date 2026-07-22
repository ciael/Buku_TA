# -*- coding: utf-8 -*-
"""
Perbandingan arsitektur MLP untuk membenarkan pemilihan 3-4-1.
Membandingkan beberapa ukuran jaringan pada DATA yang sama:
  - akurasi jujur (5-fold cross-validation, R2 mean +/- std)
  - akurasi di data uji tersendiri (R2 test) -> menunjukkan overfitting saat jaringan membesar
  - jumlah parameter (beban komputasi STM32)
Hanya arsitektur yang divariasikan; hyperparam lain disamakan (tanh, lbfgs, alpha=1e-3).

Output (folder ini):
  - banding_arsitektur.png
  - banding_arsitektur.csv
"""
import os, glob, numpy as np, pandas as pd
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split, KFold, cross_val_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.neural_network import MLPRegressor
from sklearn.metrics import r2_score
import warnings; warnings.filterwarnings('ignore')

HERE = os.path.dirname(os.path.abspath(__file__))
RS = 42

# ---- data (sama dengan notebook) ----
KEY = ['pressure_bar','duty_percent','setpoint_bar','episode_id','is_decision']
parts, gid = [], 0
for f in sorted(glob.glob(os.path.join(HERE,'*.csv'))):
    d = pd.read_csv(f)
    for c in KEY: d[c] = pd.to_numeric(d[c], errors='coerce')
    d = d.dropna(subset=KEY)
    for ep in sorted(d['episode_id'].unique()):
        gid += 1; sub = d[d['episode_id']==ep].copy(); sub['global_episode']=gid; parts.append(sub)
df = pd.concat(parts, ignore_index=True)
dec = df[df['is_decision']==1].copy().reset_index(drop=True)
dec['error']=dec['setpoint_bar']-dec['pressure_bar']
dec['d_error']=dec.groupby('global_episode')['error'].diff().fillna(0.0)
dec['delta_duty']=dec.groupby('global_episode')['duty_percent'].diff().shift(-1)
data=dec.dropna(subset=['delta_duty']).reset_index(drop=True)
X=data[['error','d_error','duty_percent']].to_numpy(np.float32)
y=data['delta_duty'].to_numpy(np.float32)
Xtr,Xte,ytr,yte = train_test_split(X,y,test_size=0.20,random_state=RS,shuffle=True)
cv = KFold(n_splits=5, shuffle=True, random_state=RS)

def nparam(hidden):
    dims=[3]+list(hidden)+[1]; s=0
    for a,b in zip(dims[:-1],dims[1:]): s += a*b + b
    return s

def pipe(hidden):
    return Pipeline([('s',StandardScaler()),
        ('mlp',MLPRegressor(hidden_layer_sizes=hidden,activation='tanh',solver='lbfgs',
                            alpha=1e-3,max_iter=5000,random_state=RS,tol=1e-7))])

archs = [('3-2-1',(2,)),('3-3-1',(3,)),('3-4-1',(4,)),('3-6-1',(6,)),
         ('3-8-1',(8,)),('3-4-4-1',(4,4))]
rows=[]
for name,h in archs:
    r2cv = cross_val_score(pipe(h),X,y,cv=cv,scoring='r2')
    m = pipe(h).fit(Xtr,ytr); r2te = r2_score(yte,m.predict(Xte))
    rows.append({'arsitektur':name,'param':nparam(h),
                 'R2_CV':r2cv.mean(),'R2_CV_std':r2cv.std(),'R2_test':r2te})
res=pd.DataFrame(rows)
res.to_csv(os.path.join(HERE,'banding_arsitektur.csv'),index=False)
print(res.round(4).to_string(index=False))

# ---- PLOT ----
fig, ax = plt.subplots(figsize=(11,6))
xpos=np.arange(len(res)); w=0.38
c_chosen='#d62728'
barcol=['#4c72b0']*len(res)
sel=list(res['arsitektur']).index('3-4-1'); barcol[sel]=c_chosen

b1=ax.bar(xpos-w/2, res['R2_CV'], w, yerr=res['R2_CV_std'], capsize=4,
          color=barcol, edgecolor='k', label='R² Cross-Validation (jujur)')
b2=ax.bar(xpos+w/2, res['R2_test'], w, color='#bbbbbb', edgecolor='k',
          label='R² Data Uji (1 split)')
for x,v in zip(xpos,res['R2_CV']): ax.text(x-w/2, v+res['R2_CV_std'][x]+0.004, f'{v:.3f}', ha='center', fontsize=8)
for x,v in zip(xpos,res['R2_test']): ax.text(x+w/2, v+0.004, f'{v:.3f}', ha='center', fontsize=8)

ax.set_xticks(xpos)
ax.set_xticklabels([f'{a}\n({p} par.)' for a,p in zip(res['arsitektur'],res['param'])])
ax.set_ylabel('Koefisien determinasi R²')
ax.set_ylim(0.80, 0.96)
ax.set_title('Perbandingan Arsitektur MLP pada Data yang Sama\n(hanya ukuran jaringan divariasikan; tanh, L-BFGS, alpha=1e-3)')
ax.axvline(sel, color=c_chosen, ls=':', lw=1, alpha=0.5)
ax.annotate('Pilihan skripsi', xy=(sel-w/2, res['R2_CV'][sel]),
            xytext=(sel-1.2, 0.935), fontsize=10, color=c_chosen, fontweight='bold',
            arrowprops=dict(arrowstyle='->', color=c_chosen))
ax.legend(loc='lower right'); ax.grid(axis='y', alpha=0.3)
plt.tight_layout(); plt.savefig(os.path.join(HERE,'banding_arsitektur.png'), dpi=160)
print('saved: banding_arsitektur.png')
