# Rencana Pengembangan Buku Tugas Akhir
**Judul:** Sistem Pengendalian Tekanan Pompa Air Berbasis Inverter dengan *Neural Network*
**Penulis:** Yoel Yhokhanan Sianipar

> Dokumen ini HANYA rencana (belum mengubah file `.tex` apa pun). Tujuannya memetakan
> sub-bab dan poin yang perlu ditambahkan/dilengkapi agar buku TA tuntas dan layak uji.

---

## 0. Temuan Penting Lebih Dulu (WAJIB diputuskan sebelum menulis)

Ini isu konsistensi yang pasti ditanyakan penguji. Selesaikan dulu di tingkat konsep, baru menulis.

1. **"Inverter" vs "PWM AC Chopper" — istilah belum konsisten.**
   - Judul, abstrak, dan Bab 1 memakai kata **inverter** (DC→AC).
   - Bab 3–4 seluruhnya membahas **PWM AC Chopper** / *AC voltage regulator* (AC 220 V → AC variabel).
   - Batasan Masalah Bab 1 menyebut input **baterai 12 V / power supply DC**, padahal chopper di Bab 3 input-nya **AC 220 V**.
   - **Keputusan yang perlu diambil:** apakah alat sebenarnya inverter (DC→AC) atau AC chopper (AC→AC)? Dari Bab 3, 4, dan data, sistem nyatanya **AC Chopper**. Rekomendasi: samakan seluruh dokumen ke istilah "PWM AC Chopper" dan jelaskan di Bab 1/2 hubungannya dengan konteks PLTS (mis. chopper sebagai pengatur tegangan AC keluaran inverter). Perbaiki juga butir batasan input.

2. **Arsitektur Neural Network di Bab 3 ≠ sistem yang benar-benar dijalankan.**
   - Bab 3 menulis input = `[setpoint, tekanan aktual]`, output = `duty cycle` absolut (sigmoid 0–100%).
   - CHEATSHEET & notebook menunjukkan sistem nyata: controller closed-loop dengan fitur `error, Δerror, duty` menghasilkan **Δduty** (inkremental), di-clamp 70–95%, setpoint 0.30 bar, interval 3 dtk.
   - Ada **dua skema** notebook: `skema2 setpoint 0.85` dan `regresi pressure controller GE80`.
   - **Keputusan:** tetapkan SATU arsitektur final yang benar-benar dipakai, lalu sinkronkan Bab 3 (perancangan) dan Bab 4 (hasil). Jelaskan kalau skema sebelumnya adalah iterasi yang ditinggalkan.

3. **Banyak placeholder `\textit{[isi ...]}` di Bab 3** (seri STM32, jumlah neuron, pustaka, dll). Seri STM32 sudah diketahui dari Bab 2: **STM32F411CE** — isi semua placeholder dengan nilai final.

4. **Seluruh tabel Bab 4 masih kosong**, padahal data CSV/oskiloskop/notebook sudah banyak. Inti pekerjaan Bab 4 = mengisi tabel + membuat grafik + menulis analisis.

---

## 1. BAB 1 — PENDAHULUAN (perlu dirapikan & dilengkapi)

Status: ada, tapi tipis dan ada inkonsistensi.

- **1.1 Latar Belakang** — sudah cukup. Tambahkan 1 paragraf transisi yang menegaskan *gap*: kenapa pendekatan sisi suplai + NN lebih baik dari APC/pressure switch/PID-TRIAC (kuantitatif bila bisa).
- **1.2 Rumusan Masalah** — sekarang hanya 2 poin. Tambah poin agar selaras dengan pengujian:
  1. Perancangan rangkaian daya PWM AC Chopper untuk pengaturan suplai pompa.
  2. Penerapan NN sebagai pengendali tekanan.
  3. (tambahan) Bagaimana performa/kestabilan sistem terhadap perubahan beban keran.
- **1.3 Batasan Masalah** — **perbaiki butir input** (DC vs AC, lihat Temuan #1). Tambah: setpoint/rentang tekanan kerja, jenis pompa (GP125 125 W), frekuensi PWM, lingkup NN (offline training, inference di STM32).
- **1.4 Tujuan** — pecah jadi poin sejajar rumusan masalah.
- **1.5 Manfaat** — sudah ada.
- **1.6 Sistematika Penulisan** — **BELUM ADA, perlu ditambah** (standar buku TA ITS).

---

## 2. BAB 2 — TINJAUAN PUSTAKA (cukup lengkap, perlu penyelarasan)

Sudah ada: Riset Terdahulu, Inverter 1 Fasa, Karakteristik Pompa, Motor Induksi 1 Fasa, PWM AC Chopper, Kontrol Neural Network, STM32F411CE, Sensor Tekanan.

Yang perlu ditambah/diselaraskan:
- **Tambah dasar teori yang dipakai di Bab 3 tapi belum ada di Bab 2:**
  - Rangkaian *snubber* RC (karena Bab 3 menurunkan rumusnya).
  - *Dead time* & *shoot-through* pada full-bridge.
  - *Gate driver* opto (HCPL-3120).
  - IGBT sebagai saklar daya (FGH40N120AN).
  - Metrik evaluasi regresi (MSE/RMSE/MAE/MAPE/R²) — dipakai di Bab 4.
  - Normalisasi min-max & konsep deployment model ke MCU (fixed-point/inference).
- **Selaraskan "Kontrol Neural Network"** dengan arsitektur final (MLP, fitur input, controller inkremental) — lihat Temuan #2.
- **Riset Terdahulu**: jadikan tabel perbandingan (penulis, metode, aktuator, hasil) untuk menonjolkan *novelty* TA ini.

---

## 3. BAB 3 — METODOLOGI (kerangka sudah bagus; isi placeholder & tambah sub-bab)

Struktur sekarang: Desain PWM AC Chopper (Topologi/IGBT, Snubber, Dead Time, STM32+Sensor) → Simulasi PSIM → Implementasi (Peralatan, Perakitan) → Perancangan NN (Arsitektur, Dataset, Pelatihan+Deployment) → Diagram Alir & Jadwal.

**Isi yang harus dilengkapi:**
- **3.1.4** Isi seri STM32 = **STM32F411CE**, lengkapi rangkaian pembagi tegangan sensor (nilai R, faktor pembagi), nilai a & b kalibrasi.
- **3.2 Simulasi PSIM** — pastikan parameter beban R-L mewakili pompa nyata; cantumkan nilai komponen snubber hasil hitung.
- **3.3.1 Peralatan** — lengkapi `[seri]`, `[tipe]`, dan pilih realisasi (PCB EasyEDA / protoboard). Tambah **GUI akuisisi data** ke daftar perangkat lunak (dari CHEATSHEET ada GUI logging/auto-collect).
- **3.4 Perancangan NN** — INTI yang harus dibetulkan:
  - Tetapkan fitur input final (`error, Δerror, duty` → Δduty, atau `[setpoint, P_aktual]` → duty) sesuai sistem nyata.
  - Isi Tabel parameter pelatihan (hidden layer, neuron, aktivasi, optimizer, loss, epoch, learning rate) dari notebook.
  - Jelaskan **logika auto-collect / aturan ΔDuty & clamp 70–95%** (dari CHEATSHEET) sebagai mekanisme pembangkitan label dataset.

**Sub-bab BARU yang sebaiknya ditambahkan di Bab 3:**
- **3.x Perancangan GUI & Mekanisme Akuisisi Data Closed-Loop** — protokol pengambilan data (setpoint, interval, episode, gangguan keran). Ini sudah Anda kerjakan rapi di CHEATSHEET; tinggal diformalkan.
- **3.x Skenario Pengujian & Variasi Beban Keran** — definisikan kondisi beban 0–5 keran, blok gangguan (sweep, acak) sebagai metodologi pengujian.
- **3.x Metrik Evaluasi & Kriteria Keberhasilan** — RMSE/MAE/R² untuk model; settling time, steady-state error, overshoot, recovery time untuk sistem kendali. Definisikan ambang "berhasil".

---

## 4. BAB 4 — HASIL DAN PEMBAHASAN (kerangka tabel lengkap; semua perlu DIISI + grafik + analisis)

Saat ini: kerangka tabel bagus tapi **semua sel kosong** dan pembahasan masih 1 paragraf umum. Ini bagian dengan beban kerja terbesar.

**4.1 Skenario Pengujian** — sudah ada tabel, oke.

**4.2 Sinyal PWM STM32** — isi dari data osiloskop:
- Tabel frekuensi & duty terukur (target 5 kHz, duty 10–90%).
- **Tambah gambar** screenshot osiloskop PA8/PA7 + verifikasi *dead time* 1.5 µs (tidak ada shoot-through). Ini menutup janji Bab 3.

**4.3 Rangkaian PWM AC Chopper** — isi tabel duty vs Vrms (teori vs ukur) + % error; **tambah grafik** duty–Vrms.
- **Sub-bab BARU yang hilang: Hasil Simulasi PSIM.** Bab 3 menjanjikan simulasi (variasi duty, snubber, beban dinamis) tapi Bab 4 belum melaporkan hasilnya. Tambahkan:
  - Bentuk gelombang Vout vs duty (simulasi vs teori).
  - **Efektivitas snubber**: V_spike & ringing sebelum/sesudah (dari folder `snubber` + data osiloskop). Cantumkan nilai Cs, Rs final.
  - Respons beban dinamis.

**4.4 Sensor Tekanan** — isi tabel ADC→tegangan→tekanan + tabel kalibrasi vs referensi; **tambah grafik regresi kalibrasi** (a, b, R²). Data ada di `analisis/` (scatter & regresi tegangan vs pressure).

**4.5 Sistem dengan Beban Pompa** — isi tabel duty–Vout–arus–tekanan & respons perubahan keran; **tambah kurva karakteristik** tekanan vs duty (file `karakteristik_pompa.jpeg` bisa dipakai).

**4.6 Pengambilan Dataset NN** — laporkan jumlah data nyata (CSV: ratusan–ribuan baris, banyak sesi), distribusi kondisi beban, contoh cuplikan, pembagian train/val/test aktual.

**4.7 Pengujian Model NN** — isi parameter final + hasil prediksi + **metrik (MSE/RMSE/MAE/MAPE/R²)** dari notebook; **tambah grafik**: loss curve, prediksi vs aktual (scatter), residual.

**4.8 Pengujian Sistem Kendali Tekanan (closed-loop)** — bagian paling penting untuk membuktikan tujuan:
- Isi tabel respons setpoint (settling time, steady-state error) & respons gangguan beban (recovery time).
- **Tambah grafik time-series** tekanan vs waktu + duty vs waktu saat gangguan keran (data `..._close_loop_*.csv`, `data_closedloop_*`). Ini bukti visual sistem menjaga 0.30 bar saat keran diganggu.
- Tunjukkan perilaku saturasi (clamp 70–95%) sebagai batas fisik.

**Tidak ada sub-bab "Pembahasan" terpisah.** Pembahasan menyatu di setiap sub-bab hasil
(4.2–4.8): tiap tabel/grafik langsung diikuti analisisnya. Maka:
- **Hapus** `\section{Pembahasan}` (4.9) yang sekarang masih ada di `4-pengujian-analisis.tex`.
- Pindahkan poin analisis yang tadinya direncanakan di situ ke sub-bab terkait, mis.:
  - kesesuaian teori-ukur & sumber error tegangan → di 4.3,
  - error kalibrasi sensor & noise → di 4.4,
  - karakteristik/rugi pompa → di 4.5,
  - kelebihan/kekurangan model NN → di 4.7,
  - kestabilan, recovery, saturasi, keterbatasan setpoint 0.35, perbandingan vs APC/PID → di 4.8.
- Pastikan tiap sub-bab punya pola: **sajikan data → bandingkan teori/target → jelaskan penyebab/temuan.**

---

## 5. BAB 5 — PENUTUP (masih `\lipsum`, tulis ulang)

- **5.1 Kesimpulan** — jawab tiap rumusan masalah dengan angka konkret (mis. "NN menjaga tekanan 0.30 bar dengan error tunak ± ... bar; RMSE model ... ; recovery time ... s").
- **5.2 Saran** — pengembangan: tambah fitur input (turunan tekanan), kuantisasi int16 di STM32, perluas rentang setpoint, uji pompa lebih besar, integrasi nyata dengan inverter PLTS, kontrol prediktif.

---

## 6. Elemen Pelengkap Buku TA (cek kelengkapan)

- Abstrak ID/EN — saat ini masih "diharapkan" (future tense). Tulis ulang dengan **hasil nyata** (angka) setelah Bab 4 jadi. Cek nama author di `main.tex` masih "Elon Musk" (placeholder template) — ganti.
- Lembar pengesahan & pernyataan keaslian (saat ini sebagian di-comment di `main.tex`).
- Daftar Pustaka (`pustaka/pustaka.bib`) — pastikan semua sitasi Bab 2/3 (Infineon AN2007-04, datasheet IGBT, HCPL-3120, DFRobot) masuk.
- Daftar Gambar/Tabel/Lampiran — lampirkan listing firmware STM32 (inference NN), skema PCB, kode notebook training.
- Biografi penulis & Kata Pengantar.

---

## 7. Urutan Kerja yang Disarankan

1. **Putuskan Temuan #1 & #2** (istilah inverter/chopper + arsitektur NN final). Semua bergantung pada ini.
2. Rapikan **Bab 1** (rumusan/batasan/tujuan + sistematika).
3. Lengkapi **placeholder Bab 3** + tambah 3 sub-bab metodologi baru.
4. Tambah dasar teori yang kurang di **Bab 2**.
5. **Olah data → isi Bab 4** (prioritas: kalibrasi sensor → duty-Vrms → metrik NN → closed-loop). Buat semua grafik.
6. Tulis **Bab 5** & **abstrak** berbasis angka hasil.
7. Lengkapi elemen pelengkap (sitasi, lampiran, identitas).

---

### Catatan aset data yang sudah tersedia (untuk mengisi Bab 4)
- CSV closed-loop banyak sesi (Mei–Juni 2026) → grafik time-series & dataset NN.
- `analisis/` → regresi & scatter tegangan vs pressure (kalibrasi sensor & karakteristik).
- `DATA OSILOSKOP/` → sinyal PWM, dead time, V_spike snubber.
- `snubber/` (datasheet & app note) → perhitungan & pembahasan snubber.
- Notebook `training_*.ipynb` → parameter & metrik model NN.
- `karakteristik_pompa.jpeg`, `perhitungan_ripple_voltage_filter.xlsx` → pendukung Bab 3/4.
