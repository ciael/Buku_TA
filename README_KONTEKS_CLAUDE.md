# README KONTEKS — Tugas Akhir Yoel Yhokhanan Sianipar

> **Untuk Claude (app Windows):** File ini adalah handoff konteks lengkap dari sesi kerja sebelumnya di Claude Code (VSCode). Baca seluruhnya sebelum mulai bekerja. Folder utama TA ini adalah `E:\SEMESTER 8\TA\BUKU TA_YOEL` — semua aspek TA (buku LaTeX, kode program, notebook, data, gambar, rencana) ada di sini.

---

## 1. Identitas & Topik TA

| Item | Nilai |
|---|---|
| Nama | Yoel Yhokhanan Sianipar |
| NRP | 5022221081 |
| Departemen | Teknik Elektro, FTEIC, Institut Teknologi Sepuluh Nopember (ITS) |
| Lahir | Medan, 29 September 2004 |
| Judul TA | **Sistem Pengendalian Tekanan Pompa Air Berbasis Inverter dengan Neural Network** |
| Dosen Pembimbing 1 | Prof. Dr. Muhammad Rivai, S.T., M.T. |
| Dosen Pembimbing 2 | Dr. Suwito, S.T., M.T. |
| Lab | B402 |
| Email | sianiparyoel9@gmail.com |

**Inti sistem:** Mengendalikan tekanan air pada pompa dengan mengatur tegangan/frekuensi efektif motor induksi 1 fasa melalui **PWM AC Chopper** (full-bridge 4 IGBT, bipolar chopping). Setpoint tekanan dijaga oleh kontroler **Neural Network (MLP)** yang dijalankan di mikrokontroler/PC. NN melakukan *behavior cloning* terhadap perilaku kontrol.

---

## 2. Struktur Folder Utama (`E:\SEMESTER 8\TA\BUKU TA_YOEL`)

```
BUKU TA_YOEL/
├── README_KONTEKS_CLAUDE.md          <- FILE INI (handoff konteks)
├── RENCANA_PENGEMBANGAN_TA.md        <- Dokumen rencana/roadmap utama (PENTING, sering diupdate)
├── training_mlp_3input_closedloop.ipynb  <- Notebook training NN (sumber arsitektur & data Bab 3.4)
├── uji_NN_uji2_16juni.csv            <- Data hasil uji 2 (respons setpoint, 5 episode)
└── Template_agath/                   <- ROOT proyek LaTeX (buku TA)
    ├── main.tex
    ├── TA_Yoel_Sianipar.pdf          <- Output PDF terakhir (117 hal, ~14MB, 0 error)
    ├── bab/
    │   ├── 1-pendahuluan.tex
    │   ├── 2-tinjauan-pustaka.tex
    │   ├── 3-metodologi.tex
    │   ├── 4-pengujian-analisis.tex
    │   └── 5-penutup.tex
    ├── abstrak/
    │   ├── abstrak-id.tex
    │   └── abstrak-en.tex
    ├── lainnya/
    │   ├── kata-pengantar.tex
    │   ├── lampiran.tex
    │   ├── biografi-penulis.tex
    │   └── pernyataan-keaslian (2 ttd dosen pembimbing)
    ├── pustaka/
    │   ├── variables.tex             <- \name, \advisor, \coadvisor, \nrp dll.
    │   └── pustaka.bib               <- daftar pustaka (biblatex/biber)
    ├── kode/                         <- kode program untuk lampiran (sudah disanitasi ASCII)
    │   ├── main.c                    (~1219 baris, firmware STM32)
    │   ├── pwm_ac_chopper_gui.py     (~1058 baris, GUI Python)
    │   └── training_mlp.py           (~241 baris, diekstrak dari notebook)
    └── gambar/                       <- semua figure (skematik, PCB, osiloskop, GUI, respons NN)
```

> **CATATAN BUILD PENTING:** VSCode LaTeX Workshop auto-build sempat mengunci `main.aux` bersamaan dengan build CLI → korupsi `.aux`. Solusi yang dipakai: build CLI memakai `-jobname` terpisah agar tidak bentrok. Toolchain: `pdflatex` + `biber`, cek PDF via `pdfinfo`/`pdftoppm`.

---

## 3. Status Tiap Bab (kondisi terakhir)

### Bab 1 — Pendahuluan
- Latar belakang sudah **diperluas**. Rumusan masalah sudah dirapikan (commit terakhir).

### Bab 2 — Tinjauan Pustaka / Dasar Teori
Subbab Dasar Teori yang **sudah ada**:
1. Inverter 1 Fasa
2. Karakteristik Pompa Air
3. Motor Induksi 1 Fasa
4. Rangkaian PWM AC Chopper
5. Kontrol Neural Network (mencakup MLP, neuron/perceptron, forward + backprop, gradient descent, inference)
6. **Mikrokontroler STM32U545RE** (Cortex-M33, 160 MHz, ADC 14-bit) — **DIGANTI dari STM32F411CE** (semua referensi STM32F411CE → STM32U545RE sudah diubah di Bab 2)
7. Sensor Tekanan Air

> ⚠️ **PEKERJAAN BERIKUTNYA YANG TERTUNDA (belum dieksekusi):** Menambahkan subbab Dasar Teori baru ke `bab/2-tinjauan-pustaka.tex`. Rekomendasi sudah ditulis lengkap di **Bagian 9 `RENCANA_PENGEMBANGAN_TA.md`**. Yang perlu ditambahkan:
>
> **A. Elektronika Daya (WAJIB — dipakai Bab 3 tapi belum ada landasannya):**
> - IGBT sebagai Saklar Daya (V_CES, I_C, V_CE(sat), waktu switching)
> - Gate Driver / Optocoupler (isolasi, penguatan sinyal gerbang, propagation delay)
> - Rangkaian Snubber RC (induktansi parasitik, voltage spike, ringing)
> - Dead Time & Shoot-through (PWM komplementer satu leg)
>
> **B. Lengkapi subbab Neural Network (dipakai Bab 3.4):**
> - Fungsi Aktivasi & Fungsi Rugi (tanh/linear, MSE)
> - Normalisasi/Standardisasi Data (StandardScaler / z-score)
> - Pembagian Data & Overfitting (+ behavior cloning)
>
> **C. Evaluasi & Kendali (PRIORITAS, diminta user):**
> - **Metrik Evaluasi Model Regresi: MAE, MSE, RMSE, R²**
> - Sistem Kendali Loop Tertutup & Parameter Respons (setpoint, error tunak, settling time, overshoot, recovery time, saturasi)
>
> **Opsional:** Daya pada Sistem AC (RMS, daya aktif, faktor daya) untuk Bab 4.5.
> **TIDAK perlu jadi dasar teori:** PSIM (cukup disebut di metodologi).
> **Reminder:** setiap teori baru WAJIB diberi sitasi di `pustaka/pustaka.bib`.

### Bab 3 — Metodologi (struktur sudah dirombak atas permintaan user)
Struktur final yang disepakati:
- **3.1 Desain dan Perhitungan Spesifikasi**
  - 3.1.1 Pemodelan
  - 3.1.2 Penentuan Nilai Komponen
    - **3.1.2.2 Snubber** — fokus ke **verifikasi formula** (bukan simulasi). Formula final:
      - C_sn = L_s·I_o²/(V_pk−V_cc)² ≈ 46 nF → dipilih 100 nF
      - R_sn ≤ t_on,min/(5·C_sn) ≈ 66 Ω → realisasi 5×330 Ω paralel
      - P_R = ½·C_sn·(V_pk²−V_cc²)·f_sw
      - ⚠️ **CATATAN PENTING (feedback user):** Klaim "1µF per 100A rule of thumb" **DIHAPUS** karena setelah diverifikasi, klaim itu **TIDAK ADA** di IR App Note (di paper hanya ada formula 1 dan penggunaan 1µF pada uji 125–150A). Jangan masukkan lagi klaim rule-of-thumb itu.
  - Dead time = **1.5 µs**
- **3.2 Simulasi** — subbab simulasi snubber (3.2.2 lama) **DIHAPUS**; skenario diringkas ke tegangan/arus vs duty.
- **3.3 Implementasi**
- **3.4 Neural Network** (dinaikkan jadi section tersendiri atas permintaan user; juga memuat **metode akuisisi data**)
  - Arsitektur: **MLP 3-4-1**, input = [error, Δerror, duty], output = ΔDuty
  - Aktivasi tanh, optimizer **L-BFGS**, loss MSE, **StandardScaler**, *behavior cloning*
  - Isi diekstrak dari notebook `training_mlp_3input_closedloop.ipynb` (arsitektur + tabel data nyata)

Komponen daya yang dipakai: IGBT **FGH40N120AN**, gate driver **HCPL-3120**.

### Bab 4 — Pengujian dan Analisis
- **TIDAK ada subbab pembahasan terpisah 4.9** — pembahasan menyatu di tiap poin (keputusan user).
- **Tabel 4.2 (`tab:hasil-pwm-stm32`):** kolom = duty cycle | PA8 active | PA7 freewheeling. 10 baris (mis. duty 50 → 49,25/49,49 ; duty 90 → 89,94/9,09).
- Tabel metrik NN diisi dengan **data nyata** dari notebook.
- **Respons setpoint (uji 2):** 5 event 0.25 → 0.30 → 0.35 → 0.30 → 0.25 bar. Data dari `uji_NN_uji2_16juni.csv`. Logging "messy" (setpoint dulu baru episode) → disegmentasi per setpoint dominan tiap episode; settling dihitung dari saat NN aktif.
- **Di bawah Tabel 4.5:** ada **perbandingan tegangan (ukur vs simulasi)** dan **perbandingan arus (ukur vs simulasi)**, pakai figure berdampingan via helper `\cmpsub` (width=\linewidth, height=4.3cm, keepaspectratio).
- Tabel 4.8 divisualisasikan; perbandingan **dengan vs tanpa kontroler NN** ditampilkan. Tabel 4.9 lama dihapus (tidak relevan).
- Respons NN ditampilkan sebagai **grid 5×2 gambar tunggal** (tiap sel = 1 gambar, di-generate dari kode Python terpisah) — sesuai format yang user minta.

### Bab 5 — Penutup
- Kesimpulan & Saran sudah ditulis.

### Bagian depan/belakang
- **Abstrak ID & EN:** sudah diupdate mencakup ringkasan sampai kesimpulan (hasil + metrik).
- **Kata Pengantar:** 9 ucapan terima kasih (Tuhan Yesus; orang tua Bapak/Mamak, Dedek, Sheline; dosen pembimbing Pak Rivai & Pak Suwito; teman Lab B402; Sarah; tim Antasena ITS; ELKA e62; Teknik Elektro ITS e62; semua pihak). Sudah final di `lainnya/kata-pengantar.tex`.
- **Pernyataan Keaslian:** 2 tanda tangan dosen pembimbing.
- **Lampiran (`lainnya/lampiran.tex`):** penomoran **ANGKA** (Lampiran 1–6), bukan huruf. Isi:
  1. Skematik
  2. PCB
  3. Instalasi
  4. Pengujian
  5. GUI (2 figure: tampilan GUI & tampilan GUI saat uji)
  6. Kode Program: 6.1 main.c (C) · 6.2 gui.py (Python) · 6.3 training_mlp.py (Python)
  - Notebook `training_mlp_3input_closedloop.ipynb` juga dimasukkan ke lampiran.
  - Helper `\lampgambar`; style listing `\lstdefinestyle{lampirankode}{... upquote=false}`.
- **Biografi Penulis:** sudah diisi (SD Latihan HKBP Pearaja Tarutung, SMPK Immanuel Batam, SMAN 1 Batam → ITS jalur UTBK-SBMPTN; aktif SRE ITS & Antasena ITS sebagai Electronics & Powertrain Engineer).

---

## 4. Daftar Keputusan Penting (User vs Claude)

### Keputusan USER (yang harus dihormati):
- Bab 4 **tanpa** subbab pembahasan 4.9 terpisah.
- Metodologi dirombak ke struktur 3.1–3.4; NN dinaikkan jadi **3.4 tersendiri** (termasuk metode akuisisi data).
- Respons kontroler NN ditampilkan sebagai **gambar tunggal per sel** (grid 5×2), bukan satu gambar gabungan.
- Gambar dimasukkan **langsung ke dalam tabel/figure**, bukan placeholder.
- Snubber 3.1.2.2 fokus **verifikasi formula**, simulasi 3.2.2 dihapus.
- Tabel 4.2 → kolom duty/PA8 active/PA7 freewheeling.
- Tabel 4.5 → ambil ulang data + ada gambar gelombang tegangan per duty + perbandingan simulasi.
- Tanpa beban sulit memunculkan arus → cukup visualisasi yang relevan; tambahkan perbandingan dengan vs tanpa NN.
- Lampiran pakai **angka**, bukan huruf.
- STM32F411CE → **STM32U545RE** di mana-mana (fokus Bab 2).
- Uji NN dilakukan untuk uji 2 (respons setpoint, 5 episode); cukup di **1 jenis keran**.

### Keputusan/temuan CLAUDE (yang divalidasi user):
- Verifikasi klaim "1µF/100A rule of thumb" → **tidak ada di sumber**, jadi dihapus (user yang minta cek: "apakah benar rule of thumb itu ada dalam file tersebut?").
- Solusi konflik build `.aux` → pakai `-jobname` terpisah dari LaTeX Workshop.
- Guard `\IfFileExists` + placeholder box untuk gambar yang belum ada (agar compile tidak gagal).
- Sanitasi non-ASCII di kode (→ jadi `->`, Δ jadi `d`, dll.) + `upquote=false` untuk listing.
- Ekstraksi data nyata dari notebook lewat skrip replikasi Python (sklearn/pandas/numpy); split PNG respons via PIL (deteksi gap putih).

---

## 5. Error yang Pernah Muncul & Solusinya (referensi cepat)

| Masalah | Solusi |
|---|---|
| Gambar hilang bikin gagal compile | `\IfFileExists` + placeholder box |
| Underscore di `\texttt{}` → "Missing $" | Hapus nama file dari teks placeholder |
| Label duplikat saat pindah blok | Hapus label asli setelah relokasi |
| Referensi menggantung | Update target `\ref`/`\label` |
| `\textquotedbl` OT1 di listing | `\usepackage{textcomp}` + `upquote=false` |
| Non-ASCII di kode | Skrip sanitizer Python |
| `main.aux` korup | `-jobname` terpisah (hindari lock LaTeX Workshop) |
| `&` tak ter-escape (biografi) | `\&` |
| `\emph{` tak tertutup (abstrak-en) | gabung jadi satu blok `\emph` |

---

## 6. Langkah Selanjutnya (roadmap)

1. **Bab 2 (PRIORITAS SAAT INI):** tulis isi subbab Dasar Teori baru ke `bab/2-tinjauan-pustaka.tex` sesuai Bagian 9 `RENCANA_PENGEMBANGAN_TA.md`. Prioritas: Metrik Evaluasi (MAE/MSE/RMSE/R²), IGBT, Gate Driver, Snubber, Dead Time, Sistem Kendali Loop Tertutup. Jangan lupa sitasi `pustaka.bib`.
2. **Prosiding / paper:** user berencana membuat prosiding (paper ringkas) dari TA ini. *(Tugas terpisah, dilakukan setelah struktur TA beres.)*
3. Re-export PDF setelah perubahan: `pdflatex` → `biber` → `pdflatex` ×2 (pakai jobname terpisah bila perlu).

---

## 7. Dokumen Rujukan di Folder Ini
- **`RENCANA_PENGEMBANGAN_TA.md`** — roadmap detail + Bagian 9 berisi rekomendasi judul Dasar Teori Bab 2 (tabel: judul · isi singkat · dipakai di mana · urutan akhir + catatan sitasi). **Baca ini untuk detail eksekusi Bab 2.**
- **`training_mlp_3input_closedloop.ipynb`** — sumber arsitektur & data NN.
- **`uji_NN_uji2_16juni.csv`** — data respons setpoint uji 2.

---

*Dibuat sebagai handoff dari sesi Claude Code (VSCode) ke Claude app Windows. Tanggal: 2026-06-21.*
