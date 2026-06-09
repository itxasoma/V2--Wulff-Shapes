# Exercise V2: Wulff Shapes
# Reads surface_energies_all.csv produced by wulff_surface_energies.py
# and generates publication-quality figures for the report.
#
# Generates:
#   figures/surface_energies_bar.pdf   : gamma_fix vs gamma_relax (grouped bar)
#   figures/relaxation_energy_bar.pdf  : Delta_gamma = gamma_relax - gamma_fix
#   figures/wulff_h_values.pdf         : normalised Wulff h-values
#
# Usage:
#   python3 src/plots.py
#   python3 src/plots.py --csv /path/to/surface_energies_all.csv

import os
import argparse
import csv
import numpy as np
import matplotlib.pyplot as plt

# ── Paths ─────────────────────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FIG_DIR  = os.path.join(BASE_DIR, '../figures')
os.makedirs(FIG_DIR, exist_ok=True)

style_file = os.path.join(BASE_DIR, 'lib/science.mplstyle')
if os.path.exists(style_file):
    plt.style.use(style_file)

EV_TO_JM2 = 16.0218

# Colours from the cycler (science.mplstyle):
#   blue #0C5DA5, green #00B945, orange #FF9500, red #FF2C00
# Cu -> blue family; Pd -> orange family
_CU_LIGHT = '#5B9FD4'   # lightened blue  (gamma_fix)
_CU_DARK  = '#0C5DA5'   # cycler blue     (gamma_relax / bar)
_PD_LIGHT = '#FFB84D'   # lightened orange (gamma_fix)
_PD_DARK  = '#FF9500'   # cycler orange   (gamma_relax / bar)

COLORS  = {
    'Cu': {'fix': _CU_LIGHT, 'relax': _CU_DARK,  'bar': _CU_DARK},
    'Pd': {'fix': _PD_LIGHT, 'relax': _PD_DARK,  'bar': _PD_DARK},
}
OFFSETS = {'Cu': -0.18, 'Pd': +0.18}
WIDTH   = 0.30

# ── Helpers ───────────────────────────────────────────────────────────────────

def load_csv(csv_path):
    data = {}
    with open(csv_path, newline='') as fh:
        for row in csv.DictReader(fh):
            metal = row['Metal']
            surf  = row['Surface']
            data.setdefault(metal, {})[surf] = (
                float(row['gamma_fix_Jm2']),
                float(row['gamma_relax_Jm2']),
                float(row['delta_gamma_Jm2']),
                float(row['gamma_relax_eVA2']),
            )
    return data

def wulff_h(data, metals, surfaces):
    h = {}
    for metal in metals:
        if metal not in data:
            continue
        vals  = {s: data[metal][s][3] for s in surfaces if s in data[metal]}
        min_g = min(vals.values())
        h[metal] = {s: v / min_g for s, v in vals.items()}
    return h

def save(fig, name):
    out = os.path.join(FIG_DIR, name)
    fig.savefig(out)               # bbox/padding handled by savefig.bbox in style
    plt.close(fig)
    print(f'Saved  {os.path.relpath(out)}')

def _style_ax(ax):
    # top/right spines off; ticks-in and minor visible are set by the style
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

# ── Figure 1: gamma_fix vs gamma_relax ───────────────────────────────────────

def plot_surface_energies(data, metals, surfaces):
    surf_labels = [r'$(%s)$' % s for s in surfaces]
    x = np.arange(len(surfaces))

    fig, ax = plt.subplots()

    for metal in metals:
        if metal not in data:
            continue
        gfix   = [data[metal][s][0] for s in surfaces]
        grelax = [data[metal][s][1] for s in surfaces]
        off    = OFFSETS[metal]
        half   = WIDTH / 2
        ax.bar(x + off - half / 2, gfix,   half, color=COLORS[metal]['fix'],
               label=r'%s $\gamma_{\rm fix}$'   % metal, edgecolor='white', linewidth=0.4)
        ax.bar(x + off + half / 2, grelax, half, color=COLORS[metal]['relax'],
               label=r'%s $\gamma_{\rm relax}$' % metal, edgecolor='white', linewidth=0.4)

    ax.set_xticks(x)
    ax.set_xticklabels(surf_labels)
    ax.set_xlabel('Surface')
    ax.set_ylabel(r'$\gamma$ (J\,m$^{-2}$)')
    ax.set_ylim(0, 2.0)
    ax.legend(ncol=2, loc='upper right')
    _style_ax(ax)
    save(fig, 'surface_energies_bar.pdf')

# ── Figure 2: Delta gamma ─────────────────────────────────────────────────────

def plot_relaxation(data, metals, surfaces):
    surf_labels = [r'$(%s)$' % s for s in surfaces]
    x = np.arange(len(surfaces))

    fig, ax = plt.subplots()

    for metal in metals:
        if metal not in data:
            continue
        dg  = [data[metal][s][2] for s in surfaces]
        off = OFFSETS[metal]
        ax.bar(x + off, dg, WIDTH, color=COLORS[metal]['bar'],
               label=metal, edgecolor='white', linewidth=0.4)
        for xi, val in zip(x + off, dg):
            va = 'top' if val < 0 else 'bottom'
            dy = -0.002 if val < 0 else +0.001
            ax.text(xi, val + dy, '%+.4f' % val, ha='center', va=va, fontsize=6)

    ax.axhline(0, color='0.4', linewidth=0.8, linestyle='--')
    ax.set_xticks(x)
    ax.set_xticklabels(surf_labels)
    ax.set_xlabel('Surface')
    ax.set_ylabel(r'$\Delta\gamma$ (J\,m$^{-2}$)')
    ax.legend()
    _style_ax(ax)
    save(fig, 'relaxation_energy_bar.pdf')

# ── Figure 3: Wulff h-values ──────────────────────────────────────────────────

def plot_wulff_h(data, metals, surfaces):
    h = wulff_h(data, metals, surfaces)
    surf_labels = [r'$(%s)$' % s for s in surfaces]
    x = np.arange(len(surfaces))

    fig, ax = plt.subplots()

    for metal in metals:
        if metal not in h:
            continue
        hvals = [h[metal].get(s, float('nan')) for s in surfaces]
        off   = OFFSETS[metal]
        ax.bar(x + off, hvals, WIDTH, color=COLORS[metal]['bar'],
               label=metal, edgecolor='white', linewidth=0.4)
        for xi, val in zip(x + off, hvals):
            ax.text(xi, val + 0.01, '%.4f' % val, ha='center', va='bottom', fontsize=6)

    ax.axhline(1.0, color='0.4', linewidth=0.8, linestyle='--',
               label=r'$h_{111}=1$ (ref.)')
    ax.set_xticks(x)
    ax.set_xticklabels(surf_labels)
    ax.set_xlabel('Surface')
    ax.set_ylabel(r'Normalised Wulff $h$-value')
    ax.set_ylim(0, 1.6)
    ax.legend()
    _style_ax(ax)
    save(fig, 'wulff_h_values.pdf')

# ── Main ──────────────────────────────────────────────────────────────────────

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Generate Wulff-shape figures from surface_energies CSV')
    parser.add_argument('--csv',      default=None)
    parser.add_argument('--metals',   nargs='+', default=['Cu', 'Pd'])
    parser.add_argument('--surfaces', nargs='+', default=['001', '011', '111'])
    args = parser.parse_args()

    if args.csv is None:
        args.csv = os.path.join(BASE_DIR, '../surface_energies_all.csv')

    csv_path = os.path.abspath(args.csv)
    if not os.path.exists(csv_path):
        raise FileNotFoundError(
            f'CSV not found: {csv_path}\nRun  make run  first to generate it.')

    print(f'Reading  {csv_path}')
    data = load_csv(csv_path)

    plot_surface_energies(data, args.metals, args.surfaces)
    plot_relaxation(data, args.metals, args.surfaces)
    plot_wulff_h(data, args.metals, args.surfaces)
    print('Done.')