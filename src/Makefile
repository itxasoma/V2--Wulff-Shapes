# Makefile for B2 – Magic cluster building blocks
# main.f90 reads the CSV directly.
FC      = gfortran
FFLAGS  = -O2 -g -Wall -Wextra -fcheck=all -fbacktrace
TARGET  = magic.x
PYTHON  = python3

all: $(TARGET)

main.o: main.f90
	$(FC) $(FFLAGS) -c $<

$(TARGET): main.o
	$(FC) $(FFLAGS) -o $@ $^

run: $(TARGET)
	mkdir -p ../results
	./$(TARGET) ../Global_minima_energies.csv ../results

figs:
	mkdir -p ../figures
	$(PYTHON) plots.py

clean:
	rm -f *.o *.mod $(TARGET)
