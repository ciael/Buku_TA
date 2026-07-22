# Gambar Respons Tekanan untuk Prosiding (Uji 1, 2, 3)

Dihasilkan oleh `gambar_prosiding.py` dari data di folder `DATA UJI`
(`uji_NN_uji1/2/3_16juni.csv`). Jalankan ulang dengan:

```
python gambar_prosiding.py
```

## Spesifikasi gambar
- Ukuran **persis 8 cm (lebar) × 5 cm (tinggi)**, DPI **400** (1259×787 px).
- Di Word: **Insert Picture → set Width = 8 cm** (tinggi otomatis 5 cm).
  Jangan diregangkan; biarkan rasio terkunci agar tulisan tetap proporsional.
- **Judul tidak dipasang di gambar** — tulis sebagai *caption* di Word.
- Setpoint utama 0,30 bar, pita toleransi ±0,02 bar (deadband NN).
- Semua angka pakai koma desimal (format Indonesia).

## Daftar file & usulan caption

| File | Usulan caption (Word) |
|---|---|
| `uji1_respons_tekanan_per_keran.png` | Respons tekanan kontroler NN pada berbagai jumlah keran (setpoint 0,30 bar; tiap segmen disejajarkan dari saat NN aktif). |
| `uji1_ringkasan_steady.png` | Tekanan *steady-state* kontroler NN per jumlah keran terhadap setpoint 0,30 bar. |
| `uji2_penjejakan_setpoint.png` | Respons penjejakan perubahan setpoint (0,25–0,30–0,35–0,30–0,25 bar) pada beban tetap. |
| `uji3_rejeksi_gangguan.png` | Respons rejeksi gangguan kontroler NN terhadap perubahan jumlah keran mendadak (setpoint 0,30 bar). |
| `uji1_tekanan_duty.png` | Respons tekanan dan *duty cycle* kontroler NN per jumlah keran (segmen NN disambung; setpoint 0,30 bar). |
| `uji2_tekanan_duty.png` | Respons tekanan, setpoint, dan *duty cycle* saat penjejakan perubahan setpoint. |
| `uji3_tekanan_duty.png` | Respons tekanan dan *duty cycle* saat rejeksi gangguan perubahan jumlah keran. |

> Tiga file `*_tekanan_duty.png` menampilkan **tekanan (sumbu kiri) + duty cycle
> (sumbu kanan)** dalam satu grafik. Empat gambar pertama (tekanan saja) tetap
> tersedia — pilih sesuai kebutuhan penjelasan di prosiding.

## Angka kunci (steady-state, dihitung saat NN aktif)
| Jumlah keran | Tekanan steady (bar) | Duty steady (%) | Keterangan |
|---|---|---|---|
| 0 | 0,513 | 70,0 | saturasi (duty di batas bawah) |
| 1 | 0,301 | 76,5 | dalam pita ±0,02 |
| 2 | 0,307 | 78,6 | dalam pita ±0,02 |
| 3 | 0,292 | 80,7 | dalam pita ±0,02 |
| 4 | 0,298 | 90,2 | dalam pita ±0,02 |

Catatan: nilai dihitung dari rata-rata ~8 keputusan terakhir tiap segmen pada
`nn_mode == 1` (saat NN benar-benar mengendalikan), sehingga konsisten dengan
tabel respons NN per keran di Bab 4 / prosiding.
