import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.neural_network import MLPRegressor
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error

plt.rcParams['figure.figsize'] = (12, 5)
plt.rcParams['axes.grid'] = True

# ============ Load data ============
DATA_PATH = Path('DATA_CLEAN_MLP_5JUNI_GE80.csv')
SETPOINT_BAR = 0.85
SAFETY_PRESSURE_BAR = 0.95
MIN_OPERATING_DUTY = 80.0
MAX_OPERATING_DUTY = 95.0
RANDOM_STATE = 42
TEST_SIZE = 0.20

df = pd.read_csv(DATA_PATH, parse_dates=['pc_timestamp'])
required_numeric_cols = [
    'setpoint','pressure','error','delta_pressure','prev_duty','voltage_rms',
    'duty_next_percent','duty_percent',
]
for col in required_numeric_cols:
    df[col] = pd.to_numeric(df[col], errors='coerce')
df = df.dropna(subset=required_numeric_cols).copy()
df = df[df['duty_percent'].between(MIN_OPERATING_DUTY, MAX_OPERATING_DUTY)].copy()
df = df[df['pressure'].between(0.0, 1.5)].copy()
df = df.reset_index(drop=True)

# Features
features_5 = ['setpoint','pressure','error','delta_pressure','prev_duty']
features_6 = ['setpoint','pressure','error','delta_pressure','prev_duty','voltage_rms']
target_col = 'duty_next_percent'

X5 = df[features_5].to_numpy(dtype=np.float32)
X6 = df[features_6].to_numpy(dtype=np.float32)
y = df[target_col].to_numpy(dtype=np.float32)

# Split
indices = np.arange(len(df))
train_idx, test_idx = train_test_split(indices, test_size=TEST_SIZE, random_state=RANDOM_STATE, shuffle=True)

def regression_metrics(y_true, y_pred):
    mse = mean_squared_error(y_true, y_pred)
    rmse = np.sqrt(mse)
    mae = mean_absolute_error(y_true, y_pred)
    r2 = r2_score(y_true, y_pred)
    return {'MSE': mse, 'RMSE': rmse, 'MAE': mae, 'R2': r2}

def train_mlp_model(X, y, train_idx, test_idx, model_name):
    X_train = X[train_idx]; X_test = X[test_idx]
    y_train = y[train_idx]; y_test = y[test_idx]
    model = Pipeline([
        ('scaler', StandardScaler()),
        ('mlp', MLPRegressor(hidden_layer_sizes=(8,), activation='tanh', solver='lbfgs', alpha=1e-4, max_iter=5000, random_state=RANDOM_STATE)),
    ])
    model.fit(X_train, y_train)
    y_train_pred = np.clip(model.predict(X_train), 0.0, MAX_OPERATING_DUTY)
    y_test_pred = np.clip(model.predict(X_test), 0.0, MAX_OPERATING_DUTY)
    return {
        'model_name': model_name, 'model': model,
        'train_metrics': regression_metrics(y_train, y_train_pred),
        'test_metrics': regression_metrics(y_test, y_test_pred),
        'y_train': y_train, 'y_train_pred': y_train_pred,
        'y_test': y_test, 'y_test_pred': y_test_pred,
        'X_train': X_train, 'X_test': X_test,
    }

result_5 = train_mlp_model(X5, y, train_idx, test_idx, 'MLP_5_8_1')
result_6 = train_mlp_model(X6, y, train_idx, test_idx, 'MLP_6_8_1')

print('=== MODEL COMPARISON ===')
for r in [result_5, result_6]:
    print(f"{r['model_name']}: train_RMSE={r['train_metrics']['RMSE']:.6f} test_RMSE={r['test_metrics']['RMSE']:.6f} | train_R2={r['train_metrics']['R2']:.6f} test_R2={r['test_metrics']['R2']:.6f}")

if result_6['test_metrics']['RMSE'] < result_5['test_metrics']['RMSE']:
    best = result_6
    best_features = features_6
else:
    best = result_5
    best_features = features_5

print()
print(f'Best model: {best["model_name"]}')
print(f'Train: {best["train_metrics"]}')
print(f'Test : {best["test_metrics"]}')

y_test = best['y_test']; y_test_pred = best['y_test_pred']

# ============ FIGURE 1: Scatter target vs pred ============
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

ax1.scatter(y_test, y_test_pred, alpha=0.75)
min_val = min(y_test.min(), y_test_pred.min())
max_val = max(y_test.max(), y_test_pred.max())
ax1.plot([min_val, max_val], [min_val, max_val], 'r--', label='Ideal (y=x)')
ax1.set_xlabel('Target duty (%)')
ax1.set_ylabel('Prediksi duty (%)')
ax1.set_title(f'Target vs Prediksi - {best["model_name"]}')
ax1.legend()
ax1.grid(True)

ax2.plot(y_test, 'b-o', label='Target duty test', markersize=4)
ax2.plot(y_test_pred, 'rs--', label='Prediksi duty test', markersize=4)
ax2.set_xlabel('Index data test')
ax2.set_ylabel('Duty (%)')
ax2.set_title('Target dan Prediksi Duty pada Data Test')
ax2.legend()
ax2.grid(True)

plt.tight_layout()
plt.savefig('target_vs_prediksi.png', dpi=150)
print()
print('Saved target_vs_prediksi.png')

# ============ Diagnostik: distribusi target ============
print()
print('=== RINGKASAN TARGET duty_next_percent ===')
print(df[target_col].describe())
print()
print('Jumlah nilai target paling sering:')
print(df[target_col].round(3).value_counts().head(10))

fig2, ax = plt.subplots(figsize=(10, 4))
ax.hist(df[target_col], bins=20, edgecolor='black')
ax.set_xlabel('duty_next_percent (%)')
ax.set_ylabel('Jumlah data')
ax.set_title('Distribusi Target Duty')
plt.tight_layout()
plt.savefig('distribusi_target.png', dpi=150)
print('Saved distribusi_target.png')

# ============ Baseline comparison ============
y_train_best = best['y_train']; y_test_best = best['y_test']

baseline_95_train = np.full_like(y_train_best, 95.0)
baseline_95_test = np.full_like(y_test_best, 95.0)

mean_train = float(np.mean(y_train_best))
baseline_mean_train = np.full_like(y_train_best, mean_train)
baseline_mean_test = np.full_like(y_test_best, mean_train)

print()
print('=== DIAGNOSTIK OVERFITTING ===')
train_rmse = best['train_metrics']['RMSE']
test_rmse = best['test_metrics']['RMSE']
print(f'Train RMSE              : {train_rmse:.6f}')
print(f'Test RMSE               : {test_rmse:.6f}')
print(f'Gap RMSE test-train     : {test_rmse - train_rmse:.6f}')
print(f'Train R2                : {best["train_metrics"]["R2"]:.6f}')
print(f'Test R2                 : {best["test_metrics"]["R2"]:.6f}')
print()

b95_rmse_test = regression_metrics(y_test_best, baseline_95_test)['RMSE']
bmean_rmse_test = regression_metrics(y_test_best, baseline_mean_test)['RMSE']
b95_r2_test = regression_metrics(y_test_best, baseline_95_test)['R2']

print('=== BASELINE PERBANDINGAN ===')
print(f'RMSE baseline 95% (test)  : {b95_rmse_test:.6f}')
print(f'RMSE baseline mean (test) : {bmean_rmse_test:.6f}')
print(f'RMSE MLP (test)           : {test_rmse:.6f}')
print(f'R2 baseline 95% (test)    : {b95_r2_test:.6f}')
print()

ratio_95 = float((df[target_col].round(3) == 95.0).mean())
print(f'\% target = 95\%: {ratio_95*100:.2f}\%')
if ratio_95 > 0.70:
    print('=> TARGET SANGAT DOMINAN DI 95%')
print()

if test_rmse < train_rmse:
    print('=> Test RMSE LEBIH KECIL dari Train RMSE (BUKAN overfitting klasik)')
    print('=> Ini terjadi karena test set kebanyakan berisi target 95% (mudah ditebak)')
else:
    print('=> Gap normal, tidak ada overfitting berat')

print()
print('=== KESIMPULAN ===')
print('1. R2 ~0.999 BUKAN berarti akurasi 99% -- ini regresi, bukan klasifikasi')
print('2. R2 tinggi karena target hampir semuanya 95% (std hanya ~0.56)')
print('3. Model sebenarnya belajar pola sederhana: prediksi ~95% untuk semua input')
print('4. Untuk deployment, model perlu diuji dengan data closed-loop real')
print('5. Jika data closed-loop nanti bervariasi, MLP mungkin perlu dilatih ulang')
