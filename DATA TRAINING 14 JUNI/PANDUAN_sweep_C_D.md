# 🌀 PANDUAN JELAS — Blok C & Blok D (Sweep Keran)

> **Inti:** Blok C & D itu **gangguan bertahap** dalam **SATU episode** masing-masing.
> Auto-collect **NYALA TERUS**. Anda cuma **buka/tutup keran + klik tombolnya**.
> Setpoint tetap 0.30. Duty digerakkan GUI sendiri.

---

## 🔻 BLOK C = TUTUP keran satu per satu (4 → 0)

**Ide:** mulai banyak keran terbuka, lalu **tutup** bertahap.
Tiap menutup keran → tekanan **NAIK** → controller menurunkan duty mengejar 0.30.

### Langkah C1 (satu episode):
```
1. Set duty 75 → Apply Duty           (pompa muter)
2. Klik tombol keran "4"
3. Klik "Episode Baru (+1)"
4. Start Auto-Collect                  ← NYALA, biarkan terus sampai langkah 11
5. TUNGGU sampai tekanan hover ~0.30   (slider duty berhenti bergerak, ~15 dtk)

6. TUTUP 1 keran (jadi 3) → klik tombol "3"
7. TUNGGU hover ~0.30 lagi             (~10–15 dtk)

8. TUTUP 1 keran (jadi 2) → klik tombol "2"  → TUNGGU settle
9. TUTUP 1 keran (jadi 1) → klik tombol "1"  → TUNGGU settle
10. TUTUP 1 keran (jadi 0) → klik tombol "0" → TUNGGU 3–4 keputusan
    (di 0 keran tekanan tinggi → duty mentok floor 70, wajar)

11. Stop Auto-Collect                  → episode C1 SELESAI
```
**Ulangi langkah 1–11 untuk C2** (klik "Episode Baru" lagi di awal C2).

**Yang Anda lihat:** keran makin sedikit → tekanan melonjak → **duty turun** 75→…→70.

---

## 🔺 BLOK D = BUKA keran satu per satu (0 → 4)

**Ide:** kebalikan C. Mulai semua keran tertutup, lalu **buka** bertahap.
Tiap membuka keran → tekanan **TURUN** → controller menaikkan duty mengejar 0.30.

### Langkah D1 (satu episode):
```
1. Set duty 80 → Apply Duty           (pompa muter)
2. Klik tombol keran "0"               (semua tertutup)
3. Klik "Episode Baru (+1)"
4. Start Auto-Collect                  ← NYALA, biarkan terus sampai langkah 11
5. TUNGGU settle                       (0 keran tekanan tinggi → mungkin mentok
                                        floor 70, biarkan 3–4 keputusan)

6. BUKA 1 keran (jadi 1) → klik tombol "1"
7. TUNGGU hover ~0.30                   (~10–15 dtk)

8. BUKA 1 keran (jadi 2) → klik tombol "2"  → TUNGGU settle
9. BUKA 1 keran (jadi 3) → klik tombol "3"  → TUNGGU settle
10. BUKA 1 keran (jadi 4) → klik tombol "4" → TUNGGU settle
    (di 4 keran tekanan rendah → duty naik; bisa sampai 95 kalau tak capai 0.30)

11. Stop Auto-Collect                  → episode D1 SELESAI
```
**Ulangi langkah 1–11 untuk D2.**

**Yang Anda lihat:** keran makin banyak → tekanan turun → **duty naik** 80→…→95.

---

## 📌 ATURAN YANG SAMA UNTUK C & D

| Hal | Aturan |
|-----|--------|
| Auto-Collect | **ON terus** sepanjang episode (jangan dimatikan saat ganti keran) |
| Episode Baru | klik **1× di awal** tiap episode (C1, C2, D1, D2). JANGAN saat ganti keran |
| Tombol keran | klik **setiap kali** buka/tutup keran (untuk label) |
| Tunggu | hover ~0.30 selama **3–4 keputusan** (~10–15 dtk) sebelum ganti keran |
| Duty | **jangan disentuh** — GUI yang atur |
| Tekanan | tak perlu pas 0.300; hover 0.28–0.32 = sudah oke |

## ⚖️ Kenapa C DAN D (dua-duanya)?
- **C** = tekanan NAIK → duty TURUN (controller belajar "tekanan kelebihan → kurangi duty").
- **D** = tekanan TURUN → duty NAIK (controller belajar "tekanan kurang → tambah duty").
- Dua arah ini harus seimbang supaya model tidak berat sebelah.

## ⚠️ Keamanan
Saat keran sedikit/tertutup (0–1) tekanan bisa tinggi → **pantau ≤ 0.9 bar**.
Kalau mendekati, buka keran / turunkan duty segera.
