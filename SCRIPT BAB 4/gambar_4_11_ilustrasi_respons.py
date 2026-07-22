"""Ilustrasi tunggal yang JELAS: bagaimana kontroler NN mencapai setpoint.
Contoh kasus 4 keran (tekanan naik dari ~0,24 ke 0,30 bar).
"""
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

here = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(here)            # folder BUKU TA_YOEL
UJI = os.path.join(ROOT, "DATA UJI")    # sumber data uji
GAMBAR = os.path.join(ROOT, "Template_agath", "gambar")  # output gambar
d = pd.read_csv(os.path.join(UJI, "uji_NN_uji1_16juni.csv"))
for c in ["pressure_bar", "duty_percent", "nn_mode", "valve_open_count"]:
    d[c] = pd.to_numeric(d[c], errors="coerce")
d["t"] = (pd.to_datetime(d["pc_timestamp"]) -
          pd.to_datetime(d["pc_timestamp"]).iloc[0]).dt.total_seconds()
s = d[(d["nn_mode"] == 1) & (d["valve_open_count"] == 4)].sort_values("t").reset_index(drop=True)
s["tr"] = s["t"] - s["t"].iloc[0]
SP = 0.30

fig, ax1 = plt.subplots(figsize=(11, 6))

# ---- Tekanan (sumbu kiri) ----
ax1.plot(s["tr"], s["pressure_bar"], color="#1f77b4", lw=2.2, label="Tekanan terukur")
ax1.axhline(SP, color="red", ls="--", lw=1.8, label="Setpoint (0,30 bar)")
ax1.axhspan(SP - 0.02, SP + 0.02, color="red", alpha=0.08)
ax1.set_xlabel("Waktu sejak kontroler NN diaktifkan (detik)", fontsize=11)
ax1.set_ylabel("Tekanan (bar)", color="#1f77b4", fontsize=11)
ax1.tick_params(axis="y", labelcolor="#1f77b4")
ax1.set_ylim(0.20, 0.34)
ax1.grid(alpha=0.3)

# ---- Duty (sumbu kanan) ----
ax2 = ax1.twinx()
ax2.plot(s["tr"], s["duty_percent"], color="#2ca02c", lw=2.0, ls="-",
         label="Duty cycle (aksi NN)")
ax2.set_ylabel("Duty cycle (%)", color="#2ca02c", fontsize=11)
ax2.tick_params(axis="y", labelcolor="#2ca02c")
ax2.set_ylim(75, 97)

# ---- anotasi yang menjelaskan ----
# titik awal
ax1.annotate("Tekanan awal di bawah setpoint",
             xy=(s["tr"].iloc[0], s["pressure_bar"].iloc[0]),
             xytext=(6, 0.215), fontsize=10,
             arrowprops=dict(arrowstyle="->", color="black"))
# aksi NN menaikkan duty
ax2.annotate("NN menaikkan duty cycle\nsecara bertahap",
             xy=(8, 86), xytext=(13, 79), fontsize=10, color="#1b6b1b",
             arrowprops=dict(arrowstyle="->", color="#2ca02c"))
# setpoint tercapai
i_set = (s["pressure_bar"] >= SP - 0.02).idxmax()
t_set = s["tr"].iloc[i_set]
ax1.axvline(t_set, color="gray", ls=":", lw=1.2)
ax1.annotate(f"Tekanan mencapai setpoint\n(settling time ≈ {t_set:.0f} detik)",
             xy=(t_set, SP), xytext=(t_set + 3, 0.247), fontsize=10,
             arrowprops=dict(arrowstyle="->", color="black"))

# legenda gabungan
l1, lab1 = ax1.get_legend_handles_labels()
l2, lab2 = ax2.get_legend_handles_labels()
ax1.legend(l1 + l2, lab1 + lab2, loc="lower right", fontsize=10)

plt.title("Ilustrasi Respons Kontroler NN Mencapai Setpoint (kondisi 4 keran)",
          fontsize=13, fontweight="bold")
plt.tight_layout()
out = os.path.join(GAMBAR, "ilustrasi_respons_nn.png")
plt.savefig(out, dpi=150, bbox_inches="tight")
print("Grafik disimpan:", out)
