# -*- coding: utf-8 -*-
"""
Gambar respons tekanan pompa untuk PROSIDING (Uji 1, 2, 3).

Setiap figur dibuat PERSIS 8 cm (lebar) x 5 cm (tinggi) dengan font dalam satuan
point dan DPI tinggi, sehingga saat disisipkan di Word pada lebar 8 cm tulisannya
tajam & terbaca. JUDUL sengaja tidak dipasang di gambar -> tulis caption di Word.

Sumber data: folder DATA UJI (induk folder ini).
Output PNG: folder ini (PROSIDING).

Jalankan:
    python gambar_prosiding.py
"""
import os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator

# ---------------------------------------------------------------- lokasi
HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.dirname(HERE)            # ...\DATA UJI
OUT  = HERE                              # ...\DATA UJI\PROSIDING
F1 = os.path.join(DATA, "uji_NN_uji1_16juni.csv")
F2 = os.path.join(DATA, "uji_NN_uji2_16juni.csv")
F3 = os.path.join(DATA, "uji_NN_uji3_16juni.csv")

# ---------------------------------------------------------------- ukuran & gaya
CM = 1 / 2.54
FIG_W, FIG_H = 8 * CM, 5 * CM            # 8 cm x 5 cm (lebar x tinggi)
DPI = 400
SP = 0.30                                # setpoint utama (bar)
BAND = 0.02                              # pita toleransi (bar)

plt.rcParams.update({
    "font.family": "serif",
    "font.size": 7.0,
    "axes.labelsize": 7.5,
    "axes.titlesize": 7.5,
    "xtick.labelsize": 6.5,
    "ytick.labelsize": 6.5,
    "legend.fontsize": 6.0,
    "axes.linewidth": 0.7,
    "lines.linewidth": 1.3,
    "xtick.major.size": 2.5,
    "ytick.major.size": 2.5,
    "xtick.major.width": 0.6,
    "ytick.major.width": 0.6,
    "legend.handlelength": 1.4,
    "legend.handletextpad": 0.4,
    "legend.borderpad": 0.3,
    "legend.labelspacing": 0.25,
    "legend.columnspacing": 0.8,
    "savefig.dpi": DPI,
    "figure.dpi": DPI,
})

# warna konsisten per jumlah keran
KCOL = {0: "#d7191c", 1: "#fdae61", 2: "#1a9850", 3: "#2c7bb6", 4: "#5e3c99"}


def _load(path):
    d = pd.read_csv(path)
    for c in ["pressure_bar", "duty_percent", "nn_duty_percent", "nn_mode",
              "valve_open_count", "setpoint_bar", "episode_id"]:
        if c in d.columns:
            d[c] = pd.to_numeric(d[c], errors="coerce")
    d["t_abs"] = (pd.to_datetime(d["pc_timestamp"])
                  - pd.to_datetime(d["pc_timestamp"]).iloc[0]).dt.total_seconds()
    return d


def _duty(d):
    """duty yang diterapkan: pakai duty_percent, fallback nn_duty_percent."""
    if "duty_percent" in d and d["duty_percent"].notna().any():
        return d["duty_percent"]
    return d["nn_duty_percent"]


def _save(fig, name):
    # JANGAN pakai bbox_inches='tight' -> agar ukuran fisik tetap 8x5 cm.
    p = os.path.join(OUT, name)
    fig.savefig(p, dpi=DPI, facecolor="white")
    plt.close(fig)
    print("  ->", name)


# ======================================================================
# UJI 1 — Respons tekanan per jumlah keran (tiap segmen NN disejajarkan t=0)
# ======================================================================
def fig_uji1():
    d = _load(F1)
    fig, ax = plt.subplots(figsize=(FIG_W, FIG_H), constrained_layout=True)
    ax.axhspan(SP - BAND, SP + BAND, color="#1a9850", alpha=0.10, zorder=0)
    ax.axhline(SP, color="#1a9850", ls="--", lw=1.0, zorder=1)
    for n in [0, 1, 2, 3, 4]:
        g = d[(d["valve_state_label"] == f"{n} keran stabil")
              & (d["nn_mode"] == 1)].copy()
        if len(g) == 0:
            continue
        t = g["t_abs"].values - g["t_abs"].values[0]
        ax.plot(t, g["pressure_bar"].values, color=KCOL[n], lw=1.2,
                label=f"{n} keran", zorder=3)
    ax.set_xlabel("Waktu sejak NN aktif (detik)")
    ax.set_ylabel("Tekanan (bar)")
    ax.set_ylim(0.15, 0.62)
    ax.yaxis.set_major_locator(MultipleLocator(0.1))
    ax.grid(True, alpha=0.25, lw=0.4)
    ax.legend(loc="upper right", ncol=2, frameon=True, framealpha=0.9,
              title="Setpoint 0,30 bar", title_fontsize=6.0)
    _save(fig, "uji1_respons_tekanan_per_keran.png")


# ======================================================================
# UJI 1 (ringkasan) — tekanan steady & error per jumlah keran (bar chart)
# ======================================================================
def fig_uji1_steady():
    d = _load(F1)
    ns, ps = [], []
    for n in [0, 1, 2, 3, 4]:
        g = d[(d["valve_state_label"] == f"{n} keran stabil")
              & (d["nn_mode"] == 1)]
        if len(g) == 0:
            continue
        ns.append(n)
        ps.append(float(np.mean(g["pressure_bar"].values[-12:])))
    fig, ax = plt.subplots(figsize=(FIG_W, FIG_H), constrained_layout=True)
    col = ["#2c7bb6" if abs(p - SP) <= BAND else "#d7191c" for p in ps]
    bars = ax.bar(ns, ps, width=0.62, color=col, edgecolor="black", lw=0.6)
    ax.axhline(SP, color="black", ls="--", lw=1.0)
    ax.axhspan(SP - BAND, SP + BAND, color="black", alpha=0.07)
    ax.set_xlabel("Jumlah keran terbuka")
    ax.set_ylabel("Tekanan steady (bar)")
    ax.set_ylim(0, 0.60)
    ax.set_xticks(ns)
    ax.grid(True, axis="y", alpha=0.25, lw=0.4)
    for b, p in zip(bars, ps):
        ax.text(b.get_x() + b.get_width() / 2, p + 0.012,
                f"{p:.3f}".replace(".", ","), ha="center", va="bottom",
                fontsize=5.8)
    ax.text(0.97, 0.95, "garis putus = setpoint 0,30 bar", transform=ax.transAxes,
            ha="right", va="top", fontsize=5.5, style="italic")
    _save(fig, "uji1_ringkasan_steady.png")


# ======================================================================
# UJI 2 — Penjejakan perubahan setpoint (tekanan mengikuti tangga setpoint)
# ======================================================================
def fig_uji2():
    d = _load(F2)
    g = d[d["nn_mode"] == 1].copy().reset_index(drop=True)
    t = g["t_abs"].values - g["t_abs"].values[0]
    p = g["pressure_bar"].values
    sp = g["setpoint_bar"].values
    fig, ax = plt.subplots(figsize=(FIG_W, FIG_H), constrained_layout=True)
    # pita toleransi mengikuti setpoint yang berlaku
    ax.fill_between(t, sp - BAND, sp + BAND, color="#1a9850", alpha=0.10,
                    step="post", zorder=0)
    ax.step(t, sp, where="post", color="#d7191c", ls="--", lw=1.1,
            label="Setpoint", zorder=2)
    ax.plot(t, p, color="#2c7bb6", lw=1.2, label="Tekanan aktual", zorder=3)
    ax.set_xlabel("Waktu sejak NN aktif (detik)")
    ax.set_ylabel("Tekanan / setpoint (bar)")
    ax.set_ylim(0.15, 0.45)
    ax.yaxis.set_major_locator(MultipleLocator(0.05))
    ax.grid(True, alpha=0.25, lw=0.4)
    ax.legend(loc="upper left", ncol=2, frameon=True, framealpha=0.9)
    _save(fig, "uji2_penjejakan_setpoint.png")


# ======================================================================
# UJI 3 — Rejeksi gangguan perubahan jumlah keran (tekanan pulih ke setpoint)
# ======================================================================
def fig_uji3():
    d = _load(F3)
    g = d[d["nn_mode"] == 1].copy().reset_index(drop=True)
    t = g["t_abs"].values - g["t_abs"].values[0]
    p = g["pressure_bar"].values
    v = g["valve_open_count"].values
    trans = [i for i in range(1, len(v)) if v[i] != v[i - 1]]
    fig, ax = plt.subplots(figsize=(FIG_W, FIG_H), constrained_layout=True)
    ax.axhspan(SP - BAND, SP + BAND, color="#1a9850", alpha=0.10, zorder=0)
    ax.axhline(SP, color="#1a9850", ls="--", lw=1.0, label="Setpoint 0,30 bar",
               zorder=1)
    ax.plot(t, p, color="#2c7bb6", lw=1.2, label="Tekanan", zorder=3)
    ymax = float(np.nanmax(p))
    for i in trans:
        a, b = int(v[i - 1]), int(v[i])
        arah = "buka" if b > a else "tutup"
        ax.axvline(t[i], color="#7b3294", ls="--", lw=0.8, alpha=0.6, zorder=2)
        ax.annotate(f"{a}→{b}\n({arah})", xy=(t[i], ymax),
                    xytext=(t[i] + 1.5, ymax), color="#7b3294", fontsize=5.3,
                    va="top", ha="left")
    ax.set_xlabel("Waktu sejak NN aktif (detik)")
    ax.set_ylabel("Tekanan (bar)")
    ax.set_ylim(0.18, ymax + 0.04)
    ax.grid(True, alpha=0.25, lw=0.4)
    ax.legend(loc="lower right", frameon=True, framealpha=0.9)
    _save(fig, "uji3_rejeksi_gangguan.png")


# ======================================================================
#  VERSI GABUNGAN: TEKANAN + DUTY CYCLE DALAM SATU GRAFIK (twin-axis)
#  (gambar di atas TIDAK diubah; ini file baru terpisah)
# ======================================================================
CP = "#2c7bb6"   # warna tekanan (kiri)
CD = "#d95f02"   # warna duty (kanan)


def _twin_axes(ax):
    axd = ax.twinx()
    ax.set_ylabel("Tekanan (bar)", color=CP)
    axd.set_ylabel("Duty cycle (%)", color=CD)
    ax.tick_params(axis="y", labelcolor=CP)
    axd.tick_params(axis="y", labelcolor=CD)
    return axd


# ---- UJI 1: tekanan + duty, timeline kontinu (segmen NN disambung) ----
def fig_uji1_duty():
    d = _load(F1)
    g = d[d["nn_mode"] == 1].copy().reset_index(drop=True)
    dty_all = _duty(g).values
    # bangun waktu kontinu: tiap segmen keran dirangkai + jeda kecil antar-segmen
    lbl = g["valve_state_label"].values
    seg_id = (lbl != np.roll(lbl, 1)).cumsum()
    t = np.zeros(len(g))
    offset, GAP = 0.0, 3.0
    bounds = []           # (t_batas, keran_baru)
    for sid in np.unique(seg_id):
        m = seg_id == sid
        loc = g.loc[m, "t_abs"].values
        loc = loc - loc[0]
        t[m] = loc + offset
        n = int(str(lbl[m.argmax()]).split()[0])
        bounds.append((offset, n))
        offset += loc[-1] + GAP
    p = g["pressure_bar"].values

    fig, ax = plt.subplots(figsize=(FIG_W, FIG_H), constrained_layout=True)
    axd = _twin_axes(ax)
    ax.axhspan(SP - BAND, SP + BAND, color="#1a9850", alpha=0.10, zorder=0)
    ax.axhline(SP, color="#1a9850", ls="--", lw=0.9, zorder=1)
    ld, = axd.plot(t, dty_all, color=CD, lw=1.0, alpha=0.9, label="Duty cycle")
    lp, = ax.plot(t, p, color=CP, lw=1.2, label="Tekanan", zorder=3)
    # batas & label jumlah keran
    for tb, n in bounds[1:]:
        ax.axvline(tb - GAP / 2, color="#999", ls=":", lw=0.6, zorder=1)
    for tb, n in bounds:
        ax.text(tb + 1, 0.605, f"{n} kr", fontsize=5.2, color="#444", va="top")
    ax.set_xlabel("Waktu (detik, segmen NN disambung)")
    ax.set_ylim(0.15, 0.62)
    ax.yaxis.set_major_locator(MultipleLocator(0.1))
    axd.set_ylim(66, 98)
    ax.grid(True, alpha=0.22, lw=0.4)
    ax.legend([lp, ld], ["Tekanan", "Duty cycle"], loc="center right",
              frameon=True, framealpha=0.9, fontsize=5.8)
    ax.set_zorder(axd.get_zorder() + 1)
    ax.patch.set_visible(False)
    _save(fig, "uji1_tekanan_duty.png")


# ---- UJI 2: tekanan + setpoint + duty ----
def fig_uji2_duty():
    d = _load(F2)
    g = d[d["nn_mode"] == 1].copy().reset_index(drop=True)
    t = g["t_abs"].values - g["t_abs"].values[0]
    p = g["pressure_bar"].values
    sp = g["setpoint_bar"].values
    dty = _duty(g).values

    fig, ax = plt.subplots(figsize=(FIG_W, FIG_H), constrained_layout=True)
    axd = _twin_axes(ax)
    ax.fill_between(t, sp - BAND, sp + BAND, color="#1a9850", alpha=0.10,
                    step="post", zorder=0)
    ls, = ax.step(t, sp, where="post", color="#d7191c", ls="--", lw=1.0,
                  label="Setpoint", zorder=2)
    ld, = axd.plot(t, dty, color=CD, lw=1.0, alpha=0.9, label="Duty cycle")
    lp, = ax.plot(t, p, color=CP, lw=1.2, label="Tekanan", zorder=3)
    ax.set_xlabel("Waktu sejak NN aktif (detik)")
    ax.set_ylim(0.15, 0.45)
    ax.yaxis.set_major_locator(MultipleLocator(0.05))
    axd.set_ylim(70, 96)
    ax.grid(True, alpha=0.22, lw=0.4)
    ax.legend([lp, ls, ld], ["Tekanan", "Setpoint", "Duty cycle"],
              loc="upper left", ncol=3, frameon=True, framealpha=0.9,
              fontsize=5.5, columnspacing=0.6)
    ax.set_zorder(axd.get_zorder() + 1)
    ax.patch.set_visible(False)
    _save(fig, "uji2_tekanan_duty.png")


# ---- UJI 3: tekanan + duty + penanda gangguan ----
def fig_uji3_duty():
    d = _load(F3)
    g = d[d["nn_mode"] == 1].copy().reset_index(drop=True)
    t = g["t_abs"].values - g["t_abs"].values[0]
    p = g["pressure_bar"].values
    dty = _duty(g).values
    v = g["valve_open_count"].values
    trans = [i for i in range(1, len(v)) if v[i] != v[i - 1]]

    fig, ax = plt.subplots(figsize=(FIG_W, FIG_H), constrained_layout=True)
    axd = _twin_axes(ax)
    ax.axhspan(SP - BAND, SP + BAND, color="#1a9850", alpha=0.10, zorder=0)
    lsp = ax.axhline(SP, color="#1a9850", ls="--", lw=0.9, zorder=1,
                     label="Setpoint 0,30 bar")
    ld, = axd.plot(t, dty, color=CD, lw=1.0, alpha=0.9, label="Duty cycle")
    lp, = ax.plot(t, p, color=CP, lw=1.2, label="Tekanan", zorder=3)
    ymax = float(np.nanmax(p))
    for i in trans:
        a, b = int(v[i - 1]), int(v[i])
        ax.axvline(t[i], color="#7b3294", ls="--", lw=0.7, alpha=0.55, zorder=2)
        ax.text(t[i] + 1.5, ymax, f"{a}→{b}", color="#7b3294",
                fontsize=5.2, va="top", ha="left")
    ax.set_xlabel("Waktu sejak NN aktif (detik)")
    ax.set_ylim(0.18, ymax + 0.05)
    axd.set_ylim(68, 98)
    ax.grid(True, alpha=0.22, lw=0.4)
    ax.legend([lp, lsp, ld], ["Tekanan", "Setpoint", "Duty cycle"],
              loc="upper left", ncol=3, frameon=True, framealpha=0.9,
              fontsize=5.5, columnspacing=0.6)
    ax.set_zorder(axd.get_zorder() + 1)
    ax.patch.set_visible(False)
    _save(fig, "uji3_tekanan_duty.png")


if __name__ == "__main__":
    print("Membuat gambar prosiding (8 cm x 5 cm, DPI %d):" % DPI)
    fig_uji1()
    fig_uji1_steady()
    fig_uji2()
    fig_uji3()
    # versi gabungan tekanan + duty cycle (satu grafik)
    fig_uji1_duty()
    fig_uji2_duty()
    fig_uji3_duty()
    print("Selesai. Semua PNG ada di:", OUT)
