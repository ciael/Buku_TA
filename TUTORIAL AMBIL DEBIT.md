# TUTORIAL AMBIL DEBIT AIR — CHEAT SHEET

> Acuan praktis pengambilan data **debit air (Q)** untuk TA.
> Sistem: Pompa air (sumber **trafo slider**) → diatur PWM AC chopper → keran.
> Prinsip dasar: **Q = Volume ÷ waktu**.

---

## 0. RINGKASAN SUPER SINGKAT (baca ini saat di lab)

1. Pompa nyala, tunggu aliran **stabil**.
2. Botol di bawah keran → mulai stopwatch **bareng**.
3. Tampung **20 detik** → tutup bareng.
4. Ukur volume tiap botol pakai **gelas ukur**.
5. **Q (L/menit) = Volume(mL) ÷ 1000 ÷ (20 ÷ 60) = Volume(mL) ÷ 333**.
6. Catat **tekanan + duty** saat itu juga.
7. **Ulang 3×**, ambil rata-rata.

> Rumus kilat untuk t = 20 detik: **Q [L/menit] = Volume [mL] ÷ 333**.
> Contoh: 900 mL ÷ 333 = **2,7 L/menit**.

---

## 1. TUJUAN

Mengukur besaran debit air pada keran untuk:
- Karakterisasi pompa (debit vs duty / debit vs jumlah keran).
- Membuktikan kontroler **NN** menjaga aliran tetap memadai saat beban berubah.

---

## 2. ALAT YANG DIPERLUKAN

| No | Alat | Jumlah | Catatan |
|----|------|--------|---------|
| 1 | Botol 1500 mL | 4 | Satu botol per keran |
| 2 | Gelas ukur | 1 | Untuk mengukur volume (JANGAN andalkan cetakan botol) |
| 3 | Stopwatch / HP | 1 | Untuk timing |
| 4 | Lap / ember | secukupnya | Antisipasi tumpah |
| 5 | Alat tulis / form | 1 | Catat data (form di bawah) |

> **Idealnya 2 orang:** satu pegang stopwatch & aba-aba, satu urus botol/keran.

---

## 3. PERSIAPAN (KALIBRASI BOTOL) — WAJIB SEKALI DI AWAL

Cetakan volume di botol sering meleset 5–10%. Kalibrasi dulu:

1. Tuang air pakai **gelas ukur** ke botol: 500 mL, 1000 mL, 1500 mL.
2. Tandai garisnya pakai spidol permanen.
3. Pakai garis hasil kalibrasi ini sebagai acuan, **bukan** angka cetakan botol.

> Kalau pakai metode "waktu tetap" (Metode B), volume tetap diukur ulang pakai gelas ukur tiap pengambilan — paling akurat.

---

## 4. DUA METODE PENGUKURAN

### Metode A — Volume tetap, ukur WAKTU  *(akurat untuk 1 keran)*
- Tampung sampai garis tertentu (mis. 1000 mL), catat **waktu** isi.
- **Q = Volume ÷ waktu.**
- Pakai kalau ingin teliti per satu keran.

### Metode B — Waktu tetap, ukur VOLUME  *(praktis untuk banyak keran)* ✅ DISARANKAN
- Tampung **waktu tetap 20 detik**, lalu ukur volume tiap botol.
- **Q = Volume ÷ 20 s.**
- Pakai untuk pengujian banyak keran sekaligus.

> **Aturan penting:** atur supaya waktu isi **> 10 detik** agar error stopwatch kecil.
> Kalau air terlalu deras (botol penuh < 5 detik), pakai Metode B 20 detik
> atau tampung sampai garis 500 mL saja.
> Catatan: 20 detik aman selama debit < 4,5 L/menit (botol 1500 mL belum luber).

---

## 5. PROSEDUR PENGAMBILAN DATA

### A. Persiapan tiap titik uji
1. Pastikan sumber pompa dari **trafo slider** (bukan inverter/baterai).
2. Set kondisi uji (duty atau jumlah keran sesuai skenario di bawah).
3. **Tunggu aliran STABIL** (tekanan tidak naik-turun lagi). Ini syarat wajib.

### B. Pengambilan (Metode B – waktu tetap)
1. Siapkan botol kosong di bawah tiap keran yang terbuka.
2. Aba-aba "MULAI" → masukkan aliran ke botol + start stopwatch **bersamaan**.
3. Pada detik ke-20 → aba-aba "STOP" → singkirkan botol **bersamaan**.
4. Ukur volume tiap botol pakai gelas ukur, catat.
5. Catat **tekanan settle** dan **duty** saat itu.
6. **Ulang 3×** untuk tiap titik, ambil rata-rata.

> **Jangan ubah bukaan keran saat menampung.** Botol hanya menadah; tidak mengganggu aliran. ✅

---

## 6. RUMUS & KONVERSI

**Rumus utama:**
```
Q = Volume / waktu
```

**Satuan & konversi:**
- 1 L = 1000 mL
- 1 menit = 60 detik
- Q [L/menit] = (Volume[mL] / 1000) / (waktu[s] / 60)
- Q [L/detik] = Volume[mL] / 1000 / waktu[s]

**Pintasan untuk t = 20 detik:**
```
Q [L/menit] = Volume [mL] / 333
```

**Debit total (banyak keran):**
```
Q_total = (V1 + V2 + ... + Vn) / waktu
```

**Contoh perhitungan:**
- 1 keran, terkumpul 900 mL dalam 20 s → 900/333 = **2,7 L/menit**.
- 3 keran (600+550+580 mL) dalam 20 s → 1730/333 = **5,2 L/menit total**.

---

## 7. SKENARIO PENGUJIAN (PILIH SESUAI KEBUTUHAN)

### Skenario 1 — Debit vs JUMLAH KERAN (open-loop, duty tetap)
> Tunjukkan efek beban. Duty dipatok (mis. 85%), keran 1→4.

| Keran | Vol total (mL) | Waktu (s) | Q total (L/mnt) | Tekanan (bar) |
|-------|----------------|-----------|-----------------|---------------|
| 1 |  | 20 |  |  |
| 2 |  | 20 |  |  |
| 3 |  | 20 |  |  |
| 4 |  | 20 |  |  |

### Skenario 2 — Debit vs DUTY CYCLE (open-loop, 4 keran terbuka)
> Tunjukkan chopper mengatur aliran pompa.

| No | Duty (%) | Vol total (mL) | Q total (L/mnt) | Tekanan (bar) |
|----|----------|----------------|-----------------|---------------|
| 1 | 70 |  |  |  |
| 2 | 75 |  |  |  |
| 3 | 80 |  |  |  |
| 4 | 85 |  |  |  |
| 5 | 90 |  |  |  |
| 6 | 95 |  |  |  |

### Skenario 3 — Debit saat NN BERJALAN (closed-loop, setpoint 0,30 bar) ⭐
> Bukti NN menjaga aliran saat beban berubah. Ukur saat sudah SETTLE.

| Keran | Duty settle (%) | Tekanan settle (bar) | Vol 20 s (mL) | Q total (L/mnt) |
|-------|-----------------|----------------------|---------------|-----------------|
| 1 |  |  |  |  |
| 2 |  |  |  |  |
| 3 |  |  |  |  |
| 4 |  |  |  |  |

> **Tips skripsi:** kalau sempat, ambil Skenario 1 (open-loop) DAN Skenario 3 (NN jalan)
> pada jumlah keran yang sama → selisihnya membuktikan peran kontroler NN.
> Kalau waktu mepet, prioritaskan **Skenario 3**.

---

## 8. FORM PENCATATAN MENTAH (per titik, 3 pengulangan)

```
Tanggal       : ____________      Skenario : ____________
Kondisi       : Duty = ____ %  | Jumlah keran = ____ | Setpoint = ____ bar
Mode sumber   : Trafo slider / Inverter (lingkari)

                Ulang-1   Ulang-2   Ulang-3   Rata-rata
Vol keran 1 :  ______    ______    ______    ______  mL
Vol keran 2 :  ______    ______    ______    ______  mL
Vol keran 3 :  ______    ______    ______    ______  mL
Vol keran 4 :  ______    ______    ______    ______  mL
Vol TOTAL   :  ______    ______    ______    ______  mL
Waktu       :  __20__    __20__    __20__            s
Tekanan     :  ______    ______    ______    ______  bar
Duty        :  ______    ______    ______    ______  %

Q total (L/mnt) = Vol total rata-rata / 333 = __________ L/menit
```

---

## 9. CHECKLIST SEBELUM AMBIL DATA ✅

- [ ] Botol sudah dikalibrasi (garis spidol benar)
- [ ] Gelas ukur & stopwatch siap
- [ ] Sumber pompa = trafo slider
- [ ] Aliran sudah STABIL sebelum mulai timing
- [ ] (Jika NN) tunggu sampai tekanan SETTLE
- [ ] Aba-aba mulai/stop kompak (kalau berdua)
- [ ] Tiap titik diulang 3×
- [ ] Catat tekanan + duty bareng debit
- [ ] Foto/rekam video sebagai bukti dokumentasi

---

## 10. KESALAHAN UMUM (HINDARI)

| ❌ Salah | ✅ Benar |
|---------|---------|
| Ukur saat aliran masih naik-turun | Tunggu stabil/settle dulu |
| Andalkan angka cetakan botol | Ukur ulang pakai gelas ukur |
| Botol penuh < 5 detik (timing meleset) | Pakai 30 detik / garis lebih kecil |
| Ubah bukaan keran saat menampung | Keran tetap, botol cuma menadah |
| Ambil 1× saja | Ulang 3× lalu rata-rata |
| Lupa catat tekanan & duty | Catat semua sekaligus |

---

## 11. SETELAH DATA TERKUMPUL

1. Hitung Q rata-rata tiap titik.
2. Masukkan ke tabel LaTeX di `bab/4-pengujian-analisis.tex`:
   - Skenario 1 → `tab:debit-keran`
   - Skenario 2 → `tab:debit-duty`
   - Skenario 3 → gabung ke `tab:respons-nn-keran` (kolom debit)
3. Buat grafik (Q vs duty, atau Q vs jumlah keran) untuk pembahasan.

---

*Selamat mengambil data! Pelan-pelan, stabil dulu, baru timing. 🚰*
