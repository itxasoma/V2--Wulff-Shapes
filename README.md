# G1--Elasticity-of-a-gold-nanowire

Molecular dynamics simulation of tensile deformation of an Au nanowire oriented along [110], using LAMMPS with an EAM force field. Analysis includes stress-strain curves, Young's modulus, and coordination-number-based defect tracking.

## Repo structure

```
├── MNS/
│   └── nanowire/
│       ├── in.nano                        ← LAMMPS input script
│       ├── Au_u3.eam                      ← EAM force field (Foiles et al., PRB 33, 7983, 1986)
│       └── lammps-210912-smp-iqtc05.sub  ← SGE job submission script
├── src/
│   ├── plots.py                           ← Stress-strain and Epot plots
│   ├── defects.py                         ← Coordination number and defect analysis
│   ├── Makefile
│   └── lib/
│       ├── science.mplstyle
│       └── requirements.txt
├── figures/                               ← Output PDFs (stress-strain, Epot)
└── defects/                               ← Output PDFs and CN table (CSV)
```

> **Note:** Large simulation outputs (`Au_tension.xyz`, `pos.dump`, `log.lammps`, ~900 MB) are not tracked by git. They are produced by running the simulation as described below.

## Virtual environment

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r src/lib/requirements.txt
```

## Running the simulation

The simulation runs on a cluster via SGE. Copy the input files and submit:

```bash
# On the cluster
cd $HOME/MNS/nanowire/
qsub lammps-210912-smp-iqtc05.sub
```

Output files will be written to `$HOME/MNS/nanowire/nanowire/$JOB_ID/`:
- `log.lammps` — thermodynamic data (step, T, Epot, Lz, Vol, Pzz)
- `Au_tension.xyz` — atomic positions at every 200 steps
- `pos.dump` — LAMMPS dump during thermalisation

Wall clock time: ~2 days (1 core).

## Analysis

```bash
cd src/
make figs      # stress-strain and Epot plots → figures/
make defects   # coordination number and defect analysis → defects/
```

Breaking point identified visually in VMD at **frame 328 / 2000** (~65.6% strain).
