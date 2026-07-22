"""
Analisis otomatis hasil UJI NN -> angka siap salin ke tabel Bab 4.

Cara pakai:
    python analyze_uji_nn.py            # baca semua uji_NN_*.csv di folder ini
    python analyze_uji_nn.py <folder>   # atau folder lain

Skrip mendeteksi fase secara OTOMATIS dari kolom yang berubah sendiri:
  - nn_mode (0->1)          -> NN mulai
  - setpoint_bar berubah    -> ganti setpoint (Uji 2)
  - valve_open_count berubah-> gangguan keran (Uji 3)
Tidak wajib menandai 'event' manual; kolom 'event' (bila ada) dipakai sebagai label tambahan.
"""
import os
import sys
import glob
import numpy as np
import pandas as pd

BAND_BAR   = 0.02   # pita "settle" di sekitar setpoint (bar)
HOLD_S     = 6.0    # tekanan harus bertahan di pita selama ini agar dianggap settle
MIN_SEG_S  = 5.0    # segmen lebih pendek dari ini diabaikan
GAP_S      = 4.0    # jeda waktu antar-baris -> dianggap segmen baru


def load_files(folder):
    files = sorted(glob.glob(os.path.join(folder, "uji_NN_*.csv")))
    if not files:
        print(f"[!] Tidak ada file 'uji_NN_*.csv' di: {folder}")
        sys.exit(1)
    frames = []
    for f in files:
        d = pd.read_csv(f)
        for c in ["pressure_bar", "duty_percent", "setpoint_bar",
                  "valve_open_count", "nn_mode"]:
            d[c] = pd.to_numeric(d.get(c), errors="coerce")
        d["t"] = (pd.to_datetime(d["pc_timestamp"]) -
                  pd.to_datetime(d["pc_timestamp"]).iloc[0]).dt.total_seconds()
        d["src"] = os.path.basename(f)
        # Tag uji dari nama file (mis. uji_NN_uji1_15juni.csv -> "uji1")
        name = os.path.basename(f).lower()
        d["uji"] = ("uji1" if "uji1" in name else "uji2" if "uji2" in name
                    else "uji3" if "uji3" in name else "")
        if "event" not in d.columns:
            d["event"] = ""
        frames.append(d)
        print(f"  - {os.path.basename(f)}: {len(d)} baris")
    return pd.concat(frames, ignore_index=True)


def segment(df):
    """Pecah menjadi segmen NN-aktif dengan (setpoint, keran) konstan."""
    df = df[df["nn_mode"] == 1].copy()
    df = df.dropna(subset=["pressure_bar", "setpoint_bar", "t"])
    df = df.sort_values(["src", "t"]).reset_index(drop=True)
    sp = df["setpoint_bar"].round(3)
    vv = df["valve_open_count"]
    change = (
        (sp != sp.shift()) |
        (vv != vv.shift()) |
        (df["src"] != df["src"].shift()) |
        (df["t"].diff() > GAP_S)
    )
    df["seg"] = change.cumsum()
    return df


def settling_time(ts, ps, setpoint, t_end):
    """Waktu (dtk relatif segmen) sampai tekanan masuk pita & bertahan hingga akhir."""
    for i in range(len(ts)):
        if t_end - ts[i] < min(HOLD_S, 3.0):
            break
        if np.all(np.abs(ps[i:] - setpoint) <= BAND_BAR):
            return ts[i] - ts[0]
    return np.nan


def analyze(df):
    rows = []
    prev = None
    for seg_id, seg in df.groupby("seg"):
        seg = seg.sort_values("t")
        t0, t_end = seg["t"].iloc[0], seg["t"].iloc[-1]
        if (t_end - t0) < MIN_SEG_S:
            continue
        setpoint = round(float(seg["setpoint_bar"].iloc[0]), 3)
        valve = seg["valve_open_count"].iloc[0]
        ps = seg["pressure_bar"].values
        ts = seg["t"].values
        du = seg["duty_percent"].values
        # nilai mantap = rata-rata 8 dtk terakhir
        tail = seg[seg["t"] >= t_end - 8.0]
        p_settle = float(tail["pressure_bar"].mean())
        d_settle = float(tail["duty_percent"].mean())
        p_start = float(ps[0])
        err_steady = setpoint - p_settle
        st = settling_time(ts, ps, setpoint, t_end)
        max_dev = float(np.max(np.abs(ps - setpoint)))

        # Pemicu segmen. 'break_before' = ada jeda NN-off / lompatan waktu
        # (mis. antar-keran Uji 1 di mana NN dimatikan). Jika TIDAK ada break
        # dan keran berubah -> itu GANGGUAN (Uji 3, NN tetap nyala).
        src = seg["src"].iloc[0]
        break_before = (prev is None or prev["src"] != src
                        or (t0 - prev["end_t"]) > GAP_S)
        if break_before:
            trig = "mulai-NN"
        elif valve != prev["valve"]:
            trig = f"gangguan {prev['valve']:.0f}->{valve:.0f}"
        elif setpoint != prev["setpoint"]:
            trig = "ganti-setpoint"
        else:
            trig = "mulai-NN"

        rows.append({
            "src": src, "uji": seg["uji"].iloc[0], "trig": trig,
            "keran": valve, "setpoint": setpoint,
            "p_start": p_start, "p_settle": p_settle,
            "d_start": float(du[0]), "d_settle": d_settle, "err_steady": err_steady,
            "settle_s": st, "max_dev": max_dev,
            "p_before": (prev["p_settle"] if (prev and not break_before) else np.nan),
            "dur": t_end - t0,
        })
        prev = {"src": src, "valve": valve, "setpoint": setpoint,
                "p_settle": p_settle, "end_t": t_end}
    return rows


def fmt(x, nd=3):
    return "-" if (x is None or (isinstance(x, float) and np.isnan(x))) else f"{x:.{nd}f}"


def report(rows):
    print("\n" + "=" * 92)
    print("RINGKASAN SEMUA SEGMEN (terdeteksi otomatis)")
    print("=" * 92)
    hdr = f"{'pemicu':<16}{'keran':>6}{'SP':>6}{'p_awal':>8}{'p_settle':>9}{'duty':>7}{'err':>8}{'settle_s':>9}{'dev_maks':>9}"
    print(hdr); print("-" * 92)
    for r in rows:
        print(f"{r['trig']:<16}{fmt(r['keran'],0):>6}{fmt(r['setpoint'],2):>6}"
              f"{fmt(r['p_start']):>8}{fmt(r['p_settle']):>9}{fmt(r['d_settle'],1):>7}"
              f"{fmt(r['err_steady']):>8}{fmt(r['settle_s'],1):>9}{fmt(r['max_dev']):>9}")

    # ---- UJI 1: tracking per keran (segmen 'mulai-NN') ----
    print("\n" + "=" * 92)
    print("UJI 1 -> Tabel tab:respons-nn-keran  (Keran | Duty awal | Duty settle | P settle | Error | Settling)")
    print("=" * 92)
    uji1 = [x for x in rows if x["uji"] == "uji1" or (x["uji"] == "" and x["trig"] == "mulai-NN")]
    for r in uji1:
        print(f"  {fmt(r['keran'],0)} & {fmt(r['d_start'],1)} & {fmt(r['d_settle'],1)} & "
              f"{fmt(r['p_settle'])} & {fmt(r['err_steady'])} & {fmt(r['settle_s'],1)} \\\\")

    # ---- UJI 2: setpoint tracking ----
    print("\n" + "=" * 92)
    print("UJI 2 -> Tabel tab:respons-setpoint  (Setpoint | P awal | P stabil | Settling | Error)")
    print("=" * 92)
    uji2 = [x for x in rows if x["uji"] == "uji2" or (x["uji"] == "" and x["trig"] == "ganti-setpoint")]
    for r in uji2:
        print(f"  {fmt(r['setpoint'],2)} & {fmt(r['p_start'])} & {fmt(r['p_settle'])} & "
              f"{fmt(r['settle_s'],1)} & {fmt(r['err_steady'])} \\\\")

    # ---- UJI 3: rejeksi gangguan ----
    print("\n" + "=" * 92)
    print("UJI 3 -> Tabel tab:respons-gangguan-beban  (Gangguan | P sebelum | P setelah | Waktu pulih)")
    print("=" * 92)
    uji3 = [x for x in rows if x["trig"].startswith("gangguan") and x["uji"] in ("", "uji3")]
    for r in uji3:
        print(f"  {r['trig']} & {fmt(r['p_before'])} & {fmt(r['p_settle'])} & "
              f"{fmt(r['settle_s'],1)} \\\\   (deviasi maks {fmt(r['max_dev'])} bar)")
    print()


if __name__ == "__main__":
    folder = sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(os.path.abspath(__file__))
    print(f"Folder: {folder}")
    df = load_files(folder)
    seg = segment(df)
    rows = analyze(seg)
    if not rows:
        print("[!] Tidak ada segmen NN valid (cek nn_mode==1 & durasi).")
    else:
        report(rows)
