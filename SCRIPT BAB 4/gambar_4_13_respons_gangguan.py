"""Grafik respons rejeksi gangguan (Uji 3) - timeline kontinu.
Pakai: python plot_gangguan_nn.py <file_uji_NN_uji3.csv>
Default: uji_NN_uji3_16juni.csv
"""
import os
import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

here = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(here)            # folder BUKU TA_YOEL
UJI = os.path.join(ROOT, "DATA UJI")    # sumber data uji
GAMBAR = os.path.join(ROOT, "Template_agath", "gambar")  # output gambar
fname = sys.argv[1] if len(sys.argv) > 1 else "uji_NN_uji3_16juni.csv"
d = pd.read_csv(os.path.join(UJI, fname))
for c in ["pressure_bar", "duty_percent", "nn_mode", "valve_open_count"]:
    d[c] = pd.to_numeric(d[c], errors="coerce")
d["t"] = (pd.to_datetime(d["pc_timestamp"]) -
          pd.to_datetime(d["pc_timestamp"]).iloc[0]).dt.total_seconds()
d = d[d["nn_mode"] == 1].reset_index(drop=True)
d["t"] -= d["t"].iloc[0]

SP = 0.30
v = d["valve_open_count"].values
t = d["t"].values
trans = [i for i in range(1, len(v)) if v[i] != v[i - 1]]

fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 7), sharex=True)

# --- Tekanan ---
ax1.plot(d["t"], d["pressure_bar"], color="#1f77b4", lw=1.5, label="Tekanan")
ax1.axhline(SP, color="r", ls="--", lw=1.4, label="Setpoint 0,30 bar")
ax1.axhspan(SP - 0.02, SP + 0.02, color="r", alpha=0.08)
ax1.set_ylabel("Tekanan (bar)")
ax1.set_title("Respons Rejeksi Gangguan Kontroler NN (perubahan jumlah keran)")
ax1.grid(alpha=0.3)

# --- Duty ---
ax2.plot(d["t"], d["duty_percent"], color="#2ca02c", lw=1.5)
ax2.axhline(95, color="gray", ls=":", lw=1, alpha=0.7)
ax2.axhline(70, color="gray", ls=":", lw=1, alpha=0.7)
ax2.text(1, 95.5, "plafon 95%", color="gray", fontsize=8)
ax2.text(1, 70.5, "lantai 70%", color="gray", fontsize=8)
ax2.set_ylabel("Duty cycle (%)")
ax2.set_xlabel("Waktu sejak NN aktif (detik)")
ax2.grid(alpha=0.3)

# --- garis & label gangguan ---
ymax = d["pressure_bar"].max()
for i in trans:
    a, b = int(v[i - 1]), int(v[i])
    arah = "buka" if b > a else "tutup"
    for ax in (ax1, ax2):
        ax.axvline(t[i], color="purple", ls="--", lw=1, alpha=0.6)
    ax1.text(t[i] + 0.5, ymax * 0.99, f"{a}$\\to${b}\n({arah})",
             color="purple", fontsize=8, va="top")

ax1.legend(loc="upper left", fontsize=9)
plt.tight_layout()
out = os.path.join(GAMBAR, "respons_gangguan_nn.png")
plt.savefig(out, dpi=150, bbox_inches="tight")
print("Grafik disimpan:", out)
