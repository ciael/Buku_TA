"""Grafik respons kontroler NN - LAYOUT TABEL (tiap baris = 1 keran).
Kolom: [label keran] [Respons Tekanan] [Duty Cycle]. Plot jadi besar & jelas.
Pakai: python plot_respons_nn.py <file_uji_NN.csv>
Default: uji_NN_uji1_16juni.csv
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
fname = sys.argv[1] if len(sys.argv) > 1 else "uji_NN_uji1_16juni.csv"
d = pd.read_csv(os.path.join(UJI, fname))
for c in ["pressure_bar", "duty_percent", "nn_mode", "valve_open_count"]:
    d[c] = pd.to_numeric(d[c], errors="coerce")
d["t"] = (pd.to_datetime(d["pc_timestamp"]) -
          pd.to_datetime(d["pc_timestamp"]).iloc[0]).dt.total_seconds()
nn = d[d["nn_mode"] == 1].copy()
SP = 0.30
kerans = sorted(nn["valve_open_count"].dropna().unique())   # 0,1,2,3,4
n = len(kerans)
colors = {4: "#1f77b4", 3: "#ff7f0e", 2: "#2ca02c", 1: "#d62728", 0: "#9467bd"}

fig = plt.figure(figsize=(11, 1.9 * n + 0.8))
gs = fig.add_gridspec(n, 3, width_ratios=[0.14, 1, 1], hspace=0.55, wspace=0.22)

for r, v in enumerate(kerans):
    seg = nn[nn["valve_open_count"] == v].sort_values("t").copy()
    seg["tr"] = seg["t"] - seg["t"].iloc[0]
    c = colors.get(int(v), "k")

    # --- kolom 0: label keran ---
    axL = fig.add_subplot(gs[r, 0]); axL.axis("off")
    axL.text(0.5, 0.5, f"{int(v)}\nkeran", ha="center", va="center",
             fontsize=14, fontweight="bold", color=c)

    # --- kolom 1: tekanan ---
    axP = fig.add_subplot(gs[r, 1])
    axP.plot(seg["tr"], seg["pressure_bar"], color=c, lw=1.8)
    axP.axhline(SP, color="red", ls="--", lw=1.3)
    axP.axhspan(SP - 0.02, SP + 0.02, color="red", alpha=0.08)
    lo = min(seg["pressure_bar"].min(), SP - 0.02) - 0.02
    hi = max(seg["pressure_bar"].max(), SP + 0.02) + 0.02
    axP.set_ylim(lo, hi)
    axP.grid(alpha=0.3)
    axP.set_ylabel("bar", fontsize=9)

    # --- kolom 2: duty ---
    axD = fig.add_subplot(gs[r, 2])
    axD.plot(seg["tr"], seg["duty_percent"], color=c, lw=1.8)
    axD.axhline(95, color="gray", ls=":", lw=0.9, alpha=0.7)
    axD.axhline(70, color="gray", ls=":", lw=0.9, alpha=0.7)
    axD.set_ylim(67, 98)
    axD.grid(alpha=0.3)
    axD.set_ylabel("%", fontsize=9)

    if r == 0:
        axP.set_title("Respons Tekanan (bar)", fontsize=12, fontweight="bold")
        axD.set_title("Duty Cycle (%)", fontsize=12, fontweight="bold")
        axL.text(0.5, 1.25, "Keran", ha="center", va="bottom",
                 fontsize=12, fontweight="bold", transform=axL.transAxes)
    if r == n - 1:
        axP.set_xlabel("Waktu sejak NN aktif (s)", fontsize=9)
        axD.set_xlabel("Waktu sejak NN aktif (s)", fontsize=9)

fig.suptitle("Respons Kontroler NN Mencapai Setpoint 0,30 bar (per Jumlah Keran)",
             fontsize=13, fontweight="bold", y=0.995)
plt.tight_layout(rect=[0, 0, 1, 0.98])
out = os.path.join(GAMBAR, "respons_nn_keran.png")
plt.savefig(out, dpi=150, bbox_inches="tight")
print("Grafik disimpan:", out)
