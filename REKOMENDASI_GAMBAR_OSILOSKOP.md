# Rekomendasi Pengambilan Gambar Osiloskop — Buku TA

Daftar gambar gelombang yang sebaiknya diambil saat ke lab, beserta tujuan, setting,
dan usulan nama file. Disusun mengikuti kebutuhan tabel/subbab yang masih kosong di
Bab 3 & Bab 4.

> ⚠️ **Keamanan (WAJIB):** sisi keluaran chopper adalah **AC 220 V**. Gunakan
> **probe ÷10** dan **differential probe / trafo isolasi** untuk sisi daya. Jangan
> meng-grounding-kan klip probe langsung ke jalur AC tanpa isolasi (risiko korslet &
> sengatan). Ukur sinyal gate (level rendah) dan sisi daya **secara terpisah** bila
> osiloskop tidak terisolasi.

---

## Peta Penempatan Gambar di Buku (ringkasan)

| Gambar | Letak (Subbab) | Judul Subbab | Mendukung |
|--------|----------------|--------------|-----------|
| A1, A2, A3 | **4.2** | Pengujian Sinyal PWM STM32 | Isi `tab:hasil-pwm-stm32` & `tab:pwm-komplementer`; verifikasi dead time 1,5 µs (rancangan 3.1.2) |
| B1, B2, B3 | **4.3** | Pengujian Rangkaian PWM AC Chopper | Pelengkap `tab:duty-tegangan-rms` (gelombang Vout per duty) |
| C1, C2 | **4.3** | Pengujian Rangkaian PWM AC Chopper | Bukti hardware efektivitas snubber (melengkapi simulasi `fig:simulasi-snubber` di 3.2; rancangan di 3.1.2) |
| D1 | **4.3** atau **4.5** | PWM AC Chopper / Beban Pompa | Sifat beban induktif (V vs I) |
| D2 | **4.3** | Pengujian Rangkaian PWM AC Chopper | Referensi sinus input AC sebelum di-chop |
| D3 | **4.3** | Pengujian Rangkaian PWM AC Chopper | Kondisi duty maksimum (95%) |

> **Catatan:** gambar **rancangan** snubber (skematik RC) tetap di **3.1.2** (metodologi),
> sedangkan gambar **hasil pengukuran** (C1, C2) diletakkan di **4.3** (bab hasil), karena
> di buku TA bagian pengukuran/eksperimen masuk Bab 4, bukan Bab 3.

---

## A. Sinyal PWM & Dead Time (untuk Subbab 4.2 + verifikasi Subbab 3.1.2)

| # | Gambar | Tujuan | Kanal / Setting | Usulan nama file |
|---|--------|--------|-----------------|------------------|
| A1 | **PWM utama (PA8)** | Verifikasi frekuensi (5 kHz) & bentuk duty | CH1 @ PA8; time/div ~50 µs; volt/div sesuai level 3,3 V | `osc_pwm_pa8.png` |
| A2 | **PWM utama + komplementer (PA8 & PA7)** | Tunjukkan dua sinyal **komplementer** (saling berlawanan) | CH1=PA8, CH2=PA7 bersamaan; time/div ~50 µs | `osc_pwm_komplementer.png` |
| A3 | **Zoom Dead Time** | Bukti ada jeda ~**1,5 µs** saat transisi (tak ada overlap) | CH1+CH2 di-zoom; time/div **0,5–1 µs**; trigger di tepi transisi | `osc_dead_time.png` |

> A3 paling penting: ukur dan beri anotasi nilai dead-time terukur (mis. "≈1,5 µs")
> untuk mengisi Tabel `tab:pwm-komplementer` dan menutup klaim di Subbab 3.1.2.

**Tabel yang terisi dari sini:** `tab:hasil-pwm-stm32` (frekuensi & duty terukur) dan
`tab:pwm-komplementer` (kondisi sinyal + dead time).

---

## B. Tegangan Keluaran Chopper per Duty Cycle (untuk Subbab 4.3)

Ambil **gelombang tegangan keluaran AC ter-*chop*** pada beberapa titik duty untuk
menunjukkan "makin besar duty → makin lebar potongan sinus".

| # | Gambar | Duty | Setting | Usulan nama file |
|---|--------|------|---------|------------------|
| B1 | Gelombang Vout duty rendah | **30%** | time/div ~5 ms (≥1 periode 50 Hz); diff probe ÷10 | `osc_vout_duty30.png` |
| B2 | Gelombang Vout duty sedang | **60%** | sama | `osc_vout_duty60.png` |
| B3 | Gelombang Vout duty tinggi | **90%** | sama | `osc_vout_duty90.png` |

> Cukup **3 titik representatif** (rendah/sedang/tinggi) — tidak perlu semua 9 duty.
> Akan saya susun sebagai **grid/tabel gambar tunggal** (mirip tabel respons NN).
> Catat juga Vrms terbaca tiap titik (untuk cross-check Tabel `tab:duty-tegangan-rms`).

---

## C. Efektivitas Snubber pada IGBT (untuk Subbab 3.1.2 / 4.3)

| # | Gambar | Tujuan | Setting | Usulan nama file |
|---|--------|--------|---------|------------------|
| C1 | **VCE IGBT tanpa snubber** | Tunjukkan *spike* & *ringing* saat switching | Probe ÷10 di VCE; time/div ~5–10 µs; trigger di tepi switching | `osc_vce_tanpa_snubber.png` |
| C2 | **VCE IGBT dengan snubber** | Tunjukkan reduksi *spike* & *ringing* | sama persis (agar adil dibandingkan) | `osc_vce_dengan_snubber.png` |

> Ukur amplitudo *spike* (V) di kedua kondisi → tunjukkan persentase reduksi. Ini
> melengkapi simulasi snubber (Gambar `fig:simulasi-snubber`) dengan bukti hardware.

---

## D. Opsional (nilai tambah, ambil jika sempat)

| # | Gambar | Tujuan | Usulan nama file |
|---|--------|--------|------------------|
| D1 | **Tegangan + arus beban bersamaan** | Tunjukkan sifat beban induktif (arus tertinggal tegangan) | `osc_v_dan_i_beban.png` |
| D2 | **Tegangan input AC (referensi)** | Sinus 220 V/50 Hz sebelum di-chop (pembanding) | `osc_vin_ac.png` |
| D3 | **Vout duty 95% (saturasi)** | Kondisi maksimum kerja sistem | `osc_vout_duty95.png` |

---

## Checklist Cepat di Lab
- [ ] A1, A2, A3 — sinyal PWM & dead time
- [ ] B1, B2, B3 — Vout pada duty 30/60/90% (+ catat Vrms)
- [ ] C1, C2 — VCE IGBT sebelum/sesudah snubber (+ catat amplitudo spike)
- [ ] (opsional) D1–D3
- [ ] Setiap tangkapan: pastikan **skala time/div & volt/div terbaca** di layar (untuk
      caption), dan simpan PNG dengan nama sesuai daftar di atas ke folder `gambar/`.

## Catatan integrasi ke buku
Setelah file gambar masuk ke `Template_agath/gambar/`, beri tahu saya — saya akan:
1. Sisipkan A1–A3 ke Subbab 4.2 dan isi tabelnya.
2. Buat grid gambar B1–B3 (per-duty) di Subbab 4.3.
3. Sisipkan C1–C2 (snubber) ke Subbab 3.1.2 / 4.3.
