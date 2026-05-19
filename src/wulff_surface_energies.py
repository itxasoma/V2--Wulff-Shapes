#!/usr/bin/env python3
"""
wulff_surface_energies.py
Computes fixed and relaxed surface energies from VASP 5.x output files.

Usage:
    python3 src/wulff_surface_energies.py /path/to/Wulff_Data
    python3 src/wulff_surface_energies.py /path/to/Wulff_Data --metals Cu Pd --surfaces 001 011 111

CSV is saved in the CURRENT WORKING DIRECTORY (where you run the script from).

Requires: numpy  (pip install numpy)
"""

import sys
import argparse
from pathlib import Path

try:
    import numpy as np
except ImportError:
    sys.exit("[ERROR] numpy not found.  Install with:  pip install numpy")

EV_TO_JM2 = 16.0218   # 1 eV/Å² → J/m²


# ── File finders ──────────────────────────────────────────────────────────────

def find_file(directory: Path, basenames: list) -> Path:
    for name in basenames:
        for candidate in [name, name + ".vasp"]:
            p = directory / candidate
            if p.exists() and p.stat().st_size > 0:
                return p
    tried = [f"{n}[.vasp]" for n in basenames]
    raise FileNotFoundError(
        f"None of [{', '.join(tried)}] found (non-empty) in:\n    {directory}")

def find_outcar(d): return find_file(d, ["OUTCAR"])
def find_poscar(d): return find_file(d, ["POSCAR", "CONTCAR"])


# ── OUTCAR parsers ────────────────────────────────────────────────────────────

def get_all_toten(outcar: Path) -> list:
    values = []
    with open(outcar) as fh:
        for line in fh:
            if "free  energy   TOTEN" in line:
                values.append(float(line.split()[-2]))
    if not values:
        raise ValueError(f"No TOTEN line found in {outcar}")
    return values

def get_nions(outcar: Path) -> int:
    with open(outcar) as fh:
        for line in fh:
            if "NIONS =" in line:
                return int(line.split()[-1])
    raise ValueError(f"NIONS not found in {outcar}")


# ── POSCAR / CONTCAR parser ───────────────────────────────────────────────────

def parse_poscar(path: Path):
    with open(path) as fh:
        lines = [l.rstrip() for l in fh if l.strip()]
    scale = float(lines[1].split()[0])
    vecs  = [[float(x) * scale for x in lines[i].split()] for i in range(2, 5)]
    lattice = np.array(vecs)
    tokens5 = lines[5].split()
    try:
        counts = [int(t) for t in tokens5]
    except ValueError:
        counts = [int(t) for t in lines[6].split()]
    return lattice, sum(counts)

def surface_area(poscar: Path) -> float:
    lattice, _ = parse_poscar(poscar)
    return float(np.linalg.norm(np.cross(lattice[0], lattice[1])))


# ── Energy functions ──────────────────────────────────────────────────────────

def bulk_energy_per_atom(bulk_dir: Path) -> float:
    outcar = find_outcar(bulk_dir)
    totens = get_all_toten(outcar)
    nions  = get_nions(outcar)
    e      = totens[-1]
    print(f"    File   : {outcar.name}")
    print(f"    TOTEN  : {e:.6f} eV  ({nions} atoms)  →  {e/nions:.6f} eV/atom")
    return e / nions

def compute_surface_energies(surf_dir: Path, e_bulk_per_atom: float):
    outcar = find_outcar(surf_dir)
    poscar = find_poscar(surf_dir)
    totens = get_all_toten(outcar)
    nions  = get_nions(outcar)
    A      = surface_area(poscar)
    e_fix   = totens[0]
    e_relax = totens[-1]
    gf_eV = (e_fix   - nions * e_bulk_per_atom) / (2 * A)
    gr_eV = (e_relax - nions * e_bulk_per_atom) / (2 * A)
    gf_J  = gf_eV * EV_TO_JM2
    gr_J  = gr_eV * EV_TO_JM2
    print(f"    Files  : {outcar.name}  |  {poscar.name}")
    print(f"    N={nions}  A={A:.4f} Å²")
    print(f"    E_fix  = {e_fix:.6f} eV  →  γ_fix  = {gf_J:.4f} J/m²")
    print(f"    E_relax= {e_relax:.6f} eV  →  γ_relax= {gr_J:.4f} J/m²")
    return gf_J, gr_J, gr_J - gf_J, gr_eV


# ── Output ────────────────────────────────────────────────────────────────────

def print_table(results, metals, surfaces):
    W = 78
    SEP = "─" * W
    print(f"\n\n{'SURFACE ENERGY SUMMARY':^{W}}")
    print(SEP)
    print(f"{'Metal':<6} {'Surface':<9} "
          f"{'γ_fix (J/m²)':>14} {'γ_relax (J/m²)':>15} "
          f"{'Δγ (J/m²)':>11} {'γ_relax (eV/Å²)':>16}")
    print(SEP)
    for metal in metals:
        if metal not in results:
            continue
        min_s = min(results[metal], key=lambda s: results[metal][s][1])
        for surf in surfaces:
            if surf not in results[metal]:
                continue
            gf, gr, dg, gr_ev = results[metal][surf]
            tag = "  ← most stable" if surf == min_s else ""
            print(f"{metal:<6} ({surf})     "
                  f"{gf:>14.4f} {gr:>15.4f} {dg:>11.4f} {gr_ev:>16.6f}{tag}")
        print(SEP)
    print("\nWulff h-values  (normalised: most stable = 1.000)")
    print("→  Enter in VESTA: Edit → Edit Data → Crystal Shape")
    print(f"{'Metal':<6}  {'h(001)':>8}  {'h(011)':>8}  {'h(111)':>8}")
    for metal in metals:
        if metal not in results:
            continue
        vals   = {s: results[metal][s][3] for s in surfaces if s in results[metal]}
        min_g  = min(vals.values())
        normed = {s: v / min_g for s, v in vals.items()}
        row    = "  ".join(f"{normed.get(s, float('nan')):>8.4f}" for s in surfaces)
        print(f"{metal:<6}  {row}")
    print()

def save_csv(results, metals, surfaces, outfile: Path):
    """Save to CWD, not inside ROOT."""
    outfile = Path.cwd() / outfile.name
    with open(outfile, "w") as fh:
        fh.write("Metal,Surface,gamma_fix_Jm2,gamma_relax_Jm2,"
                 "delta_gamma_Jm2,gamma_relax_eVA2\n")
        for metal in metals:
            if metal not in results:
                continue
            for surf in surfaces:
                if surf not in results[metal]:
                    continue
                gf, gr, dg, gr_ev = results[metal][surf]
                fh.write(f"{metal},{surf},{gf:.6f},{gr:.6f},"
                         f"{dg:.6f},{gr_ev:.8f}\n")
    print(f"  CSV saved → {outfile}")


# ── Diagnostic ────────────────────────────────────────────────────────────────

def diagnose(root: Path, metals: list, surfaces: list):
    print("\n── File scan ──────────────────────────────────────────────")
    for metal in metals:
        for parts in [("Bulk",)] + [("Surfaces", s) for s in surfaces]:
            d = root / metal / Path(*parts)
            label = f"{metal}/{'/'.join(parts)}"
            if not d.exists():
                print(f"  [MISSING DIR]  {label}")
                continue
            files = sorted(p.name for p in d.iterdir() if p.is_file())
            print(f"  {label}: {files}")
    print()


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Compute Wulff surface energies from VASP 5.x output")
    parser.add_argument("root", nargs="?", default=".",
                        help="Root directory containing Cu/ and Pd/")
    parser.add_argument("--metals",   nargs="+", default=["Cu", "Pd"])
    parser.add_argument("--surfaces", nargs="+", default=["001", "011", "111"])
    parser.add_argument("--csv",      default="surface_energies.csv",
                        help="Output CSV filename (saved in current directory)")
    parser.add_argument("--diagnose", action="store_true",
                        help="List files found and exit")
    args = parser.parse_args()

    root     = Path(args.root).expanduser().resolve()
    metals   = args.metals
    surfaces = args.surfaces
    csv_path = Path(args.csv)

    print(f"Root directory : {root}")
    print(f"Output CSV     : {Path.cwd() / csv_path.name}")
    diagnose(root, metals, surfaces)

    if args.diagnose:
        return

    results = {}
    for metal in metals:
        bulk_dir = root / metal / "Bulk"
        if not bulk_dir.exists():
            print(f"[WARN] {bulk_dir} not found — skipping {metal}")
            continue
        print(f"\n{'='*60}")
        print(f"  {metal}  —  Bulk")
        print(f"{'='*60}")
        try:
            e_bulk = bulk_energy_per_atom(bulk_dir)
        except Exception as exc:
            print(f"  [ERR] {exc}")
            continue
        results[metal] = {}
        for surf in surfaces:
            surf_dir = root / metal / "Surfaces" / surf
            if not surf_dir.exists():
                print(f"  [WARN] {surf_dir} not found — skipping")
                continue
            print(f"\n  {metal} ({surf})")
            try:
                results[metal][surf] = compute_surface_energies(surf_dir, e_bulk)
            except Exception as exc:
                print(f"  [ERR] {exc}")

    print_table(results, metals, surfaces)
    save_csv(results, metals, surfaces, csv_path)


if __name__ == "__main__":
    main()
