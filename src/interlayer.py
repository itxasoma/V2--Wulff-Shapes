# Exercise V2: Wulff Shapes -- Bonus Track 1
# Computes interlayer relaxation distances for all studied surfaces.
#
# For each surface the first two interlayer spacings are extracted from:
#   POSCAR.vasp  (unrelaxed slab)  -> d12_fix,   d23_fix
#   CONTCAR.vasp (relaxed slab)    -> d12_relax, d23_relax
# and compared to the ideal bulk interlayer spacing d_bulk.
#
# Relative relaxation:
#   Delta_d12 (%) = (d12_relax - d12_fix) / d_bulk * 100
#
# Generates:
#   interlayer_relaxation.csv   : full numerical table
#   figures/interlayer_bar.pdf  : bar chart of Delta_d12 and Delta_d23
#
# Usage (from src/):
#   python3 interlayer.py
#   python3 interlayer.py --root ../Wulff-Data

import os
import argparse
import csv
import numpy as np
import matplotlib.pyplot as plt

# -- Paths --------------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FIG_DIR  = os.path.join(BASE_DIR, '../figures')
os.makedirs(FIG_DIR, exist_ok=True)

style_file = os.path.join(BASE_DIR, 'lib/science.mplstyle')
if os.path.exists(style_file):
    plt.style.use(style_file)

METALS   = ['Cu', 'Pd']
SURFACES = ['001', '011', '111']

COLORS  = {'Cu': '#0C5DA5', 'Pd': '#FF9500'}
OFFSETS = {'Cu': -0.18, 'Pd': +0.18}
WIDTH   = 0.30

# -- POSCAR parser ------------------------------------------------------------

def read_poscar(path):
    with open(path) as fh:
        lines = fh.readlines()
    scale   = float(lines[1].strip())
    lattice = np.array([[float(x) for x in lines[i].split()] for i in [2, 3, 4]]) * scale
    # VASP 5 has an element-symbol line; detect by trying int conversion of line 5
    try:
        counts = [int(x) for x in lines[5].split()]
        coord_line = 7
    except ValueError:
        counts = [int(x) for x in lines[6].split()]
        coord_line = 8
    n_atoms = sum(counts)
    # Skip optional 'Selective dynamics' line
    if lines[coord_line].strip().lower().startswith('s'):
        coord_line += 1
    mode = lines[coord_line].strip().lower()
    cartesian = mode.startswith('c') or mode.startswith('k')
    coord_line += 1
    coords = np.array([[float(x) for x in lines[i].split()[:3]]
                       for i in range(coord_line, coord_line + n_atoms)])
    if not cartesian:
        coords = coords @ lattice
    return lattice, coords


def bulk_interlayer(lattice, surface):
    a = np.linalg.norm(lattice[0])
    if surface == '001': return a / 2.0
    if surface == '011': return a / (2.0 * np.sqrt(2))
    if surface == '111': return a / np.sqrt(3)
    raise ValueError(f'Unknown surface: {surface}')


def layer_spacings(coords, n=3):
    z = np.sort(coords[:, 2])
    layers, current = [], [z[0]]
    for zi in z[1:]:
        if zi - current[-1] < 0.5:
            current.append(zi)
        else:
            layers.append(np.mean(current))
            current = [zi]
    layers.append(np.mean(current))
    return [layers[i+1] - layers[i] for i in range(min(n - 1, len(layers) - 1))]


# -- Main computation ---------------------------------------------------------

def compute(root):
    rows = []
    for metal in METALS:
        bp = os.path.join(root, metal, 'Bulk', 'POSCAR.vasp')
        if not os.path.exists(bp):
            bp = os.path.join(root, metal, 'Bulk', 'CONTCAR.vasp')
        bulk_lat, _ = read_poscar(bp)

        for surf in SURFACES:
            sdir    = os.path.join(root, metal, 'Surfaces', surf)
            lat_f,  c_f = read_poscar(os.path.join(sdir, 'POSCAR.vasp'))
            lat_r,  c_r = read_poscar(os.path.join(sdir, 'CONTCAR.vasp'))

            d_bulk  = bulk_interlayer(bulk_lat, surf)
            sp_f    = layer_spacings(c_f)
            sp_r    = layer_spacings(c_r)

            d12_f,  d23_f  = sp_f[0], sp_f[1]  if len(sp_f)  > 1 else None
            d12_r,  d23_r  = sp_r[0], sp_r[1]  if len(sp_r)  > 1 else None

            dd12 = (d12_r - d12_f) / d_bulk * 100.0
            dd23 = (d23_r - d23_f) / d_bulk * 100.0 if d23_f is not None else None

            sign = 'contraction' if dd12 < 0 else 'expansion'
            print(f'{metal} ({surf})  d_bulk={d_bulk:.4f} A  '
                  f'd12: {d12_f:.4f}->{d12_r:.4f} A  '
                  f'Delta_d12={dd12:+.2f}%  ({sign})')

            rows.append({
                'Metal':        metal,
                'Surface':      surf,
                'd_bulk_A':     round(d_bulk, 4),
                'd12_fix_A':    round(d12_f,  4),
                'd12_relax_A':  round(d12_r,  4),
                'Delta_d12_pct': round(dd12,  3),
                'd23_fix_A':    round(d23_f,  4) if d23_f  is not None else '',
                'd23_relax_A':  round(d23_r,  4) if d23_r  is not None else '',
                'Delta_d23_pct': round(dd23,  3) if dd23   is not None else '',
            })
    return rows


# -- CSV ----------------------------------------------------------------------

def write_csv(rows, out):
    fields = ['Metal', 'Surface', 'd_bulk_A',
              'd12_fix_A', 'd12_relax_A', 'Delta_d12_pct',
              'd23_fix_A', 'd23_relax_A', 'Delta_d23_pct']
    with open(out, 'w', newline='') as fh:
        w = csv.DictWriter(fh, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)
    print(f'Saved  {os.path.relpath(out)}')


# -- Figure -------------------------------------------------------------------

def plot(rows):
    surf_labels = [r'$(%s)$' % s for s in SURFACES]
    x = np.arange(len(SURFACES))

    fig, axes = plt.subplots(1, 2, sharey=False)

    for ax, key, ylabel in zip(
            axes,
            ['Delta_d12_pct', 'Delta_d23_pct'],
            [r'$\Delta d_{12}$ (\%)', r'$\Delta d_{23}$ (\%)']):

        for metal in METALS:
            vals = []
            for surf in SURFACES:
                row = next(r for r in rows if r['Metal'] == metal and r['Surface'] == surf)
                v = row[key]
                vals.append(float(v) if v != '' else 0.0)

            off  = OFFSETS[metal]
            ax.bar(x + off, vals, WIDTH, color=COLORS[metal],
                   label=metal, edgecolor='white', linewidth=0.4)
            for xi, val in zip(x + off, vals):
                va = 'top' if val < 0 else 'bottom'
                dy = -0.03 if val < 0 else +0.03
                ax.text(xi, val + dy, f'{val:+.2f}',
                        ha='center', va=va, fontsize=6)

        ax.axhline(0, color='0.4', linewidth=0.8, linestyle='--')
        ax.set_xticks(x)
        ax.set_xticklabels(surf_labels)
        ax.set_xlabel('Surface')
        ax.set_ylabel(ylabel)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)

    axes[0].legend()
    fig.tight_layout()
    out = os.path.join(FIG_DIR, 'interlayer_bar.pdf')
    fig.savefig(out)
    plt.close(fig)
    print(f'Saved  {os.path.relpath(out)}')


# -- Entry point --------------------------------------------------------------

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Bonus 1 -- interlayer relaxation distances')
    parser.add_argument('--root', default=os.path.join(BASE_DIR, '../Wulff-Data'))
    parser.add_argument('--csv',  default=os.path.join(BASE_DIR, '../interlayer_relaxation.csv'))
    args = parser.parse_args()

    root = os.path.abspath(args.root)
    if not os.path.isdir(root):
        raise FileNotFoundError(f'Wulff-Data not found at: {root}')

    rows = compute(root)
    write_csv(rows, os.path.abspath(args.csv))
    plot(rows)
    print('Done.')
