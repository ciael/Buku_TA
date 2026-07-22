# 🧪 PANDUAN UJI NN (MLP) DI ALAT — untuk Data Bab 4

> **Tujuan:** menguji kontroler NN (yang sudah di-flash di STM32) dan merekam data untuk
> 3 tabel Bab 4: (1) tracking per keran, (2) penjejakan setpoint, (3) rejeksi gangguan.

> ⚠️ **BEDAKAN dua mode di GUI:**
> - **Auto-Collect** = dulu untuk ambil data LATIH (Python yang mengatur duty). **TIDAK dipakai sekarang.**
> - **Apply Mode → NN** = STM32 (model terlatih) yang mengatur duty. **INI yang kita uji sekarang.**

---

## ✅ PERSIAPAN (sekali di awal)
1. **Firmware sudah di-flash** dengan MLP 3-input (build + flash di STM32CubeIDE).
2. Pompa lewat **AC chopper** (bukan 220V langsung). Variac pada tegangan kerja.
3. GUI: **Connect** → cek telemetry **Pressure** bergerak wajar.
4. Klik **Start Logging** → beri nama sesuai sesi, mis. `uji_NN_uji1_<tgl>.csv`
   (lihat **Skema File** di bawah). Biarkan ON selama satu sesi.
5. Pastikan radio mode di **MANUAL** dulu.

## 🔑 ATURAN PENTING
- NN mengambil keputusan **tiap 3 detik** → settling perlu belasan detik, **sabar**.
- **Pantau tekanan ≤ 0,9 bar.** Kalau mendekati, segera **Apply Mode → MANUAL** / buka keran.
- "NN Output (Duty)" di panel performa = duty yang sedang diterapkan NN. Lihat **Error → ~0**
  untuk tahu sudah settle.
- **TIDAK wajib tandai Event manual.** Skrip analisis mendeteksi otomatis dari kolom yang
  berubah sendiri saat Anda klik tombol: `nn_mode` (Apply Mode NN), `setpoint_bar`
  (Apply Setpoint), `valve_open_count` (tombol keran). Kotak **Event CSV** opsional (label saja).

### ⚠️ ATURAN PEMBEDA (wajib, agar skrip mengelompokkan dengan benar)
- **Antar-keran di Uji 1:** selalu **Apply Mode → MANUAL** dulu sebelum ganti keran berikutnya.
  Jeda NN-off ini menandai "tes baru per keran" (bukan gangguan).
- **Di Uji 3 (gangguan):** **JANGAN matikan NN** saat mengubah keran. NN tetap ON → perubahan
  keran dibaca sebagai **gangguan**.

### 🎛️ Tombol GUI yang dipakai
| Tombol | Fungsi |
|---|---|
| **Connect / Start Logging** | sambung + mulai rekam CSV |
| **Spinbox Duty → Apply Duty** | set duty awal (mode MANUAL) |
| **Tombol keran 0–4** | set & label jumlah keran (`valve_open_count`) |
| **Spinbox Setpoint NN → Apply Setpoint** | kirim setpoint ke NN (`setpoint_bar`) |
| **Radio NN/MANUAL → Apply Mode** | nyalakan/matikan kontroler NN (`nn_mode`) |
| **Stop Logging** | tutup file CSV |

## 🗂️ SKEMA FILE — uji terpisah (karena snubber panas)

Boleh uji **tidak sekaligus**. Kuncinya: **beri tag uji di NAMA FILE** supaya skrip
mengelompokkan benar. Satu sesi = satu file:

| Sesi | Nama file CSV | Isi |
|---|---|---|
| Sesi 1 | `uji_NN_uji1_<tgl>.csv` | Uji 1 (semua keran 4→0) |
| Sesi 2 | `uji_NN_uji2_<tgl>.csv` | Uji 2 (setpoint 0,25/0,30/0,35) |
| Sesi 3 | `uji_NN_uji3_<tgl>.csv` | Uji 3 (gangguan keran) |

**Alur tiap sesi:** matikan dari sesi sebelumnya → dinginkan snubber → nyalakan lagi
(variac 220V) → Connect → **Start Logging dengan nama sesuai tabel di atas** → jalankan
uji-nya → **Stop Logging** → shutdown aman (Apply Mode MANUAL → Stop PWM → variac 0V).

- Wajib ada kata **`uji1`/`uji2`/`uji3`** di nama file (huruf kecil) — itu yang dibaca skrip.
- Kalau satu uji pun terlalu panas, boleh dipecah lagi (mis. `uji_NN_uji1_keran4.csv`,
  `uji_NN_uji1_keran3.csv`) — selama tetap mengandung `uji1`, skrip menggabungnya.
- Taruh semua file di folder `E:\SEMESTER 8\TA\BUKU TA_YOEL\`, lalu jalankan skrip sekali
  untuk semua (lihat "Analisis Otomatis").

---

## 🧩 UJI 1 — Tracking Setpoint per Jumlah Keran
**Mengisi Tabel "Respons Kontroler NN pada Berbagai Jumlah Keran" (`tab:respons-nn-keran`).**
Ulangi untuk keran **4, 3, 2, 1, 0**:

```
1. Apply Mode → MANUAL.  Set duty 80 → Apply Duty.
2. Set keran fisik (mis. 4) → klik tombol keran "4".
3. Set Setpoint 0,30 → Apply Setpoint.
4. Event: ketik "uji1 keran4 mulai" → Tandai.
5. Apply Mode → NN. ← NN mulai mengejar 0,30 (tiap 3 dtk)
6. Tunggu sampai tekanan diam di ~0,30 (slider duty berhenti, output Δ≈0).
7. Event: ketik "uji1 keran4 settle" → Tandai.
8. Diamkan ~10 dtk lagi (rekam kondisi mantap), lalu Apply Mode → MANUAL.
9. Lanjut keran berikut (ulangi dari langkah 1).
```
Yang dicatat per keran (dibaca dari CSV, lihat bagian "Cara Ekstrak"):
**duty settle, tekanan settle, error steady, settling time.**

> Catatan: untuk keran banyak (4) bisa mentok 95% tak sampai 0,30; untuk keran sedikit (0)
> bisa mentok 70%. Itu **saturasi** yang wajar — tetap catat sebagai hasil.

---

## 🎯 UJI 2 — Penjejakan Setpoint
**Mengisi Tabel "Respons Sistem terhadap Perubahan Setpoint" (`tab:respons-setpoint`).** Keran dibuat **tetap** (mis. 2):

```
1. Set keran 2 → klik tombol "2".  Apply Mode → NN.
2. Set Setpoint 0,25 → Apply Setpoint → Event "SP 0,25" → Tandai.  Tunggu settle.
3. Set Setpoint 0,30 → Apply Setpoint → Event "SP 0,30" → Tandai.  Tunggu settle.
4. Set Setpoint 0,35 → Apply Setpoint → Event "SP 0,35" → Tandai.  Tunggu settle.
5. Apply Mode → MANUAL.
```
Yang dicatat per setpoint (sesuai kolom tabel): **tekanan awal, tekanan stabil,
settling time, error stabil**. (Tekanan awal = tekanan tepat sebelum setpoint diubah.)

---

## 🌊 UJI 3 — Rejeksi Gangguan (perubahan keran mendadak)
**Mengisi Tabel "Respons Sistem terhadap Gangguan Beban" (`tab:respons-gangguan-beban`).** Setpoint tetap 0,30:

```
1. Set keran 2 → klik "2".  Apply Mode → NN.  Tunggu settle di 0,30.
2. GANGGU: buka cepat jadi 4 keran → klik tombol "4" + Event "gangguan 2->4" → Tandai.
3. Amati tekanan turun lalu pulih ke 0,30. Tunggu pulih.
4. GANGGU lagi: tutup jadi 1 keran → klik "1" + Event "gangguan 4->1" → Tandai. Tunggu pulih.
5. (opsi) ulangi pola lain. Lalu Apply Mode → MANUAL.
```
Yang dicatat per gangguan (sesuai kolom tabel): **tekanan sebelum gangguan,
tekanan setelah (pulih), waktu pemulihan**. (Deviasi tekanan maks boleh dicatat
sebagai tambahan untuk analisis.)

---

## ⚡ ANALISIS OTOMATIS (cara cepat — disarankan)

Tidak perlu hitung manual. Setelah uji selesai:
1. Simpan semua CSV dengan nama berawalan **`uji_NN_`** (mis. `uji_NN_15juni.csv`) di folder
   `E:\SEMESTER 8\TA\BUKU TA_YOEL\`.
2. Jalankan:
   ```
   python analyze_uji_nn.py
   ```
3. Skrip otomatis mengelompokkan tiap fase (Uji 1/2/3) dan mencetak **baris siap salin**
   ke tabel `tab:respons-nn-keran`, `tab:respons-setpoint`, `tab:respons-gangguan-beban`.

Skrip menghitung sendiri: tekanan settle, duty settle, error steady, settling time,
deviasi maks, dan waktu pulih (pita ±0,02 bar). Agar pengelompokan benar, **patuhi
"ATURAN PEMBEDA"** di atas (NN-off antar-keran Uji 1; NN tetap ON untuk gangguan Uji 3).

---

## 📐 CARA EKSTRAK MANUAL (kalau tak pakai skrip)

Buka CSV (Excel/Python). Kolom kunci: `pc_timestamp`, `pressure_bar`, `duty_percent`,
`setpoint_bar`, `valve_open_count`, `nn_mode`, `event`.

| Metrik | Cara hitung |
|---|---|
| **Tekanan settle** | rata-rata `pressure_bar` selama ~10 dtk terakhir saat mantap |
| **Duty settle** | `duty_percent` saat mantap |
| **Error steady** | `setpoint_bar − tekanan settle` |
| **Settling time** | selisih waktu dari event "mulai" sampai `pressure_bar` masuk pita ±0,02 bar dari setpoint **dan tetap di dalamnya** |
| **Deviasi maks (gangguan)** | `max|pressure_bar − setpoint|` setelah event "gangguan" |
| **Waktu pulih** | dari event "gangguan" sampai `pressure_bar` kembali masuk pita ±0,02 bar |

**Tips:** band ±0,02 bar (deadband NN). Karena ada noise, gunakan "masuk pita dan bertahan
≥3 keputusan (≈9 dtk)" sebagai kriteria settle agar tidak terkecoh fluktuasi.

---

## 🧷 RINGKAS ALUR TOMBOL GUI
```
Connect → Start Logging
   (per uji)  Set keran/duty/setpoint → Apply → Event Tandai → Apply Mode NN → tunggu → Apply Mode MANUAL
Selesai → Stop Logging → backup CSV
```

## ⚠️ KEAMANAN
- Selalu siap klik **Apply Mode → MANUAL** lalu **Stop PWM** kalau tekanan/alat tidak wajar.
- Jangan tinggal alat saat NN aktif di keran sedikit (tekanan bisa tinggi).
- Snubber panas → beri jeda antar-uji (Apply Mode MANUAL + Stop PWM saat istirahat).
