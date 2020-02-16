#include <math.h> //pow,sqrt
#include "data.h"
#include "prototypes.h"

/* helper function: apply minimum image convention */
double pbc(double x, const double boxby2)
{
    while (x >  boxby2) x -= 2.0*boxby2;
    while (x < -boxby2) x += 2.0*boxby2;
    return x;
}

/* compute forces */
void force(mdsys_t *sys) 
{
    double rsq, rcsq, ffac;
    double rx,ry,rz;
    double t_fx, t_fy, t_fz;
    double c12, c6;
    int i,j;

    /* zero energy and forces */
    sys->epot=0.0;
    azzero(sys->fx,sys->natoms);
    azzero(sys->fy,sys->natoms);
    azzero(sys->fz,sys->natoms);
    
    // define temporary variables for avoiding using power and sqrt in cycle
    c12 = 4.0 * sys->epsilon*pow(sys->sigma, 12.0);
    c6 = 4.0 * sys->epsilon*pow(sys->sigma, 6.0);
    rcsq = sys->rcut * sys->rcut;

    for(i=0; i < (sys->natoms) -1 ; ++i) {
        
        t_fx = 0.0;
        t_fy = 0.0;
        t_fz = 0.0;
        
        for(j= i+1 ; j < (sys->natoms); ++j) {
            
            /* get distance between particle i and j */
            rx=pbc(sys->rx[i] - sys->rx[j], 0.5*sys->box);
            ry=pbc(sys->ry[i] - sys->ry[j], 0.5*sys->box);
            rz=pbc(sys->rz[i] - sys->rz[j], 0.5*sys->box);
            rsq = rx*rx + ry*ry + rz*rz;
      
            /* compute force and energy if within cutoff */
            if (rsq < rcsq) {
                double r6, rinv;
                rinv= 1.0/rsq;
                r6 = rinv * rinv * rinv;
                //ffac = -4.0*sys->epsilon*(-12.0*pow(sys->sigma/r,12.0)/r
                //                         +6*pow(sys->sigma/r,6.0)/r);
                
                ffac = (12.0 * c12 * r6 -6.0*c6) * r6 *rinv;
                
                //sys->epot += 4.0*sys->epsilon*(pow(sys->sigma/r,12.0)
                //                               -pow(sys->sigma/r,6.0));
                
                sys->epot += r6 *(c12*r6 -c6);
                
                t_fx += rx*ffac;
                t_fy += ry*ffac;
                t_fz += rz*ffac;

		        sys->fx[j] -= rx*ffac;
		        sys->fy[j] -= ry*ffac;
		        sys->fz[j] -= rz*ffac;
             
            }
        }
    
        sys->fx[i] += t_fx;
        sys->fy[i] += t_fy;
        sys->fz[i] += t_fz;
    
    }
}

