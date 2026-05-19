! Exercise B2: Magic cluster building blocks
! Reads Global_minima_energies.csv, computes:
!   - Binding energy per atom:    E_b(N)    = [E_ref*N - E(N)] / N
!   - Incremental binding energy: Delta_E(N) = E(N-1) + E_atom - E(N)
!   - Second finite difference:   Delta2(N)  = E(N+1) + E(N-1) - 2*E(N)
!     (local maxima in Delta2 identify magic numbers)
!
! Usage:  ./magic.x  [csv_file]  [results_dir]
! Output: <results_dir>/magic.dat

program main
  implicit none
  integer, parameter:: NMAX = 200
  character(len=200):: csv_file, results_dir, outfile
  character(len=512):: line
  integer:: ios, ndata, i, N
  integer:: Narr(NMAX)
  double precision:: Earr(NMAX)
  double precision:: Eb(NMAX), DeltaE(NMAX), Delta2(NMAX)
  double precision:: E_atom, E_ref
  character(len=1):: comma

  ! Reference energy: isolated (MgO)_1 divided by 2 atoms = monomer/diatom
  ! E_atom here is the energy of a single MgO formula unit (N=1).
  ! We use E(N=1) / (2*1) as the single-atom reference.
  ! All energies in eV.

  ! -- Default arguments -----------------------------------------------
  csv_file    = '../Global_minima_energies.csv'
  results_dir = '../results'
  call get_command_argument(1, csv_file)
  call get_command_argument(2, results_dir)

  ! -- Read CSV --------------------------------------------------------
  open(10, file=trim(csv_file), status='old', iostat=ios)
  if (ios /= 0) then
    write(*,'(A,A)') 'ERROR: cannot open ', trim(csv_file)
    stop
  endif

  ! Skip header line
  read(10,'(A)', iostat=ios) line
  if (ios /= 0) then
    write(*,*) 'ERROR: empty CSV file'
    stop
  endif

  ndata = 0
  do
    read(10,'(A)', iostat=ios) line
    if (ios /= 0) exit
    line = adjustl(trim(line))
    if (len_trim(line) == 0) cycle
    ndata = ndata + 1
    if (ndata > NMAX) then
      write(*,*) 'ERROR: more data rows than NMAX =', NMAX
      stop
    endif
    ! parse "N,energy"
    read(line, *, iostat=ios) Narr(ndata), comma, Earr(ndata)
    if (ios /= 0) then
      ! fallback: try comma as delimiter
      read(line, *, iostat=ios) Narr(ndata), Earr(ndata)
    endif
  enddo
  close(10)

  if (ndata < 3) then
    write(*,*) 'ERROR: need at least 3 data points, found', ndata
    stop
  endif

  write(*,'(A,I4,A)') 'Read ', ndata, ' data points from CSV.'

  ! -- Reference: energy per MgO formula unit from monomer (N=1) ------
  ! E_ref = E(N=1) / 1  (energy of one formula unit in the monomer)
  E_ref  = Earr(1)          ! total energy of (MgO)_1, eV
  E_atom = Earr(1) / 2.0d0 ! energy per atom (Mg + O) from monomer

  ! -- Binding energy per atom -----------------------------------------
  ! E_b(N) = [E_ref * N - E(N)] / (2N)
  !        = energy gained per atom relative to isolated monomers
  do i = 1, ndata
    N     = Narr(i)
    Eb(i) = (E_ref * dble(N) - Earr(i)) / dble(2 * N)
  enddo

  ! -- Incremental binding energy Delta_E(N) = E(N-1) + E_ref - E(N) --
  ! For N=1 (no N-1 available): set to 0
  DeltaE(1) = 0.0d0
  do i = 2, ndata
    DeltaE(i) = Earr(i-1) + E_ref - Earr(i)
  enddo

  ! -- Second finite difference Delta2(N) = E(N+1) + E(N-1) - 2*E(N) --
  ! Endpoints (N=1, N=ndata): set to 0 (not computable)
  Delta2(1)     = 0.0d0
  Delta2(ndata) = 0.0d0
  do i = 2, ndata-1
    Delta2(i) = Earr(i+1) + Earr(i-1) - 2.0d0 * Earr(i)
  enddo

  ! -- Screen output ---------------------------------------------------
  write(*,'(A)') ''
  write(*,'(A6,A10,A18,A18,A18,A18)') &
      'N_MgO', 'N_atoms', 'E_total(eV)', 'Eb/atom(eV)', 'DeltaE(eV)', 'Delta2(eV)'
  write(*,'(A)') repeat('-', 88)
  do i = 1, ndata
    write(*,'(I6,I10,F18.6,F18.8,F18.6,F18.6)') &
        Narr(i), 2*Narr(i), Earr(i), Eb(i), DeltaE(i), Delta2(i)
  enddo

  ! -- Write results file ----------------------------------------------
  call system('mkdir -p ' // trim(results_dir))

  outfile = trim(results_dir) // '/magic.dat'
  open(20, file=trim(outfile), status='replace')
  write(20,'(A)') '# B2 Magic cluster building blocks – (MgO)_N'
  write(20,'(A)') '# N_MgO  N_atoms  E_total(eV)  Eb_per_atom(eV)  DeltaE(eV)  Delta2(eV)'
  do i = 1, ndata
    write(20,'(I6,1X,I8,1X,F18.6,1X,F18.8,1X,F18.6,1X,F18.6)') &
        Narr(i), 2*Narr(i), Earr(i), Eb(i), DeltaE(i), Delta2(i)
  enddo
  close(20)

  print *, 'Written: ', trim(outfile)

end program main
