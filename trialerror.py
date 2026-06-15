import pandas as pd
import numpy as np
import itertools
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.neural_network import MLPClassifier
from sklearn.metrics import accuracy_score
import warnings
warnings.filterwarnings('ignore')

# ==========================================
# 1. PERSIAPAN DATA DAN EKSTRAKSI FITUR
# ==========================================
file_input = 'Hasil_Gabungan_10Detik_Terakhir.xlsx'

print(f"Membaca dataset gabungan: {file_input}...")
try:
    df = pd.read_excel(file_input)
except FileNotFoundError:
    print(f"File {file_input} tidak ditemukan!")
    exit()

sensor_kolom = ['V135', 'V136', 'V137', 'V3']
for col in sensor_kolom:
    if df[col].dtype == object:
        df[col] = df[col].astype(str).str.replace(',', '.')
    df[col] = pd.to_numeric(df[col], errors='coerce')

df = df.dropna(subset=sensor_kolom)

print("Mengekstrak fitur (Sensing - Preheat)...")
all_features = []

for filename, file_group in df.groupby('Nama_File'):
    kategori = file_group['Kategori_Sampel'].iloc[0].capitalize()
    
    df_preheat = file_group[file_group['Siklus'].str.contains('Preheat', case=False, na=False)]
    if df_preheat.empty: continue
    mean_preheat = df_preheat[sensor_kolom].mean()

    df_sensing = file_group[file_group['Siklus'].str.contains('Sensing', case=False, na=False)]
    for siklus_name, sensing_group in df_sensing.groupby('Siklus'):
        mean_sensing = sensing_group[sensor_kolom].mean()
        diff_value = mean_sensing - mean_preheat
        
        all_features.append({
            'MQ135': diff_value['V135'],
            'MQ136': diff_value['V136'],
            'MQ137': diff_value['V137'],
            'MQ3': diff_value['V3'],
            'Kategori': kategori
        })

df_features = pd.DataFrame(all_features)
print(f"Total data siap olah: {len(df_features)} sampel.\n")

# ==========================================
# 2. SPLIT DATA & NORMALISASI
# ==========================================
fitur_cols = ['MQ135', 'MQ136', 'MQ137', 'MQ3']
X_raw = df_features[fitur_cols]
y_raw = df_features['Kategori']

X_train_raw, X_test_raw, y_train, y_test = train_test_split(
    X_raw, y_raw, test_size=0.30, random_state=42, stratify=y_raw
)

max_values = X_train_raw.max()
X_train_scaled = X_train_raw / max_values
X_test_scaled = X_test_raw / max_values

encoder = LabelEncoder()
encoder.fit(['Segar', 'Sedang', 'Busuk']) 
y_train_enc = encoder.transform(y_train)
y_test_enc = encoder.transform(y_test)

# ==========================================
# 3. PERSIAPAN KOMBINASI HYPERPARAMETER (GRID SEARCH)
# ==========================================
# Membuat daftar kombinasi layer dan neuron
daftar_konfigurasi = []

# 1 Hidden Layer (1 s/d 10)
for i in range(1, 21):
    daftar_konfigurasi.append((i,))

# 2 Hidden Layer (1 s/d 10)
#for i in range(1, 21):
     #for j in range(1, 21):
         #daftar_konfigurasi.append((i, j))

#3 Hidden Layer (1 s/d 10)
#for i in range(1, 21):
     #for j in range(1, 21):
         #for k in range(1, 21):
             #daftar_konfigurasi.append((i, j, k))

total_eksperimen = len(daftar_konfigurasi)
print(f"Memulai eksperimen untuk {total_eksperimen} kombinasi arsitektur ANN...")
print("Proses ini mungkin memakan waktu beberapa menit. Silakan tunggu...\n")

# ==========================================
# 4. TRAINING OTOMATIS & PENCATATAN HASIL
# ==========================================
hasil_eksperimen = []

for index, config in enumerate(daftar_konfigurasi):
    # Mengurangi max_iter menjadi 1000 agar loop ribuan kali tidak terlalu lama,
    # namun tetap cukup untuk mencari konvergensi pada dataset kecil
    ann = MLPClassifier(hidden_layer_sizes=config, max_iter=3000, random_state=42)
    
    # Latih model
    ann.fit(X_train_scaled, y_train_enc)
    
    # Hitung akurasi
    pred_train = ann.predict(X_train_scaled)
    pred_test = ann.predict(X_test_scaled)
    
    acc_train = accuracy_score(y_train_enc, pred_train) * 100
    acc_test = accuracy_score(y_test_enc, pred_test) * 100
    
    # Simpan hasil
    hasil_eksperimen.append({
        'Jumlah Hidden Layer': len(config),
        'Konfigurasi Neuron': str(config),
        'Akurasi Training (%)': round(acc_train, 2),
        'Akurasi Testing (%)': round(acc_test, 2)
    })
    
    # Tampilkan progress setiap 100 iterasi agar terminal tidak terlihat hang
    if (index + 1) % 100 == 0 or (index + 1) == total_eksperimen:
        print(f"Progress: [{index + 1}/{total_eksperimen}] kombinasi selesai dievaluasi...")

# ==========================================
# 5. EXPORT HASIL KE EXCEL
# ==========================================
df_hasil = pd.DataFrame(hasil_eksperimen)

# Mengurutkan dari akurasi Testing tertinggi, kemudian Akurasi Training tertinggi
df_hasil_sorted = df_hasil.sort_values(by=['Akurasi Testing (%)', 'Akurasi Training (%)'], ascending=[False, False])

nama_file_output = 'Hasil_Tuning_Arsitektur_ANN.xlsx'
df_hasil_sorted.to_excel(nama_file_output, index=False)

print("\n" + "="*50)
print(f"✅ EKSPERIMEN SELESAI!")
print(f"Data akurasi dari {total_eksperimen} arsitektur telah diurutkan dari yang terbaik.")
print(f"File disimpan sebagai: {nama_file_output}")
print("="*50)

# Menampilkan top 3 arsitektur terbaik di terminal
print("\n🏆 Top 3 Arsitektur Terbaik:")
print(df_hasil_sorted.head(3).to_string(index=False))