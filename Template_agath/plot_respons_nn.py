import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

plt.rcParams.update({
    "font.family": "serif",
    "font.size": 11,
})

CSV_PATH = r"E:\SEMESTER 8\TA\BUKU TA_YOEL\uji_NN_uji1_16juni.csv"
df = pd.read_csv(CSV_PATH)

conditions = ["0 keran stabil", "1 keran stabil", "2 keran stabil",
              "3 keran stabil", "4 keran stabil"]
setpoint = 0.3

rows = []
for cond in conditions:
    g = df[df["valve_state_label"] == cond]
    if len(g) == 0:
        continue
    n = g["valve_open_count"].iloc[0]
    p = g["pressure_bar"]
    d = g["nn_duty_percent"]
    steady_p = float(np.mean(p.tail(15))) if len(p) >= 15 else float(np.mean(p))
    steady_d = float(np.mean(d.tail(15))) if len(d) >= 15 else float(np.mean(d))
    error = steady_p - setpoint
    rows.append((n, steady_p, error, steady_d, len(g)))

# ============ LaTeX Table ============
latex = r"""\begin{table}[H]
\centering
\caption{Respons Kontroler NN Mencapai \emph{Setpoint} 0,30~bar per Jumlah Keran}
\label{tab:respons-nn-per-keran}
\begin{tabularx}{\linewidth}{|c|>{\centering\arraybackslash}X|>{\centering\arraybackslash}X|>{\centering\arraybackslash}X|>{\centering\arraybackslash}X|}
\hline
\textbf{Keran} &
\textbf{Tekanan \emph{Steady} (bar)} &
\textbf{Error (bar)} &
\textbf{NN \emph{Duty Cycle} (\%)} &
\textbf{Jumlah Data} \\
\hline"""
for n, sp, err, sd, cnt in rows:
    latex += f"\n{n} & {sp:.3f} & {err:+.3f} & {sd:.1f} & {cnt} \\\\"
    latex += "\n\\hline"

latex += r"""
\end{tabularx}
\end{table}"""

print("=== LATEX TABLE ===")
print(latex)

# ============ Bar Chart ============
keran = [r[0] for r in rows]
steady_p = [r[1] for r in rows]
steady_d = [r[3] for r in rows]
errors = [r[2] for r in rows]

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

colors_p = ['#d7191c' if abs(e) > 0.02 else '#2c7bb6' for e in errors]
bars1 = ax1.bar(keran, steady_p, color=colors_p, edgecolor='black', width=0.5)
ax1.axhline(y=setpoint, color='red', linestyle='--', linewidth=1.5, label=f'Setpoint {setpoint} bar')
ax1.set_xlabel('Jumlah Keran')
ax1.set_ylabel('Tekanan Steady (bar)')
ax1.set_title(f'Tekanan Steady vs Setpoint {setpoint} bar')
ax1.set_xticks(keran)
ax1.legend()
ax1.grid(True, alpha=0.3, axis='y')
for bar, val, err in zip(bars1, steady_p, errors):
    ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.005,
             f'{val:.3f}', ha='center', va='bottom', fontsize=9)

bars2 = ax2.bar(keran, steady_d, color='#d95f02', edgecolor='black', width=0.5)
ax2.set_xlabel('Jumlah Keran')
ax2.set_ylabel('NN Duty Cycle (%)')
ax2.set_title('NN Duty Cycle Steady per Jumlah Keran')
ax2.set_xticks(keran)
ax2.grid(True, alpha=0.3, axis='y')
for bar, val in zip(bars2, steady_d):
    ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.3,
             f'{val:.1f}%', ha='center', va='bottom', fontsize=9)

plt.tight_layout()
plt.savefig("gambar/respons_nn_per_keran.png", dpi=200, bbox_inches='tight')
plt.close()
print("\nSaved: gambar/respons_nn_per_keran.png")
