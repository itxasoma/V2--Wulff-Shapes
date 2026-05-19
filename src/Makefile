# ===========================================================================
#  Makefile — Wulff Surface Energies + Figures
#  Location: src/Makefile
#
#  Usage (from src/):
#    make                     compute energies + generate figures
#    make energies            compute surface energies only
#    make figures             generate figures from existing CSV
#    make run                 force re-run of energy calculation
#    make diagnose            list VASP files found in each folder
#    make cu / pd             single metal, all surfaces
#    make cu_001 ... pd_111   single metal + surface
#    make clean               remove all output CSV and PDF figures
#
#  Or from the repo root:
#    make -C src ROOT=/path/to/Wulff_Data
#
#  Override root:     make ROOT=/path/to/Wulff_Data
#  Override metals:   make METALS="Cu"
#  Override surfaces: make SURFACES="001 111"
#
#  CSV and figures are saved one level up (../)
# ===========================================================================

PYTHON   = python3
SRC_DIR  = $(dir $(abspath $(lastword $(MAKEFILE_LIST))))
SCRIPT   = $(SRC_DIR)wulff_surface_energies.py
PLOTS    = $(SRC_DIR)plots.py
ROOT     = .
METALS   = Cu Pd
SURFACES = 001 011 111

CSV_ALL  = ../surface_energies_all.csv
CSV_CU   = ../surface_energies_Cu.csv
CSV_PD   = ../surface_energies_Pd.csv

.PHONY: all energies figures run diagnose cu pd \
        cu_001 cu_011 cu_111 pd_001 pd_011 pd_111 clean help

# ── Default: energies + figures ───────────────────────────────────────────────
all: $(CSV_ALL)
	$(PYTHON) "$(PLOTS)" --csv $(CSV_ALL) --metals $(METALS) --surfaces $(SURFACES)

# ── Energies only ─────────────────────────────────────────────────────────────
energies: $(CSV_ALL)

$(CSV_ALL):
	$(PYTHON) "$(SCRIPT)" "$(ROOT)" --metals $(METALS) --surfaces $(SURFACES) --csv $(CSV_ALL)

# ── Figures only (CSV must exist) ────────────────────────────────────────────
figures:
	$(PYTHON) "$(PLOTS)" --csv $(CSV_ALL) --metals $(METALS) --surfaces $(SURFACES)

# ── Force re-run ──────────────────────────────────────────────────────────────
run:
	$(PYTHON) "$(SCRIPT)" "$(ROOT)" --metals $(METALS) --surfaces $(SURFACES) --csv $(CSV_ALL)
	$(PYTHON) "$(PLOTS)"  --csv $(CSV_ALL) --metals $(METALS) --surfaces $(SURFACES)

# ── Diagnose ──────────────────────────────────────────────────────────────────
diagnose:
	$(PYTHON) "$(SCRIPT)" "$(ROOT)" --metals $(METALS) --surfaces $(SURFACES) --diagnose

# ── Per-metal ─────────────────────────────────────────────────────────────────
cu:
	$(PYTHON) "$(SCRIPT)" "$(ROOT)" --metals Cu --surfaces $(SURFACES) --csv $(CSV_CU)
	$(PYTHON) "$(PLOTS)"  --csv $(CSV_CU) --metals Cu --surfaces $(SURFACES)

pd:
	$(PYTHON) "$(SCRIPT)" "$(ROOT)" --metals Pd --surfaces $(SURFACES) --csv $(CSV_PD)
	$(PYTHON) "$(PLOTS)"  --csv $(CSV_PD) --metals Pd --surfaces $(SURFACES)

# ── Per-surface ───────────────────────────────────────────────────────────────
cu_001:
	$(PYTHON) "$(SCRIPT)" "$(ROOT)" --metals Cu --surfaces 001 --csv ../surface_energies_Cu_001.csv

cu_011:
	$(PYTHON) "$(SCRIPT)" "$(ROOT)" --metals Cu --surfaces 011 --csv ../surface_energies_Cu_011.csv

cu_111:
	$(PYTHON) "$(SCRIPT)" "$(ROOT)" --metals Cu --surfaces 111 --csv ../surface_energies_Cu_111.csv

pd_001:
	$(PYTHON) "$(SCRIPT)" "$(ROOT)" --metals Pd --surfaces 001 --csv ../surface_energies_Pd_001.csv

pd_011:
	$(PYTHON) "$(SCRIPT)" "$(ROOT)" --metals Pd --surfaces 011 --csv ../surface_energies_Pd_011.csv

pd_111:
	$(PYTHON) "$(SCRIPT)" "$(ROOT)" --metals Pd --surfaces 111 --csv ../surface_energies_Pd_111.csv

# ── Clean ─────────────────────────────────────────────────────────────────────
clean:
	rm -f ../surface_energies_*.csv
	rm -f ../figures/surface_energies_bar.pdf ../figures/relaxation_energy_bar.pdf ../figures/wulff_h_values.pdf
	@echo "Output files removed."

# ── Help ──────────────────────────────────────────────────────────────────────
help:
	@echo ""
	@echo "  make                   Compute energies + generate all figures"
	@echo "  make energies          Compute energies only"
	@echo "  make figures           Generate figures from existing CSV"
	@echo "  make run               Force re-run (ignore existing CSV)"
	@echo "  make diagnose          Show which VASP files are found"
	@echo "  make cu / pd           Single metal, all surfaces"
	@echo "  make cu_001 ... pd_111 Single metal + surface"
	@echo "  make clean             Remove output CSVs and PDF figures"
	@echo ""
	@echo "  Override root:     make ROOT=/path/to/Wulff_Data"
	@echo "  Override metals:   make METALS=Cu"
	@echo "  Override surfaces: make SURFACES=\"001 111\""
	@echo ""
