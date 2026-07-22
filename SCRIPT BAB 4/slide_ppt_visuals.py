"""
slide_ppt_visuals.py
====================
Membuat gambar-gambar visualisasi berkualitas presentasi (16:9, font besar,
anotasi jelas) untuk slide PowerPoint sidang TA.

Menghasilkan 4 kelompok gambar:
  SLIDE 1  Pengujian Model Neural Network
             - slide1_arsitektur_mlp.png     (diagram MLP 3-4-1)
             - slide1_evaluasi_model.png      (metrik + distribusi target)
  SLIDE 2  Pengujian Respon Tekanan 1 (per jumlah keran 0-4)
             - slide2_keran_bar.png           (tekanan steady per keran)
             - slide2_keran_timeline.png      (timeline tekanan+duty disambung)
  SLIDE 3  Pengujian Respon Tekanan 2 (pelacakan setpoint)
             - slide3_setpoint.png
  SLIDE 4  Pengujian Respon Tekanan 3 (rejeksi gangguan)
             - slide4_gangguan.png

Sumber data (folder DATA UJI):
  uji_NN_uji1_16juni.csv  -> per keran
  uji_NN_uji2_16juni.csv  -> setpoint
  uji_NN_uji3_16juni.csv  -> gangguan

Output: folder  GAMBAR_PPT/  di root proyek.
Jalankan:  python slide_ppt_visuals.py
"""
import matplotlib
matplotlib.use("Agg")
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Circle, FancyArrowPatch, Rectangle

# ----------------------------------------------------------------------------
# Path
# ----------------------------------------------------------------------------
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
UJI = os.path.join(ROOT, "DATA UJI")
OUT = os.path.join(ROOT, "GAMBAR_PPT")
os.makedirs(OUT, exist_ok=True)

# ----------------------------------------------------------------------------
# Gaya global (bernuansa slide: sans-serif, font besar, bersih)
# ----------------------------------------------------------------------------
plt.rcParams.update({
    "font.family": "Calibri",
    "font.size": 15,
    "axes.titlesize": 18,
    "axes.titleweight": "bold",
    "axes.labelsize": 15,
    "axes.labelweight": "bold",
    "axes.edgecolor": "#444444",
    "axes.linewidth": 1.1,
    "axes.grid": True,
    "grid.linestyle": "--",
    "grid.alpha": 0.35,
    "legend.fontsize": 13,
    "legend.frameon": True,
    "legend.framealpha": 0.9,
    "figure.dpi": 120,
})

# Palet warna konsisten (biru ITS + aksen)
C_PRESS = "#1f6feb"    # tekanan
C_DUTY = "#e8710a"     # duty cycle
C_SP = "#2ca02c"       # setpoint
C_BAD = "#d62728"      # kondisi saturasi/gagal
C_BAND = "#2ca02c"     # pita toleransi
SP = 0.30              # setpoint utama
BAND = 0.02            # +/- pita toleransi

KERAN_COL = {0: "#d62728", 1: "#1f6feb", 2: "#1f9d55",
             3: "#e8710a", 4: "#7b2ff7"}


def load(fname):
    d = pd.read_csv(os.path.join(UJI, fname))
    for c in ["pressure_bar", "duty_percent", "valve_open_count",
              "nn_mode", "setpoint_bar"]:
        d[c] = pd.to_numeric(d.get(c), errors="coerce")
    d["t"] = (pd.to_datetime(d["pc_timestamp"]) -
              pd.to_datetime(d["pc_timestamp"]).iloc[0]).dt.total_seconds()
    return d


def save(fig, name):
    path = os.path.join(OUT, name)
    fig.savefig(path, dpi=200, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print("  [OK]", name)


# ============================================================================
# SLIDE 1a — Diagram Arsitektur MLP 3-4-1
# ============================================================================
def slide1_arsitektur():
    fig, ax = plt.subplots(figsize=(12, 6.4))
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 8)
    ax.axis("off")

    # posisi layer
    x_in, x_hid, x_out = 2.2, 6.0, 9.8
    inputs = ["error\n(e)", "Δerror\n(Δe)", "duty\n(d)"]
    y_in = [6.0, 4.0, 2.0]
    y_hid = [6.6, 4.9, 3.2, 1.5]
    y_out = [4.0]

    def node(x, y, r, fc, ec):
        ax.add_patch(Circle((x, y), r, fc=fc, ec=ec, lw=2.2, zorder=3))

    # koneksi input->hidden
    for yi in y_in:
        for yh in y_hid:
            ax.plot([x_in, x_hid], [yi, yh], color="#c7ccd1", lw=1.1, zorder=1)
    # koneksi hidden->output
    for yh in y_hid:
        ax.plot([x_hid, x_out], [yh, y_out[0]], color="#c7ccd1", lw=1.1, zorder=1)

    # node input
    for yi, lab in zip(y_in, inputs):
        node(x_in, yi, 0.55, "#dbeafe", C_PRESS)
        ax.text(x_in, yi, lab, ha="center", va="center",
                fontsize=13, fontweight="bold", zorder=4)
    # node hidden
    for j, yh in enumerate(y_hid, 1):
        node(x_hid, yh, 0.5, "#fff2df", C_DUTY)
        ax.text(x_hid, yh, f"h{j}", ha="center", va="center",
                fontsize=13, fontweight="bold", zorder=4)
    # node output
    node(x_out, y_out[0], 0.6, "#dcfce7", C_SP)
    ax.text(x_out, y_out[0], "Δduty", ha="center", va="center",
            fontsize=13, fontweight="bold", zorder=4)

    # judul kolom
    ax.text(x_in, 7.2, "INPUT (3)", ha="center", fontsize=15,
            fontweight="bold", color=C_PRESS)
    ax.text(x_hid, 7.6, "HIDDEN (4)", ha="center", fontsize=15,
            fontweight="bold", color=C_DUTY)
    ax.text(x_hid, 7.05, "aktivasi: tanh", ha="center", fontsize=12, color="#555")
    ax.text(x_out, 7.2, "OUTPUT (1)", ha="center", fontsize=15,
            fontweight="bold", color=C_SP)
    ax.text(x_out, 6.65, "aktivasi: linear", ha="center", fontsize=12, color="#555")

    # panah keluaran & interpretasi
    ax.add_patch(FancyArrowPatch((x_out + 0.6, 4.0), (11.4, 4.0),
                 arrowstyle="-|>", mutation_scale=22, lw=2, color="#333"))
    ax.text(11.5, 4.0, "koreksi\nduty cycle", ha="left", va="center",
            fontsize=12, fontweight="bold")

    ax.set_title("Arsitektur Neural Network  —  MLP 3-4-1 (Behavior Cloning)",
                 fontsize=19, pad=14)
    save(fig, "slide1_arsitektur_mlp.png")


# ============================================================================
# SLIDE 1b — Evaluasi model: metrik + distribusi target
# ============================================================================
def slide1_evaluasi():
    fig = plt.figure(figsize=(12, 6.0))
    gs = fig.add_gridspec(1, 2, width_ratios=[1.05, 1.0], wspace=0.28)

    # -- kiri: kartu metrik --
    axm = fig.add_subplot(gs[0, 0])
    axm.axis("off")
    axm.set_title("Kinerja Model pada Data Uji", fontsize=18, pad=10)

    cards = [("R²", "0,915", "Koefisien determinasi", C_SP),
             ("RMSE", "0,463", "Root Mean Square Error", C_PRESS),
             ("MAE", "0,329", "Mean Absolute Error", C_DUTY)]
    for i, (k, v, sub, col) in enumerate(cards):
        y = 0.78 - i * 0.30
        box = FancyBboxPatch((0.06, y - 0.11), 0.88, 0.22,
                             boxstyle="round,pad=0.02,rounding_size=0.03",
                             fc="white", ec=col, lw=2.4,
                             transform=axm.transAxes)
        axm.add_patch(box)
        axm.text(0.14, y, k, transform=axm.transAxes, fontsize=22,
                 fontweight="bold", color=col, va="center")
        axm.text(0.50, y, v, transform=axm.transAxes, fontsize=26,
                 fontweight="bold", va="center")
        axm.text(0.50, y - 0.075, sub, transform=axm.transAxes, fontsize=11,
                 color="#555", va="center")

    # -- kanan: distribusi target Δduty --
    axd = fig.add_subplot(gs[0, 1])
    labels = ["Naik\n(Δ>0)", "Tahan\n(Δ=0)", "Turun\n(Δ<0)"]
    vals = [161, 201, 91]
    cols = [C_SP, "#9aa0a6", C_BAD]
    bars = axd.bar(labels, vals, color=cols, edgecolor="black", lw=1.2, width=0.65)
    axd.set_ylabel("Jumlah data")
    axd.set_title("Distribusi Keputusan Δduty\n(453 data latih)", fontsize=16)
    axd.set_ylim(0, max(vals) * 1.20)
    for b, v in zip(bars, vals):
        axd.text(b.get_x() + b.get_width() / 2, v + 6, str(v),
                 ha="center", fontsize=15, fontweight="bold")
    axd.grid(axis="x", visible=False)

    fig.suptitle("Evaluasi Model Neural Network", fontsize=20, fontweight="bold",
                 y=1.02)
    save(fig, "slide1_evaluasi_model.png")


# ============================================================================
# SLIDE 2a — Tekanan steady per jumlah keran (bar chart)
# ============================================================================
def slide2_keran_bar():
    d = load("uji_NN_uji1_16juni.csv")
    nn = d[d["nn_mode"] == 1]
    kerans, press = [], []
    for k in sorted(nn["valve_open_count"].dropna().unique()):
        seg = nn[nn["valve_open_count"] == k].sort_values("t")
        tail = seg[seg["t"] >= seg["t"].max() - 8]
        kerans.append(int(k))
        press.append(tail["pressure_bar"].mean())

    fig, ax = plt.subplots(figsize=(11, 6.2))
    cols = [C_BAD if abs(p - SP) > 0.05 else C_PRESS for p in press]
    bars = ax.bar([str(k) for k in kerans], press, color=cols,
                  edgecolor="black", lw=1.3, width=0.62, zorder=3)
    ax.axhline(SP, color=C_SP, ls="--", lw=2.2, zorder=2,
               label=f"Setpoint {SP:.2f} bar")
    ax.axhspan(SP - BAND, SP + BAND, color=C_BAND, alpha=0.12, zorder=1)

    for b, p in zip(bars, press):
        ax.text(b.get_x() + b.get_width() / 2, p + 0.008, f"{p:.3f}",
                ha="center", fontsize=15, fontweight="bold")

    ax.set_xlabel("Jumlah keran terbuka")
    ax.set_ylabel("Tekanan steady (bar)")
    ax.set_ylim(0, max(press) * 1.18)
    ax.set_title("Tekanan Steady Kontroler NN pada Tiap Kondisi Keran",
                 fontsize=18, pad=12)
    ax.legend(loc="upper right")
    ax.grid(axis="x", visible=False)

    # anotasi kondisi saturasi (keran 0)
    if kerans and kerans[0] == 0:
        ax.annotate("Saturasi:\ntekanan minimum pompa\n> setpoint",
                    xy=(0, press[0]), xytext=(0.55, press[0] + 0.03),
                    fontsize=12, color=C_BAD, fontweight="bold",
                    ha="left", va="center",
                    arrowprops=dict(arrowstyle="->", color=C_BAD, lw=1.8))
    save(fig, "slide2_keran_bar.png")


# ============================================================================
# SLIDE 2b — Timeline tekanan + duty (segmen NN disambung) per keran
# ============================================================================
def slide2_keran_timeline():
    d = load("uji_NN_uji1_16juni.csv")
    nn = d[d["nn_mode"] == 1].copy()

    # sambung segmen per keran secara berurutan (4->0 sesuai urutan waktu)
    segs = []
    tcur = 0.0
    order = []
    for k in sorted(nn["valve_open_count"].dropna().unique(), reverse=True):
        seg = nn[nn["valve_open_count"] == k].sort_values("t").copy()
        if seg.empty:
            continue
        seg["tt"] = seg["t"] - seg["t"].iloc[0] + tcur
        segs.append((int(k), seg))
        order.append((int(k), tcur, seg["tt"].iloc[-1]))
        tcur = seg["tt"].iloc[-1] + 2
    if not segs:
        return
    allseg = pd.concat([s for _, s in segs])

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12.5, 7.0), sharex=True,
                                   gridspec_kw={"height_ratios": [1.15, 1]})

    ax1.plot(allseg["tt"], allseg["pressure_bar"], color=C_PRESS, lw=2.2,
             label="Tekanan")
    ax1.axhline(SP, color=C_SP, ls="--", lw=2, label=f"Setpoint {SP:.2f} bar")
    ax1.axhspan(SP - BAND, SP + BAND, color=C_BAND, alpha=0.12)
    ax1.set_ylabel("Tekanan (bar)")
    # beri ruang atas untuk label segmen agar tidak bertabrakan
    pmin, pmax = allseg["pressure_bar"].min(), allseg["pressure_bar"].max()
    ax1.set_ylim(pmin - 0.02, pmax + (pmax - pmin) * 0.24)
    ax1.legend(loc="lower right", ncol=2)
    ax1.set_title("Respon Kontroler NN — Semua Kondisi Keran (segmen disambung)",
                  fontsize=18, pad=10)

    ax2.plot(allseg["tt"], allseg["duty_percent"], color=C_DUTY, lw=2.2,
             label="Duty cycle")
    ax2.axhline(95, color="gray", ls=":", lw=1.2)
    ax2.axhline(70, color="gray", ls=":", lw=1.2)
    ax2.set_ylabel("Duty cycle (%)")
    ax2.set_xlabel("Waktu (detik, segmen NN disambung)")
    ax2.set_ylim(66, 99)
    ax2.legend(loc="upper right")

    # pemisah & label segmen keran (di pita atas ax1)
    ytxt = pmax + (pmax - pmin) * 0.15
    for k, t0, t1 in order:
        for ax in (ax1, ax2):
            ax.axvline(t1 + 1, color="#999", ls="-", lw=0.8, alpha=0.6)
        ax1.text((t0 + t1) / 2, ytxt, f"{k} keran",
                 ha="center", va="center", fontsize=12, fontweight="bold",
                 color=KERAN_COL.get(k, "#333"),
                 bbox=dict(boxstyle="round,pad=0.2", fc="white",
                           ec=KERAN_COL.get(k, "#333"), alpha=0.9))
    save(fig, "slide2_keran_timeline.png")


# ============================================================================
# SLIDE 3 — Pelacakan setpoint (uji 2)
# ============================================================================
def slide3_setpoint():
    d = load("uji_NN_uji2_16juni.csv")
    nn = d[d["nn_mode"] == 1].copy()
    nn["tt"] = nn["t"] - nn["t"].iloc[0]
    # haluskan garis setpoint: buang spike transien 1-2 sampel (median window 5)
    nn["sp_clean"] = (nn["setpoint_bar"].rolling(9, center=True, min_periods=1)
                      .median())

    fig, ax = plt.subplots(figsize=(12.5, 6.4))
    ax.plot(nn["tt"], nn["sp_clean"], color=C_BAD, ls="--", lw=2.4,
            label="Setpoint", zorder=3)
    ax.plot(nn["tt"], nn["pressure_bar"], color=C_PRESS, lw=2.2,
            label="Tekanan aktual", zorder=4)

    # pita toleransi mengikuti setpoint
    ax.fill_between(nn["tt"], nn["sp_clean"] - BAND, nn["sp_clean"] + BAND,
                    color=C_BAND, alpha=0.12, zorder=1)

    ax.set_xlabel("Waktu sejak NN aktif (detik)")
    ax.set_ylabel("Tekanan / setpoint (bar)")
    ax.set_title("Pelacakan Perubahan Setpoint oleh Kontroler NN",
                 fontsize=18, pad=12)
    ax.legend(loc="upper left", ncol=2)

    # label satu nilai per plateau setpoint (abaikan transien singkat)
    sp = nn["sp_clean"].round(2).values
    tt = nn["tt"].values
    # run-length encoding plateau
    bounds = [0] + list(np.where(sp[1:] != sp[:-1])[0] + 1) + [len(sp)]
    for a, b in zip(bounds[:-1], bounds[1:]):
        dur = tt[b - 1] - tt[a]
        if dur < 6:            # buang plateau transien (<6 dtk)
            continue
        xc = (tt[a] + tt[b - 1]) / 2
        val = sp[a]
        ax.text(xc, val + 0.012, f"{val:.2f} bar", ha="center", va="bottom",
                fontsize=13, color=C_BAD, fontweight="bold",
                bbox=dict(boxstyle="round,pad=0.15", fc="white",
                          ec=C_BAD, alpha=0.85))
    save(fig, "slide3_setpoint.png")


# ============================================================================
# SLIDE 4 — Rejeksi gangguan (uji 3)
# ============================================================================
def slide4_gangguan():
    d = load("uji_NN_uji3_16juni.csv")
    nn = d[d["nn_mode"] == 1].copy().reset_index(drop=True)
    nn["tt"] = nn["t"] - nn["t"].iloc[0]

    v = nn["valve_open_count"].values
    t = nn["tt"].values
    trans = [i for i in range(1, len(v)) if v[i] != v[i - 1]]

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12.5, 7.0), sharex=True,
                                   gridspec_kw={"height_ratios": [1.15, 1]})

    ax1.plot(nn["tt"], nn["pressure_bar"], color=C_PRESS, lw=2.2, label="Tekanan")
    ax1.axhline(SP, color=C_SP, ls="--", lw=2, label=f"Setpoint {SP:.2f} bar")
    ax1.axhspan(SP - BAND, SP + BAND, color=C_BAND, alpha=0.12)
    ax1.set_ylabel("Tekanan (bar)")
    ax1.legend(loc="upper left", ncol=2)
    ax1.set_title("Rejeksi Gangguan — Keran Dibuka/Ditutup Mendadak Saat NN Aktif",
                  fontsize=18, pad=10)

    ax2.plot(nn["tt"], nn["duty_percent"], color=C_DUTY, lw=2.2, label="Duty cycle")
    ax2.axhline(95, color="gray", ls=":", lw=1.2)
    ax2.axhline(70, color="gray", ls=":", lw=1.2)
    ax2.set_ylabel("Duty cycle (%)")
    ax2.set_xlabel("Waktu sejak NN aktif (detik)")
    ax2.set_ylim(66, 99)
    ax2.legend(loc="upper left")

    ymax = nn["pressure_bar"].max()
    for i in trans:
        a, b = int(v[i - 1]), int(v[i])
        for ax in (ax1, ax2):
            ax.axvline(t[i], color="#7b2ff7", ls="--", lw=1.6, alpha=0.7)
        ax1.annotate(f"{a}→{b} keran", xy=(t[i], ymax * 0.98),
                     xytext=(t[i] + 1.5, ymax * 0.99),
                     fontsize=12, color="#7b2ff7", fontweight="bold", va="top")
    save(fig, "slide4_gangguan.png")


if __name__ == "__main__":
    print("Menghasilkan gambar presentasi ->", OUT)
    slide1_arsitektur()
    slide1_evaluasi()
    slide2_keran_bar()
    slide2_keran_timeline()
    slide3_setpoint()
    slide4_gangguan()
    print("\nSelesai. Semua gambar ada di:", OUT)
