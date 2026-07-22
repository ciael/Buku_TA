# SCRIPT GAMBAR BAB 4

Script Python yang menghasilkan **gambar olahan data** di Bab 4.
Nama file = nomor gambar tempat ia muncul, agar mudah dicari saat ingin diedit.

| File script | Output (di `Template_agath/gambar/`) | Muncul di Bab 4 | Sumber data |
|---|---|---|---|
| `gambar_4_11_ilustrasi_respons.py` | `ilustrasi_respons_nn.png` | **Gambar 4.11** | `DATA UJI/uji_NN_uji1_16juni.csv` |
| `tabel_respons_nn_per_keran.py` | `respons_nn_keran.png` | **Tabel** respons per keran (`tab:respons-nn-keran-grid`) | `DATA UJI/uji_NN_uji1_16juni.csv` |
| `gambar_4_13_respons_gangguan.py` | `respons_gangguan_nn.png` | **Gambar 4.13** | `DATA UJI/uji_NN_uji3_16juni.csv` |

> **Gambar 4.12** (`respons_setpoint_nn.png`, respons perubahan setpoint / Uji 2)
> **belum ada script plot-nya**. Analisis angkanya ada di
> `DATA UJI/_analisis_uji2_setpoint.py`. Plotnya dibuat menyusul setelah Uji 2.

## Cara pakai
```bash
cd "SCRIPT BAB 4"
python gambar_4_11_ilustrasi_respons.py
python gambar_4_13_respons_gangguan.py
python tabel_respons_nn_per_keran.py          # default uji1
python tabel_respons_nn_per_keran.py <file.csv>   # file uji lain
```
Path otomatis: baca CSV dari `../DATA UJI/`, simpan gambar ke `../Template_agath/gambar/`.

## ⚠️ Catatan tabel per-keran
Tabel `tab:respons-nn-keran-grid` di `4-pengujian-analisis.tex` memakai **10 gambar
terpisah** (`respons_tekanan_keran0..4.png`, `respons_duty_keran0..4.png`) yang
**saat ini sudah ada** di folder gambar. Namun `tabel_respons_nn_per_keran.py`
versi sekarang hanya menghasilkan **1 gambar gabungan** (`respons_nn_keran.png`),
sehingga **tidak meregenerasi 10 file tersebut**. Jika ingin mengubah gambar tabel
per-keran, minta saya menyesuaikan script agar mengeluarkan 10 file itu.

## Data uji & script analisis-angka
Ada di folder `../DATA UJI/` (CSV uji + `analyze_uji_nn.py`, `_analisis_uji2_setpoint.py`).
