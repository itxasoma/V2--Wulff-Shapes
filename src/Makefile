# ===========================================================================
#  Makefile -- V2: Wulff Surface Energies & Figures
#
#  Usage (run from src/):
#    make          compute energies + generate all figures
#    make figs     generate figures from existing CSV
#    make run      force re-run of energy calculation
#    make bonus1   interlayer relaxation (Bonus Track 1)
#    make clean    remove output CSV and PDF figures
# ===========================================================================

PYTHON  = python3
SCRIPT  = wulff_surface_energies.py
PLOTS   = plots.py
BONUS1  = interlayer.py
ROOT    = ../Wulff-Data
CSV     = ../surface_energies_all.csv
FIGS    = ../figures

.PHONY: all figs run bonus1 clean

all: $(CSV)
	$(PYTHON) $(PLOTS) --csv $(CSV)

$(CSV):
	$(PYTHON) $(SCRIPT) $(ROOT) --csv $(CSV)

figs:
	$(PYTHON) $(PLOTS) --csv $(CSV)

run:
	$(PYTHON) $(SCRIPT) $(ROOT) --csv $(CSV)
	$(PYTHON) $(PLOTS)  --csv $(CSV)

bonus1:
	$(PYTHON) $(BONUS1) --root $(ROOT)

clean:
	rm -f $(CSV) ../interlayer_relaxation.csv
	rm -f $(FIGS)/surface_energies_bar.pdf $(FIGS)/relaxation_energy_bar.pdf
	rm -f $(FIGS)/wulff_h_values.pdf $(FIGS)/interlayer_bar.pdf
	@echo "Output files removed."
