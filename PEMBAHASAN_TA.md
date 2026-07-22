# Ringkasan: Konversi Buku TA → Prosiding Jurnal (.docx)

**Tanggal:** 20 Juni 2026
**Penulis TA:** Yoel Yhokhanan Sianipar (NRP 5022221081)
**Judul:** *Sistem Pengendalian Tekanan Pompa Air Berbasis Inverter dengan Neural Network*

---

## 1. Tujuan Pekerjaan
Mengubah Buku Tugas Akhir (proyek LaTeX, 5 bab) menjadi **paper prosiding**
dalam format `.docx` mengikuti template prosiding ITS (HIMATEKTRO) yang
disediakan di `E:\SEMESTER 8\TA\Jurnal TA.docx`.

**Sumber konten:** proyek LaTeX di `E:\SEMESTER 8\TA\BUKU TA_YOEL\Template_agath`
(5 bab, ~32 gambar, ~43 blok persamaan, ~20 sitasi APA, 22 entri `pustaka.bib`).

**Kondisi awal template:** `Jurnal TA.docx` masih berisi paper contoh milik
mahasiswa lain (Ega Bagus Saputra — "Unit Commitment MILP Sulbagsel"), format
2 kolom gaya IEEE.

---

## 2. Keputusan Akhir yang Disepakati
| Aspek | Keputusan |
|---|---|
| **Panjang** | Ringkas, ~6 halaman isi + 1 halaman pustaka (≤7). Hasil akhir = **5 halaman**. |
| **Persamaan** | **Equation Word asli (OMML)** — bisa diedit di Word, bukan gambar. |
| **Abstrak** | **Bahasa Indonesia saja** + Kata Kunci. |
| **Gambar** | Dipilihkan yang kunci + **plot respons tekanan pengujian di-regenerate** agar lebih jelas/bagus. |
| **Sitasi** | Konversi APA → **bernomor IEEE** `[1]`–`[14]`. |

---

## 3. Temuan Teknis Penting (Struktur Template)
- Style template: `Title`, `Authors`, `Abstract`, `IndexTerms`, `Heading1/2`,
  `Text`, `caption`, `References`, `Reference Head`.
- Halaman: **US Letter**, 2 kolom (lebar kolom 3,5"), lebar penuh 7,2".
- Judul & penulis tampil full-width via **framePr** (text frame) di style —
  framePr asli di-nonaktifkan dan diganti **section 1-kolom** agar kokoh
  terhadap panjang judul yang berbeda.
- Style `References` sudah **auto-numbering** `[n]` (tidak perlu nomor manual).
- Konversi persamaan: **LaTeX → MathML (`latex2mathml`) → OMML
  (`MML2OMML.XSL` bawaan MS Office)** lalu disuntik via `python-docx`.
- Gambar full-width di tengah dokumen 2 kolom: memakai **continuous section
  break** (state kolom 2→1→2).

---

## 4. Isi Prosiding yang Dihasilkan
Pemetaan Buku TA → Prosiding:
- **Judul / Penulis / Abstrak** ← abstrak-id + biografi.
- **I. Pendahuluan** ← Bab 1.
- **II. Dasar Teori** ← Bab 2 + penjelasan_mlp (PWM AC chopper, kontrol NN, STM32, sensor).
- **III. Metodologi** ← Bab 3 (pemodelan sistem, dead time & snubber, arsitektur NN, dataset & pelatihan).
- **IV. Hasil dan Pembahasan** ← Bab 4 (sinyal PWM & dead time, tegangan RMS vs duty, kinerja NN, pengujian kendali tekanan).
- **V. Kesimpulan** ← Bab 5.
- **Daftar Pustaka** ← pustaka.bib (14 referensi bernomor).

Konten terverifikasi:
- **10 persamaan** OMML (5 pecahan, 6 sigma) — antara lain duty ratio, V_L(t),
  dead time Infineon, snubber, standardisasi z-score, forward pass MLP
  (h_j & Δduty), clamp duty, loss MSE, V_out = D·V_in.
- **6 gambar**: skema sistem, skematik PWM AC chopper, arsitektur NN MLP 3-4-1,
  pengukuran dead time (≈1,48 µs), + **2 plot regenerate** (respons tekanan
  per keran small-multiples & ringkasan steady-state) — full-width.
- **3 tabel**: tegangan RMS vs duty + error, MLP vs baseline (R²=0,915),
  respons kontroler NN per jumlah keran.

---

## 5. Regenerasi Gambar Respons Tekanan
- Sumber data: `E:\SEMESTER 8\TA\BUKU TA_YOEL\uji_NN_uji1_16juni.csv`
  (1 episode, setpoint 0,30 bar, kondisi 0–4 keran).
- Skrip: `jurnal_build\regen_plots.py` (matplotlib, DPI 320, serif, anotasi
  steady/error berwarna, pita toleransi ±0,02 bar).
- Output: `jurnal_build\gambar_jurnal\respons_tekanan_nn.png` &
  `respons_nn_per_keran.png`.
- Nilai steady-state cocok 100% dengan tabel TA:
  0,513 / 0,482 / 0,309 / 0,292 / 0,276 bar; duty 70 / 76,5 / 78,7 / 80,6 / 90,2 %.

---

## 6. File Hasil & Lokasi
| File | Keterangan |
|---|---|
| `E:\SEMESTER 8\TA\Jurnal TA.docx` | **Prosiding final** (5 halaman). |
| `E:\SEMESTER 8\TA\Jurnal TA_BACKUP.docx` | Cadangan template asli (paper contoh Ega Bagus). |
| `E:\SEMESTER 8\TA\jurnal_build\build_jurnal.py` | Skrip pembangun docx (bisa dijalankan ulang). |
| `E:\SEMESTER 8\TA\jurnal_build\regen_plots.py` | Skrip regenerate plot. |
| `E:\SEMESTER 8\TA\jurnal_build\gambar_jurnal\` | Gambar hasil regenerate. |
| `E:\SEMESTER 8\TA\jurnal_build\result_preview.pdf` | Pratinjau PDF hasil render Word. |

---

## 7. Verifikasi
- Dirender ke PDF lewat MS Word → semua tampil benar (judul, 2 kolom, persamaan
  native, gambar + caption, sitasi konsisten dengan daftar pustaka bernomor).
- Cek XML: 10 `<m:oMath>`, header di tiap section (6 headerReference), 6 sectPr,
  21 gambar tertanam, integritas zip OK, file terbuka ulang tanpa error.

---

## 8. Catatan untuk Revisi Lanjutan
1. Teks sengaja dipadatkan jadi ~5 halaman (boleh ditambah bila perlu sub-bagian
   atau gambar lain, mis. waveform tegangan terukur vs simulasi, respons
   setpoint-tracking).
2. Halaman 4 ada ruang kosong di bawah karena 2 gambar full-width mengambang
   (wajar di layout 2 kolom; bisa dirapikan).
3. Periksa **nama pembimbing** (dipakai tanpa gelar: "Muhammad Rivai, Suwito")
   dan **nomor prosiding "134"** (bawaan template — ganti sesuai panitia).

---

## 9. Cara Membangun Ulang (bila ada revisi)
```bash
# 1) Regenerate plot (opsional, bila data berubah)
python "E:\SEMESTER 8\TA\jurnal_build\regen_plots.py"

# 2) Bangun docx (selalu mulai dari Jurnal TA_BACKUP.docx)
python "E:\SEMESTER 8\TA\jurnal_build\build_jurnal.py"
```
Prasyarat Python: `python-docx`, `lxml`, `latex2mathml`, `matplotlib`, `pandas`
(MS Office terpasang untuk `MML2OMML.XSL` & render PDF).
