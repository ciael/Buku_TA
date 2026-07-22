import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

plt.rcParams.update({
    "font.family": "serif",
    "font.size": 11,
    "axes.labelsize": 12,
    "axes.titlesize": 13,
    "legend.fontsize": 10,
})

df = pd.read_csv(r"E:\SEMESTER 8\TA\BUKU TA_YOEL\uji_NN_uji1_16juni.csv")

conditions = ["0 keran stabil", "1 keran stabil", "2 keran stabil",
              "3 keran stabil", "4 keran stabil"]

for cond in conditions:
    g = df[df["valve_state_label"] == cond].copy()
    if len(g) == 0:
        continue

    t_rel = (g["stm32_ms"] - g["stm32_ms"].iloc[0]) / 1000.0
    p = g["pressure_bar"].values
    duty = g["nn_duty_percent"].values
    setpoint = g["setpoint_bar"].iloc[0]
    n_keran = g["valve_open_count"].iloc[0]

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 6),
                                    gridspec_kw={'height_ratios': [3, 2]},
                                    sharex=True)

    # Tekanan — zoom ke sekitar setpoint
    ax1.plot(t_rel, p, linewidth=1.5, color='#2c7bb6')
    ax1.axhline(y=setpoint, color='red', linestyle='--', linewidth=1.2,
                label=f'Setpoint {setpoint} bar')
    steady = np.mean(p[-15:]) if len(p) >= 15 else np.mean(p)
    error = steady - setpoint
    ax1.fill_between(t_rel, setpoint, p, alpha=0.10, color='blue')

    # Zoom y-axis around setpoint
    y_min = max(0.10, min(p.min(), setpoint) - 0.08)
    y_max = min(0.65, max(p.max(), setpoint) + 0.10)
    ax1.set_ylim(y_min, y_max)

    ax1.set_ylabel("Tekanan (bar)")
    ax1.set_title(f"Respons Tekanan — {cond} (Setpoint {setpoint} bar)")
    ax1.legend(loc='upper right')
    ax1.grid(True, alpha=0.3)
    ax1.text(0.02, 0.96,
             f"Steady: {steady:.3f} bar  |  Error: {error:+.3f} bar",
             transform=ax1.transAxes, fontsize=10, va='top',
             bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.85))

    # Duty cycle NN — zoom ke rentang relevan
    ax2.plot(t_rel, duty, linewidth=1.5, color='#d95f02')
    ax2.set_ylabel("NN Duty Cycle (%)")
    ax2.set_xlabel("Waktu (detik)")
    d_min, d_max = duty.min(), duty.max()
    margin = max(5, (d_max - d_min) * 0.15)
    ax2.set_ylim(max(0, d_min - margin), min(100, d_max + margin))
    ax2.grid(True, alpha=0.3)
    ax2.text(0.02, 0.93, f"Mean duty: {np.mean(duty):.1f}%",
             transform=ax2.transAxes, fontsize=10, va='top',
             bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.85))

    plt.tight_layout()
    fname = f"gambar/respons_{n_keran}_keran.png"
    plt.savefig(fname, dpi=200, bbox_inches='tight')
    plt.close()
    print(f"Saved: {fname}")

# Print summary
print("\n=== Ringkasan ===")
for cond in conditions:
    g = df[df["valve_state_label"] == cond]
    if len(g) > 0:
        p = g["pressure_bar"]
        steady = p.tail(15).mean()
        print(f"{cond:20s} | N={len(g):4d} | Steady={steady:.4f} bar "
              f"| Error={steady-0.3:+.4f} bar | Duty={g['nn_duty_percent'].mean():.1f}%")
