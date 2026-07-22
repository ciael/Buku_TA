# 📋 CHEAT SHEET — Pengambilan Data Closed-Loop (Auto-Collect)

**Setpoint: 0.30 bar | Interval: 3 dtk | Duty min: 70% | Duty maks: 95% | Pompa LEWAT chopper | Keran = setengah-buka**

---

## PRINSIP PALING PENTING (baca dulu ini)

1. **Anda atur KERAN (kasar), GUI atur DUTY.** Tidak perlu memutar keran sampai tekanan pas 0.30 — set kira-kira setengah, biarkan duty yang mengejar.
2. **Keran = gangguan, Duty = aktuator.** Tekanan awal 0.35 / 0.41 / berapa pun TIDAK masalah; controller menariknya ke 0.30 sendiri.
3. **Keran setengah TIDAK perlu presisi.** Variasi justru memperkaya data. Model tak melihat posisi keran (hanya `error, Δerror, duty`).
4. **"Settle" = hover di ~0.28–0.32 dengan koreksi kecil ±1**, BUKAN diam mati di 0.300. Sistem sensitif + ada noise → itu normal & tetap data bagus.
5. **Pertahankan trik setengah-keran.** (Full-buka → <0.1 bar, tak berguna.)

---

## ✅ SEBELUM MULAI (sekali saja)
1. Pompa lewat **AC chopper** (bukan 220V langsung).
2. **Connect** → cek telemetry jalan (terutama **Pressure** dari sensor PC1).
3. **Start Logging** → file: `data_closedloop_<tanggal>.csv`.
4. Set **Setpoint 0.30**, **Interval 3.0**, **Duty min 70** di panel Auto Data Collection.
5. Pemanasan 1 menit → buka CSV → pastikan `is_decision`, `episode_id`, `setpoint_bar` terisi.

## 🔧 KARAKTERISASI CEPAT (WAJIB, ~3 menit) — peta 5 Juni SUDAH USANG
Sensor baru (PC1) baca lebih tinggi. Petakan ulang dulu: Auto-collect OFF, set duty 80 + Apply, lalu untuk tiap keran catat tekanan di telemetry:

| Keran | P @ duty 80% (isi sendiri) | Arah controller ke 0.30 |
|-------|---------------------------|--------------------------|
| 4 (paling terbuka) | ______ | jika <0.30 → **NAIK** |
| 3 | ~0.35 | **TURUN** |
| 2 | ~0.41 | **TURUN** |
| 1 | ______ | **TURUN** |
| 0 (paling tertutup) | ______ | **TURUN** (mentok floor) |

> **Aturan umum:** makin SEDIKIT keran (makin tertutup) → tekanan makin TINGGI → butuh duty makin RENDAH. Kebalikan dari peta 5 Juni!

## 🎛️ ATURAN ΔDuty (GUI yang jalankan)
`err = setpoint − pressure` →
`>0.08:+3 | >0.05:+2 | >0.02:+1 | ±0.02:0 | <-0.02:-1 | <-0.05:-2 | <-0.08:-3`
(otomatis di-clamp **70–95%**)

## ⚠️ KALAU TEKANAN TAK SAMPAI 0.30 (SATURASI) — NORMAL, BUKAN ERROR
Auto-collect menangani sendiri lewat clamp 70–95. **JANGAN ganti episode, JANGAN panik.**

- **Tekanan < 0.30 walau duty 95** (kemungkinan 4 keran) → mentok **ceiling 95%**, ΔDuty=0.
- **Tekanan > 0.30 walau duty 70** (kemungkinan 0–1 keran) → mentok **floor 70%**, ΔDuty=0.
- → biarkan **3–4 keputusan** di rail untuk merekam perilaku "mentok", lalu ubah keran / Stop.

❌ Jangan diamkan lama di rail (hindari 20+ keputusan ΔDuty=0).
👉 Data saturasi ini berharga untuk Bab 4 (batas fisik). Kalau di floor 70 pun masih overshoot, **turunkan Duty min ke 65/60** — tapi pantau pompa tetap mulus (lihat catatan keamanan).

## 🔑 ATURAN EMAS
1. **Anda atur KERAN, GUI atur DUTY.** Jangan geser duty manual saat auto-collect ON.
2. Klik **"Episode Baru (+1)"** HANYA saat mulai episode baru (reset/loncat duty / ganti setpoint). JANGAN saat hanya ubah keran.
3. Ganti keran di tengah kejar → **klik tombol keran** (label), auto-collect tetap ON.
4. **Tahan di setpoint maks 3–4 keputusan**, lalu ganggu/lanjut.
5. **`is_decision` otomatis** — tak perlu diapa-apakan.

---

## 📑 DAFTAR EPISODE

> **Arah kejar dikendalikan DUTY AWAL, bukan tebakan keran:**
> mau data **NAIK** → mulai duty **rendah (70)** | mau data **TURUN** → mulai duty **tinggi**.
> Setelah Apply, lihat tekanan awal: <0.30 = naik, >0.30 = turun. Dua-duanya bagus.

### 🔥 PEMANASAN — ~3 menit
| No | Setpoint | Duty awal | Keran | Ep.Baru? | Est. |
|----|----------|-----------|-------|----------|------|
| W1 | 0.30 | 70 | **4** (amati: harusnya naik) | — (ep 1) | 1 mnt |
| W2 | 0.30 | 85 | **1** (harusnya turun) | ✅ | 1 mnt |

### ⬆️ BLOK A — kejar NAIK (duty awal 70, keran terbuka 4 & 3) — ~5 menit
| No | Setpoint | Duty awal | Keran | Ep.Baru? | Est. |
|----|----------|-----------|-------|----------|------|
| A1 | 0.30 | 70 | **4** | ✅ | 50 dtk |
| A2 | 0.30 | 70 | **4** | ✅ | 50 dtk |
| A3 | 0.30 | 70 | **3** | ✅ | 50 dtk |
| A4 | 0.30 | 70 | **3** | ✅ | 50 dtk |

### ⬇️ BLOK B — kejar TURUN (keran tertutup 0–3) — ~5 menit
| No | Setpoint | Duty awal | Keran | Ep.Baru? | Est. |
|----|----------|-----------|-------|----------|------|
| B1 | 0.30 | 80 | **0** (mentok floor 70, settle) | ✅ | 45 dtk |
| B2 | 0.30 | 85 | **1** | ✅ | 45 dtk |
| B3 | 0.30 | 90 | **2** | ✅ | 45 dtk |
| B4 | 0.30 | 90 | **3** | ✅ | 45 dtk |

> ⚠️ **Keamanan:** keran 0–1 bertekanan tinggi. Mulai duty jangan kelewat tinggi & **pantau tekanan ≤ 0.9 bar**. Kalau mendekati, turunkan duty / buka keran segera.

### 🔻 BLOK C — SWEEP TUTUP 4→0 (gangguan, 1 episode) — ~5 menit
| No | Setpoint | Duty awal | Keran (berurutan) | Ep.Baru? | Est. |
|----|----------|-----------|-------------------|----------|------|
| C1 | 0.30 | 75 | **4 → 3 → 2 → 1 → 0** | ✅ | 2 mnt |
| C2 | 0.30 | 75 | **4 → 3 → 2 → 1 → 0** | ✅ | 2 mnt |

### 🔺 BLOK D — SWEEP BUKA 0→4 (gangguan, 1 episode) — ~5 menit
| No | Setpoint | Duty awal | Keran (berurutan) | Ep.Baru? | Est. |
|----|----------|-----------|-------------------|----------|------|
| D1 | 0.30 | 80 | **0 → 1 → 2 → 3 → 4** | ✅ | 2 mnt |
| D2 | 0.30 | 80 | **0 → 1 → 2 → 3 → 4** | ✅ | 2 mnt |

### 🎲 BLOK E — GANGGUAN ACAK (DATA PALING BERHARGA) — ~12 menit
| No | Setpoint | Duty awal | Keran (acak) | Ep.Baru? | Est. |
|----|----------|-----------|--------------|----------|------|
| E1 | 0.30 | 75 | **2 → 4 → 1 → 3 → 0** | ✅ | 2 mnt |
| E2 | 0.30 | 80 | **3 → 1 → 4 → 2** | ✅ | 1.5 mnt |
| E3 | 0.30 | 75 | **1 → 3 → 0 → 2 → 4** | ✅ | 2 mnt |
| E4 | 0.30 | 80 | **4 → 2 → 3 → 1** | ✅ | 1.5 mnt |
| E5 | 0.30 | 78 | **0 → 2 → 4 → 1** | ✅ | 1.5 mnt |
| E6 | 0.30 | 80 | **3 → 0 → 2 → 4** | ✅ | 1.5 mnt |

### 🎯 BLOK F — SETPOINT LAIN (kalau sempat) — ~5 menit
| No | Setpoint | Duty awal | Keran | Ep.Baru? | Est. |
|----|----------|-----------|-------|----------|------|
| F1 | **0.25** | 75 | **4 → 2 → 3** | ✅ (+ubah setpoint) | 1.5 mnt |
| F2 | **0.25** | 70 | **4** | ✅ | 1 mnt |
| F3 | **0.35** | 80 | **1 → 3 → 2** | ✅ (+ubah setpoint) | 1.5 mnt |
| F4 | **0.35** | 75 | **3 → 4** | ✅ | 1 mnt |

> ⚠️ Setpoint 0.35 mungkin tak tercapai di keran terbuka (4) → biarkan saturasi, lanjut.

---

## 📊 TARGET & CEK AKHIR
- **Total ≈ 24 episode, ~45 menit** (≈ **500+ baris** `is_decision=1`).
- Kalau < 500 baris → ulangi Blok C/D/E dengan urutan keran berbeda.
- **Cek keseimbangan:** jumlah ΔDuty **naik** ≈ **turun**. Kalau timpang, tambah Blok A (naik) atau Blok B (turun).
- **Stop Logging** di akhir → backup CSV.

## 🔁 ALUR TIAP EPISODE (hafalkan)
```
1. (kalau perlu) Stop Auto-Collect
2. Set duty awal → Apply Duty   (pompa muter, tunggu ~5 dtk)
3. Klik tombol keran awal → klik "Episode Baru (+1)"
4. (kalau ganti setpoint) ubah Setpoint dulu
5. Start Auto-Collect → biarkan duty mengejar (jangan disentuh)
6. Hover ~0.30 (3–4 keputusan) ATAU ganti keran utk gangguan
7. Stop Auto-Collect → episode berikutnya
```

## ⏸️ BERHENTI / LANJUT (snubber panas / ganti hari)
- **Berhenti:** Stop Auto-Collect → Stop Logging → shutdown aman (duty 50% → variac 0V).
- **Lanjut:** variac 220V → Start Logging **dgn FILE BARU** (`..._sesi2.csv`) → lanjut. (Notebook gabung otomatis pakai offset.)
