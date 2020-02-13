from ctypes import *

# generic file- or pathname buffer length 

BLEN = 200

# a few physical constants 

# boltzman constant in kcal/mol/K 
kboltz = 0.0019872067     
# m*v^2 in kcal/mol
mvsq2e = 2390.05736153349 

# structure to hold the complete information about the MD system 

class _mdsys(Structure):
    _fields_ = [
        ("natoms", c_int),
        ("nfi", c_int),
        ("nsteps", c_int),
        ("dt", c_double),
        ("mass", c_double),
        ("epsilon", c_double),
        ("sigma", c_double),
        ("box", c_double),
        ("rcut", c_double),
        ("ekin", c_double),
        ("epot", c_double),
        ("temp", c_double),
        ("rx", c_double_p),
        ("ry", c_double_p),
        ("rz", c_double_p),
        ("vx", c_double_p),
        ("vy", c_double_p),
        ("vz", c_double_p),
        ("fx", c_double_p),
        ("fy", c_double_p),
        ("fz", c_double_p)
    ]

#struct _mdsys {
#    int natoms,nfi,nsteps;
#    double dt, mass, epsilon, sigma, box, rcut;
#    double ekin, epot, temp;
#    double *rx, *ry, *rz;
#    double *vx, *vy, *vz;
#    double *fx, *fy, *fz;
#};
#typedef struct _mdsys mdsys_t; 
