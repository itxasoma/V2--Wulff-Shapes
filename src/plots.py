# Exercise B4: Wulff Shapes
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

# ── Load CSV ──────────────────────────────────────────────────────────────────

def load_csv(csv_path):
    """
    Returns a dict:  data[metal][surface] = (gfix, grelax, dgamma, grelax_eVA2)
    """
    data = {}
    with open(csv_path, newline='') as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            metal = row['Metal']
            surf  = row['Surface']
            gf    = float(row['gamma_fix_Jm2'])
            gr    = float(row['gamma_relax_Jm2'])
            dg    = float(row['delta_gamma_Jm2'])
            gr_ev = float(row['gamma_relax_eVA2'])
            data.setdefault(metal, {})[surf] = (gf, gr, dg, gr_ev)
    return data


def wulff_h(data, metals, surfaces):
    """Normalised h-values: h_hkl = gamma_hkl / gamma_min."""
    h = {}
    for metal in metals:
        if metal not in data:
            continue
        vals   = {s: data[metal][s][3] for s in surfaces if s in data[metal]}
        min_g  = min(vals.values())
        h[metal] = {s: v / min_g for s, v in vals.items()}
    return h


# ── Plot helpers ──────────────────────────────────────────────────────────────

def save(fig, name):
    out = os.path.join(FIG_DIR, name)
    fig.savefig(out, bbox_inches='tight')
    plt.close(fig)
    print(f'Saved  {os.path.relpath(out)}')


# ── Figure 1: gamma_fix vs gamma_relax ───────────────────────────────────────

def plot_surface_energies(data, metals, surfaces):
    surf_labels = [f'({s})' for s in surfaces]
    x = np.arange(len(surfaces))
    width = 0.18

    colors = {
        'Cu': {'fix': '#7bbcde', 'relax': '#1a5c8a'},
        'Pd': {'fix': '#f5c07a', 'relax': '#b86a10'},
    }
    offsets = {'Cu': -0.20, 'Pd': +0.20}

    fig, ax = plt.subplots(figsize=(7, 4.5))

    for metal in metals:
        if metal not in data:
            continue
        gfix   = [data[metal][s][0] for s in surfaces]
        grelax = [data[metal][s][1] for s in surfaces]
        off    = offsets[metal]

        ax.bar(x + off - width / 2, gfix,   width, color=colors[metal]['fix'],
               label=rf'{metal} $\gamma_{{\rm fix}}$',   edgecolor='white', linewidth=0.5)
        ax.bar(x + off + width / 2, grelax, width, color=colors[metal]['relax'],
               label=rf'{metal} $\gamma_{{\rm relax}}$', edgecolor='white', linewidth=0.5)

    ax.set_xticks(x)
    ax.set_xticklabels(surf_labels, fontsize=12)
    ax.set_xlabel('Surface', fontsize=12)
    ax.set_ylabel(r'$\gamma$  (J m$^{-2}$)', fontsize=12)
    ax.set_title(r'Surface energies of Cu and Pd', fontsize=13)
    ax.set_ylim(0, 2.0)
    ax.legend(ncol=2, fontsize=9, loc='upper right')
    ax.grid(axis='y', alpha=0.3)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    fig.tight_layout()
    save(fig, 'surface_energies_bar.pdf')


# ── Figure 2: Delta gamma ─────────────────────────────────────────────────────

def plot_relaxation(data, metals, surfaces):
    surf_labels = [f'({s})' for s in surfaces]
    x      = np.arange(len(surfaces))
    width  = 0.30
    colors = {'Cu': '#1a5c8a', 'Pd': '#b86a10'}
    offsets = {'Cu': -0.18, 'Pd': +0.18}

    fig, ax = plt.subplots(figsize=(7, 4.0))

    for metal in metals:
        if metal not in data:
            continue
        dg  = [data[metal][s][2] for s in surfaces]
        off = offsets[metal]
        ax.bar(x + off, dg, width, color=colors[metal],
               label=metal, edgecolor='white', linewidth=0.5)
        for xi, val in zip(x + off, dg):
            ax.text(xi, val - 0.002 if val < 0 else val + 0.001,
                    f'{val:+.4f}', ha='center', va='top' if val < 0 else 'bottom',
                    fontsize=8)

    ax.axhline(0, color='#555', linewidth=1.0, linestyle='--')
    ax.set_xticks(x)
    ax.set_xticklabels(surf_labels, fontsize=12)
    ax.set_xlabel('Surface', fontsize=12)
    ax.set_ylabel(r'$\Delta\gamma$  (J m$^{-2}$)', fontsize=12)
    ax.set_title(r'Relaxation energy $\Delta\gamma = \gamma_{\rm relax} - \gamma_{\rm fix}$',
                 fontsize=13)
    ax.legend(fontsize=10)
    ax.grid(axis='y', alpha=0.3)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    fig.tight_layout()
    save(fig, 'relaxation_energy_bar.pdf')


# ── Figure 3: Wulff h-values ──────────────────────────────────────────────────

def plot_wulff_h(data, metals, surfaces):
    h      = wulff_h(data, metals, surfaces)
    surf_labels = [f'({s})' for s in surfaces]
    x      = np.arange(len(surfaces))
    width  = 0.30
    colors = {'Cu': '#1a5c8a', 'Pd': '#b86a10'}
    offsets = {'Cu': -0.18, 'Pd': +0.18}

    fig, ax = plt.subplots(figsize=(7, 4.0))

    for metal in metals:
        if metal not in h:
            continue
        hvals = [h[metal].get(s, float('nan')) for s in surfaces]
        off   = offsets[metal]
        ax.bar(x + off, hvals, width, color=colors[metal],
               label=metal, edgecolor='white', linewidth=0.5)
        for xi, val in zip(x + off, hvals):
            ax.text(xi, val + 0.01, f'{val:.4f}',
                    ha='center', va='bottom', fontsize=8)

    ax.axhline(1.0, color='#555', linewidth=1.0, linestyle='--', label=r'$h_{111}=1$ (ref.)')
    ax.set_xticks(x)
    ax.set_xticklabels(surf_labels, fontsize=12)
    ax.set_xlabel('Surface', fontsize=12)
    ax.set_ylabel(r'Normalised Wulff $h$-value', fontsize=12)
    ax.set_title(r'Wulff $h$-values  ($h_{111} = 1$)', fontsize=13)
    ax.set_ylim(0, 1.6)
    ax.legend(fontsize=10)
    ax.grid(axis='y', alpha=0.3)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    fig.tight_layout()
    save(fig, 'wulff_h_values.pdf')


# ── Main ──────────────────────────────────────────────────────────────────────

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Generate Wulff-shape figures from surface_energies CSV')
    parser.add_argument('--csv', default=None,
                        help='Path to CSV (default: ../surface_energies_all.csv)')
    parser.add_argument('--metals',   nargs='+', default=['Cu', 'Pd'])
    parser.add_argument('--surfaces', nargs='+', default=['001', '011', '111'])
    args = parser.parse_args()

    if args.csv is None:
        args.csv = os.path.join(BASE_DIR, '../surface_energies_all.csv')

    csv_path = os.path.abspath(args.csv)
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f'CSV not found: {csv_path}\n'
                                f'Run  make run  first to generate it.')

    print(f'Reading  {csv_path}')
    data = load_csv(csv_path)

    plot_surface_energies(data, args.metals, args.surfaces)
    plot_relaxation(data, args.metals, args.surfaces)
    plot_wulff_h(data, args.metals, args.surfaces)
    print('Done.')
