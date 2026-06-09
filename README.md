# V2--Wulff-Shapes

DFT-PBE surface energy calculations for the three low-index facets of Cu and Pd,
followed by the Wulff construction to obtain the equilibrium nanoparticle shape.

## Repo structure

```
├── Wulff-Data/
│   ├── Cu/
│   │   ├── Bulk/    OUTCAR + POSCAR for the fcc bulk unit cell
│   │   ├── 001/     OUTCAR + CONTCAR for the relaxed slab
│   │   ├── 011/
│   │   └── 111/
│   └── Pd/
│       ├── Bulk/
│       ├── 001/
│       ├── 011/
│       └── 111/
├── src/
│   ├── wulff_surface_energies.py  reads VASP output, writes CSV
│   ├── plots.py                   reads CSV, writes PDF figures
│   ├── Makefile
│   └── lib/
│       ├── science.mplstyle
│       └── requirements.txt
├── figures/                       output PDFs
└── surface_energies_all.csv       computed surface energies
```

## Virtual environment

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r src/lib/requirements.txt
```

## Running the analysis

```bash
cd src/
make        # compute energies + generate all figures
make figs   # regenerate figures from existing CSV
make run    # force re-run (ignore existing CSV)
make clean  # remove CSV and PDF outputs
```

Figures are saved in `figures/`:
- `surface_energies_bar.pdf`   — fixed vs. relaxed $\gamma$ for all facets
- `relaxation_energy_bar.pdf`  — $\Delta\gamma$ per facet
- `wulff_h_values.pdf`         — normalised Wulff h-values

## Results summary

| Metal | $\gamma_{111}$ (J m⁻²) | $\gamma_{001}$ (J m⁻²) | $\gamma_{011}$ (J m⁻²) |
|-------|--------------|--------------|--------------|
| Cu    | 1.3313       | 1.5102       | 1.5421       |
| Pd    | 1.1352       | 1.5022       | 1.5406       |

Stability order: $\gamma_{111}$ < $\gamma_{001}$ < $\gamma_{011}$ for both metals.
Wulff shapes: truncated octahedron (Cu) and near-perfect octahedron (Pd).
