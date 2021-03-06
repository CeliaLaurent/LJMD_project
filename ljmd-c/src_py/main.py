import sys
import data
from utilities import *
from output import *
from energy import *
import time

def create_system(input_contents):
   S=data.mdsys_t()
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
   return S,restfile,trajfile,ergfile,nprint

#****************************************************************************************

# MAIN

# read file from stdin

system,restfile,trajfile,ergfile,nprint=create_system(sys.stdin)

# otherwise read input file directly

#f = open("../examples/argon_108.inp", "r")
#system,restfile,trajfile,ergfile,nprint=create_system(f) 
#f.close()

system.nthreads = 1

# allocate memory

system.rx = (c_double * system.natoms)()
system.ry = (c_double * system.natoms)()
system.rz = (c_double * system.natoms)()
system.vx = (c_double * system.natoms)()
system.vy = (c_double * system.natoms)()
system.vz = (c_double * system.natoms)()
system.fx = (c_double * system.natoms)()
system.fy = (c_double * system.natoms)()
system.fz = (c_double * system.natoms)()

# read restart

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

# initialize forces and energies

system.nfi = 0

fso = CDLL("../Obj-new/libforce.so" )
fso.force.argtypes =[POINTER(data.mdsys_t)] #Structure

vso = CDLL("../Obj-new/libvelverlet.so" )
vso.velverlet.argtypes =[POINTER(data.mdsys_t)] #Structure
vso.velverlet_first.argtypes =[POINTER(data.mdsys_t)] #Structure
vso.velverlet_second.argtypes =[POINTER(data.mdsys_t)] #Structure

fso.force(system)
ekin(system)

erg = open(ergfile, "w")
traj = open(trajfile, "w")

print("Starting simulation with %d atoms for %d steps." % (system.natoms, system.nsteps));
print("     NFI            TEMP            EKIN                 EPOT              ETOT");

output(system, erg, traj)

#****************************************************************************************

# main MD loop 

t = 0.0
t_tmp = 0.0

for system.nfi in range(1, system.nsteps + 1):

    # write output, if requested 
    if ((system.nfi % nprint) == 0):
        output(system, erg, traj);
    
    t_tmp = time.time()
    
    # propagate system and recompute energies 
    vso.velverlet(system);
    ekin(system)
    
    t += time.time() - t_tmp

print("Evolve time: %.6f" %(t))

#****************************************************************************************

# clean up: close files
    
print("Simulation Done.");

erg.close()
traj.close()

#****************************************************************************************
