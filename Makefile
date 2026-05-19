# ===========================================================================
#  Makefile — Wulff Surface Energies
#
#  Usage:
#    make                     full run (Cu + Pd, surfaces 001 011 111)
#    make run                 force re-run even if CSV exists
#    make diagnose            list which files are found in each folder
#    make cu                  Cu only
#    make pd                  Pd only
#    make cu_001              Cu (001) only
#    make pd_111              Pd (111) only
#    make clean               remove all output CSVs
#
#  Override root:   make ROOT=/path/to/Wulff_Data
#  Override metals: make METALS="Cu"
#  Override surfs:  make SURFACES="001 111"
# ===========================================================================

PYTHON   = python3
SCRIPT   = wulff_surface_energies.py
ROOT     = .
METALS   = Cu Pd
SURFACES = 001 011 111

CSV_ALL  = surface_energies_all.csv
CSV_CU   = surface_energies_Cu.csv
CSV_PD   = surface_energies_Pd.csv

.PHONY: all run diagnose cu pd cu_001 cu_011 cu_111 pd_001 pd_011 pd_111 clean help

# ── Default ───────────────────────────────────────────────────────────────────
all: $(CSV_ALL)

$(CSV_ALL):
	$(PYTHON) $(SCRIPT) "$(ROOT)" --metals $(METALS) --surfaces $(SURFACES) --csv $(CSV_ALL)

# ── Force re-run (always executes) ───────────────────────────────────────────
run:
	$(PYTHON) $(SCRIPT) "$(ROOT)" --metals $(METALS) --surfaces $(SURFACES) --csv $(CSV_ALL)

# ── Show what files are found ─────────────────────────────────────────────────
diagnose:
	$(PYTHON) $(SCRIPT) "$(ROOT)" --metals $(METALS) --surfaces $(SURFACES) --diagnose

# ── Per-metal ─────────────────────────────────────────────────────────────────
cu:
	$(PYTHON) $(SCRIPT) "$(ROOT)" --metals Cu --surfaces $(SURFACES) --csv $(CSV_CU)

pd:
	$(PYTHON) $(SCRIPT) "$(ROOT)" --metals Pd --surfaces $(SURFACES) --csv $(CSV_PD)

# ── Per-surface ───────────────────────────────────────────────────────────────
cu_001:
	$(PYTHON) $(SCRIPT) "$(ROOT)" --metals Cu --surfaces 001 --csv surface_energies_Cu_001.csv

cu_011:
	$(PYTHON) $(SCRIPT) "$(ROOT)" --metals Cu --surfaces 011 --csv surface_energies_Cu_011.csv

cu_111:
	$(PYTHON) $(SCRIPT) "$(ROOT)" --metals Cu --surfaces 111 --csv surface_energies_Cu_111.csv

pd_001:
	$(PYTHON) $(SCRIPT) "$(ROOT)" --metals Pd --surfaces 001 --csv surface_energies_Pd_001.csv

pd_011:
	$(PYTHON) $(SCRIPT) "$(ROOT)" --metals Pd --surfaces 011 --csv surface_energies_Pd_011.csv

pd_111:
	$(PYTHON) $(SCRIPT) "$(ROOT)" --metals Pd --surfaces 111 --csv surface_energies_Pd_111.csv

# ── Clean ─────────────────────────────────────────────────────────────────────
clean:
	rm -f surface_energies_*.csv
	@echo "CSV files removed."

# ── Help ──────────────────────────────────────────────────────────────────────
help:
	@echo ""
	@echo "  make                   Full run: Cu + Pd, all surfaces"
	@echo "  make run               Force re-run"
	@echo "  make diagnose          Show which files are found"
	@echo "  make cu / pd           Single metal, all surfaces"
	@echo "  make cu_001 ... pd_111 Single metal + surface"
	@echo "  make clean             Remove output CSVs"
	@echo ""
	@echo "  Override root:    make ROOT=/path/to/Wulff_Data"
	@echo "  Override metals:  make METALS=Cu"
	@echo "  Override surfaces: make SURFACES=\"001 111\""
	@echo ""
