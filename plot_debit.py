# Plot debit total vs jumlah keran: kendali NN vs open-loop duty 90%
import matplotlib.pyplot as plt

keran = [1, 2, 3, 4]
debit_nn = [94.14, 103.43, 215.73, 278.80]      # mL/s
debit_ol = [64.67, 83.33, 193.87, 226.13]       # mL/s

fig, ax = plt.subplots(figsize=(6.4, 4.0))

ax.plot(keran, debit_nn, marker='o', linewidth=2, color='#1f4e79',
        label='Kendali NN (setpoint 0,30 bar)')
ax.plot(keran, debit_ol, marker='s', linewidth=2, color='#c0392b',
        linestyle='--', label='Open-loop (duty 90%)')

# anotasi nilai
for x, y in zip(keran, debit_nn):
    ax.annotate(f'{y:.1f}', (x, y), textcoords='offset points',
                xytext=(0, 8), ha='center', fontsize=8, color='#1f4e79')
for x, y in zip(keran, debit_ol):
    ax.annotate(f'{y:.1f}', (x, y), textcoords='offset points',
                xytext=(0, -12), ha='center', fontsize=8, color='#c0392b')

ax.set_xlabel('Jumlah Keran Terbuka')
ax.set_ylabel('Debit Total (mL/s)')
ax.set_xticks(keran)
ax.set_ylim(0, 320)
ax.grid(True, linestyle=':', alpha=0.6)
ax.legend(loc='upper left', fontsize=9, frameon=True)

fig.tight_layout()
out = 'Template_agath/gambar/debit_vs_keran.png'
fig.savefig(out, dpi=200)
print('saved:', out)
