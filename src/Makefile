# ===========================================================================
#  Makefile V2: Wulff Surface Energies & Figures
#
#  Usage (run from src/):
#    make          compute energies + generate figures
#    make figs     generate figures from existing CSV
#    make run      force re-run of energy calculation
#    make clean    remove output CSV and PDF figures
# ===========================================================================

PYTHON  = python3
SCRIPT  = wulff_surface_energies.py
PLOTS   = plots.py
ROOT    = ../../Wulff-Data
CSV     = ../surface_energies_all.csv
FIGS    = ../figures

.PHONY: all figs run clean

all: $(CSV)
	$(PYTHON) $(PLOTS) --csv $(CSV)

$(CSV):
	$(PYTHON) $(SCRIPT) $(ROOT) --csv $(CSV)

figs:
	$(PYTHON) $(PLOTS) --csv $(CSV)

run:
	$(PYTHON) $(SCRIPT) $(ROOT) --csv $(CSV)
	$(PYTHON) $(PLOTS)  --csv $(CSV)

clean:
	rm -f $(CSV)
	rm -f $(FIGS)/surface_energies_bar.pdf $(FIGS)/relaxation_energy_bar.pdf $(FIGS)/wulff_h_values.pdf
	@echo "Output files removed."