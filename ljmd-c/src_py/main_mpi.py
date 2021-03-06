import sys
from data import *
from utilities import *
from output import *
from energy import *
import time
from mpi4py import MPI

def create_system(S, input_contents):
   for count,line in enumerate(input_contents):
       (R,value)=get_a_line(line)
       if(R==0):
          if(  count== 0): S.natoms  = c_int(int(value))
          elif(count== 1): S.mass    = c_double(float(value))
          elif(count== 2): S.epsilon = c_double(float(value))
          elif(count== 3): S.sigma   = c_double(float(value))
          elif(count== 4): S.rcut    = c_double(float(value))
          elif(count== 5): S.box     = c_double(float(value))
          elif(count== 6): restfile  = value
          elif(count== 7): trajfile  = value
          elif(count== 8): ergfile   = value
          elif(count== 9): S.nsteps  = c_int(int(value))
          elif(count==10): S.dt      = c_double(float(value))
          elif(count==11): nprint    = int(value)
   return restfile,trajfile,ergfile,nprint

#****************************************************************************************

# MAIN

system = mdsys_t()

comm = MPI.COMM_WORLD
comm_ptr = MPI._addressof(comm)
comm_val = MPI_Comm.from_address(comm_ptr)

system.mpicomm = comm_val
system.mpirank  = comm.Get_rank()
system.nprocs = comm.Get_size()

if (system.mpirank == 0):
    
    # read file from stdin

    restfile,trajfile,ergfile,nprint=create_system(system, sys.stdin)
    
    # otherwise read input file directly

    #f = open("../examples/argon_2916.inp", "r")
    #restfile,trajfile,ergfile,nprint=create_system(system, f) 
    #f.close()
    
system.dt = comm.bcast(system.dt, root = 0)
system.nsteps = comm.bcast(system.nsteps, root = 0)
system.box = comm.bcast(system.box, root = 0)
system.rcut = comm.bcast(system.rcut, root = 0)
system.natoms = comm.bcast(system.natoms, root = 0) 
system.sigma = comm.bcast(system.sigma, root = 0)
system.epsilon = comm.bcast(system.epsilon, root = 0)
system.mass = comm.bcast(system.mass, root = 0)

system.nthreads = 1

# allocate memory

system.rx = (c_double * system.natoms)()
system.ry = (c_double * system.natoms)()
system.rz = (c_double * system.natoms)()
system.vx = (c_double * system.natoms)()
system.vy = (c_double * system.natoms)()
system.vz = (c_double * system.natoms)()

system.cx = (c_double * system.natoms)()
system.cy = (c_double * system.natoms)()
system.cz = (c_double * system.natoms)()

if system.mpirank == 0:
    system.fx = (c_double * system.natoms)()
    system.fy = (c_double * system.natoms)()
    system.fz = (c_double * system.natoms)()

# read restart

if system.mpirank == 0:

    fp = open("../examples/" + restfile, "r")

    for i in range(system.natoms):
        rx, ry, rz = fp.readline().split()
        system.rx[i] = c_double(float(rx))
        system.ry[i] = c_double(float(ry))
        system.rz[i] = c_double(float(rz))
    for i in range(system.natoms):
        vx, vy, vz = fp.readline().split()
        system.vx[i] = c_double(float(vx))
        system.vy[i] = c_double(float(vy))
        system.vz[i] = c_double(float(vz))

    fp.close()
    
comm.barrier()

# initialize forces and energies

system.nfi = 0

fso = CDLL("../Obj-mpi/libforce_mpi.so" )
fso.force.argtypes =[POINTER(mdsys_t)] #Structure

vso = CDLL("../Obj-mpi/libvelverlet.so" )
vso.velverlet.argtypes =[POINTER(mdsys_t)] #Structure
vso.velverlet_first.argtypes =[POINTER(mdsys_t)] #Structure
vso.velverlet_second.argtypes =[POINTER(mdsys_t)] #Structure

fso.force(system)

if system.mpirank == 0:
    ekin(system)

    erg = open(ergfile, "w")
    traj = open(trajfile, "w")

    print("Starting simulation with %d atoms for %d steps." % (system.natoms, system.nsteps));
    print("     NFI            TEMP            EKIN                 EPOT              ETOT");

    output(system, erg, traj)

#****************************************************************************************

# main MD loop with timing
 
t = 0.0
final_t = 0.0

for system.nfi in range(1, system.nsteps + 1):

    # write output, if requested 
    if (system.mpirank == 0 and (system.nfi % nprint) == 0):
        output(system, erg, traj);
    
    t_tmp = time.time()
    
    # propagate system and recompute energies 
    if system.mpirank == 0:
        vso.velverlet_first(system);
    
    fso.force(system)
    
    if system.mpirank == 0:
        vso.velverlet_second(system);
        ekin(system)
    
    t += time.time() - t_tmp

final_t = comm.reduce(t, op = MPI.MAX, root = 0)

print("Time proc %d: %.6f" %(system.mpirank, t))
if system.mpirank == 0:
    print("Evolve time: %.6f" %(final_t))
    
#****************************************************************************************

# clean up: close files

if system.mpirank == 0:
    print("Simulation Done.");

    erg.close()
    traj.close()

#****************************************************************************************
