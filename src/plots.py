# Exercise B2: Magic cluster building blocks
# Reads magic.dat and produces 4 plots exactly as defined in the assignment:
#   plot1.pdf – E_N = E(N)/N  vs  N^{-1/3}          (Exercise 1.1)
#   plot2.pdf – E_N = E(N)/N  vs  N                  (Exercise 1.2)
#   plot3.pdf – [E_N - (E_{N-1} + E_1)]  vs  N       (Exercise 1.3)
#   plot4.pdf – [2E_N - (E_{N-1} + E_{N+1})]  vs  N  (Exercise 1.4)
#
# Usage:  python3 plots.py

import numpy as np
import matplotlib.pyplot as plt
import os

BASE_DIR    = os.path.dirname(os.path.abspath(__file__))
RESULTS_DIR = os.path.join(BASE_DIR, '../results')
FIG_DIR     = os.path.join(BASE_DIR, '../figures')

style_file = os.path.join(BASE_DIR, 'lib/science.mplstyle')
if os.path.exists(style_file):
    plt.style.use(style_file)

os.makedirs(FIG_DIR, exist_ok=True)

DATA_FILE = os.path.join(RESULTS_DIR, 'magic.dat')


# ── Load data ────────────────────────────────────────────────────────────────
def load_data(filename):
    """
    Expected columns (space-separated, '#' lines are comments):
        N_MgO   N_atoms   E_total
    """
    data = np.genfromtxt(filename, comments='#')
    N    = data[:, 0].astype(int)
    E    = data[:, 2]
    return N, E


# ── Helper: find local minima ────────────────────────────────────────────────
def local_minima(x, y):
    """Return (x[i], y[i]) where y[i] < y[i-1] and y[i] < y[i+1]."""
    idx = [i for i in range(1, len(y) - 1)
           if y[i] < y[i - 1] and y[i] < y[i + 1]]
    return x[idx], y[idx]


# ── Plot 1: E_N = E(N)/N  vs  N^{-1/3}  (N = 2–19) ─────────────────────────
def plot1(N, E):
    mask = N >= 2
    x    = N[mask] ** (-1.0 / 3.0)
    y    = E[mask] / N[mask]

    fig, ax = plt.subplots()
    ax.plot(x, y, 'o-', ms=5, lw=1.2)

    ax.set_xlabel(r'$N^{-1/3}$')
    ax.set_ylabel(r'$E_N = E(N)/N$  (eV / MgO)')
    ax.set_title(r'Plot 1: Scalability of $({\rm MgO})_N$ clusters')
    ax.grid(True, alpha=0.3)
    fig.tight_layout()

    out = os.path.join(FIG_DIR, 'plot1.pdf')
    fig.savefig(out)
    plt.close(fig)
    print(f'Saved  {os.path.relpath(out)}')


# ── Plot 2: E_N = E(N)/N  vs  N  (N = 1–19) ─────────────────────────────────
def plot2(N, E):
    """Binding energy per formula unit vs cluster size."""
    y = E / N

    fig, ax = plt.subplots()
    ax.plot(N, y, 'o-', ms=5, lw=1.2)

    ax.set_xlabel(r'$N$ (MgO formula units)')
    ax.set_ylabel(r'$E_N = E(N)/N$  (eV / MgO)')
    ax.set_title(r'Plot 2: Binding energy per unit of $({\rm MgO})_N$')
    ax.grid(True, alpha=0.3)
    fig.tight_layout()

    out = os.path.join(FIG_DIR, 'plot2.pdf')
    fig.savefig(out)
    plt.close(fig)
    print(f'Saved  {os.path.relpath(out)}')


# ── Plot 3: [E_N - (E_{N-1} + E_1)]  vs  N  (N = 2–19) ─────────────────────
# ── Plot 3: [E_N - (E_{N-1} + E_1)]  vs  N  (N = 2–19) ─────────────────────
def plot3(N, E):
    E_dict = dict(zip(N, E))
    E1     = E_dict[1]

    Nsel, y = [], []
    for n in N:
        if n >= 2 and (n - 1) in E_dict:
            Nsel.append(n)
            y.append(E_dict[n] - (E_dict[n - 1] + E1))

    Nsel = np.array(Nsel)
    y    = np.array(y)

    x_min, y_min = local_minima(Nsel, y)

    fig, ax = plt.subplots()
    ax.plot(Nsel, y, 'o-', ms=5, lw=1.2,
            label=r'$E_N - (E_{N-1} + E_1)$')
    if len(x_min):
        ax.plot(x_min, y_min, 'v', ms=7, zorder=4, label='Minima (magic)')
        for xm, ym in zip(x_min, y_min):
            ax.annotate(f'$N={xm}$', xy=(xm, ym),
                        xytext=(0, -14), textcoords='offset points',
                        ha='center', fontsize=8)

    ypad = 0.08 * (y.max() - y.min())
    ax.set_ylim(y.min() - ypad, y.max() + ypad)

    ax.set_xlabel(r'$N$ (MgO formula units)')
    ax.set_ylabel(r'$E_N - (E_{N-1}+E_1)$  (eV)')
    ax.set_title(r'Plot 3: Incremental binding energy of $({\rm MgO})_N$')
    leg = ax.legend(loc='upper right')
    leg.get_frame().set_alpha(0.8)
    ax.grid(True, alpha=0.3)
    fig.tight_layout()

    out = os.path.join(FIG_DIR, 'plot3.pdf')
    fig.savefig(out)
    plt.close(fig)
    print(f'Saved  {os.path.relpath(out)}')
    if len(x_min):
        print('  Plot 3 minima:', ', '.join(f'N={n}' for n in x_min))


# ── Plot 4: [2E_N - (E_{N-1} + E_{N+1})]  vs  N  (N = 2–18) ────────────────
def plot4(N, E):
    """
    Second finite difference.
    y = 2*E(N) - E(N-1) - E(N+1)
    Minima = magic numbers. ylim fixed to (-3.5, 3.5).
    """
    E_dict = dict(zip(N, E))

    Nsel, y = [], []
    for n in N:
        if n >= 2 and n <= 18 and (n - 1) in E_dict and (n + 1) in E_dict:
            Nsel.append(n)
            y.append(2 * E_dict[n] - E_dict[n - 1] - E_dict[n + 1])

    Nsel = np.array(Nsel)
    y    = np.array(y)

    x_min, y_min = local_minima(Nsel, y)

    fig, ax = plt.subplots()
    ax.plot(Nsel, y, 'o-', ms=5, lw=1.2,
            label=r'$2E_N - (E_{N-1}+E_{N+1})$')
    if len(x_min):
        ax.plot(x_min, y_min, 'v', ms=7, zorder=4, label='Minima (magic)')
        for xm, ym in zip(x_min, y_min):
            ax.annotate(f'$N={xm}$', xy=(xm, ym),
                        xytext=(0, -14), textcoords='offset points',
                        ha='center', fontsize=8)

    ax.set_ylim(-3.5, 3.5)
    ax.axhline(0, color='grey', lw=0.8, ls='--')

    ax.set_xlabel(r'$N$ (MgO formula units)')
    ax.set_ylabel(r'$2E_N - (E_{N-1}+E_{N+1})$  (eV)')
    ax.set_title(r'Plot 4: Second finite difference of $({\rm MgO})_N$')
    ax.legend()
    ax.grid(True, alpha=0.3)
    fig.tight_layout()

    out = os.path.join(FIG_DIR, 'plot4.pdf')
    fig.savefig(out)
    plt.close(fig)
    print(f'Saved  {os.path.relpath(out)}')
    if len(x_min):
        print('  Plot 4 minima:', ', '.join(f'N={n}' for n in x_min))


# ── Main ─────────────────────────────────────────────────────────────────────
if __name__ == '__main__':
    if not os.path.exists(DATA_FILE):
        print(f'ERROR: {DATA_FILE} not found. Run `make run` first.')
        raise SystemExit(1)

    N, E = load_data(DATA_FILE)

    plot1(N, E)
    plot2(N, E)
    plot3(N, E)
    plot4(N, E)
    print('Done.')