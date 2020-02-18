#include <math.h> //pow,sqrt
#include <stdlib.h> //malloc
#if defined (_OPENMP)
#include <omp.h>
#endif
#include "data.h"
#include "prototypes.h"
/* helper function: apply minimum image convention */
static inline __attribute__((always_inline)) double pbc(double x, const double boxby2) 
{
    while (x >  boxby2) x -= 2.0*boxby2;
    while (x < -boxby2) x += 2.0*boxby2;
    return x;
}

/* compute forces */
void force(mdsys_t *sys) 
{   
    
    double rcsq;
    double c12,c6;
    double half_box;
    

    /* zero energy and forces */
    double epot=0.0;

    // define temporary variables for avoiding using power, sqrt and some mult in cycle
    c12 = 4.0 * sys->epsilon*pow(sys->sigma, 12.0);
    c6 = 4.0 * sys->epsilon*pow(sys->sigma, 6.0);
    rcsq = sys->rcut * sys->rcut;
    half_box = 0.5*sys->box;
    
    /* def temporary buffer for position */
    double * R;
    
    R=(double *)malloc(sys->natoms*sizeof(double));
       
    for(int i=0; i<sys->natoms; i++){
        int ii = 3 * i;
        R[ ii ] = sys->rx[i];
        R[ ii + 1 ] = sys->ry[i];
        R[ ii + 2 ] = sys->rz[i];   
    }
     
    /* def temporary buffer for force */
    
    double * F;  
    
    F=(double *)malloc(3*sys->nthreads*sys->natoms*sizeof(double));
    
    printf("HERE WE ARE\n");
    
#if defined (_OPENMP)
#pragma omp parallel reduction(+:epot)
#endif
    {
       double rx,ry,rz;
       //double *fx,*fy,*fz;
       double * f;
       double rsq,ffac;
       double epot_priv=0.0;
       int i, ii;
       
       
       
#if defined (_OPENMP)
       int tid=omp_get_thread_num();
#else
       int tid=0;
#endif  
       
       
       /*
       fx=sys->fx + (tid*sys->natoms); azzero(fx,sys->natoms);
       fy=sys->fy + (tid*sys->natoms); azzero(fy,sys->natoms);
       fz=sys->fz + (tid*sys->natoms); azzero(fz,sys->natoms);  
       */
       
       f = F + (3 * tid * sys->natoms); 
       azzero(f, 3 * sys->natoms); 
       
       
       
       //azzero(fx,sys->natoms);
       
       
       //fy = F + 1 + (3 * tid * sys->natoms); 
       
       //azzero(fy,sys->natoms);
       
       //fz = F + 2 + (3 * tid * sys->natoms); 
       
       //azzero(fz,sys->natoms);
       
       printf("HERE WE ARE, %d, %d \n", tid, sys->nthreads);
       
       for(i=tid; i < (sys->natoms) -1 ; i+=sys->nthreads) {
           for(int j= i+1 ; j < (sys->natoms); ++j) {
               
               ii = 3 * i;
               int jj = 3 * j;
               
               printf("HERE WE ARE BEFORE, %d, %d \n", tid, sys->nthreads);
               /* get distance between particle i and j */
               rx=pbc(R[ ii ] - R[ jj ], half_box);
               ry=pbc(R[ ii+1 ] - R[ jj+1 ], half_box);
               rz=pbc(R[ ii+2 ] - R[ jj+2 ], half_box);
               rsq = rx*rx + ry*ry + rz*rz;
               printf("HERE WE ARE AFTER, %d, %d \n", tid, sys->nthreads);
         
               /* compute force and energy if within cutoff */
               if (rsq < rcsq) {
                   double r6, rinv;
                   rinv= 1.0/rsq;
                   r6 = rinv * rinv * rinv;
      
                   ffac = (12.0 * c12 * r6 -6.0*c6) * r6 *rinv;
                   epot_priv += r6 *(c12*r6 -c6);
                   /*
                   fx[i] += rx*ffac;
                   fy[i] += ry*ffac;
                   fz[i] += rz*ffac;
                   fx[j] -= rx*ffac;
           	       fy[j] -= ry*ffac;
           	       fz[j] -= rz*ffac;
                   */
                   f[ ii ] += rx*ffac;
                   f[ ii + 1 ] += rx*ffac;
                   f[ ii + 2 ] += rx*ffac;
                   f[ jj ] += rx*ffac;
                   f[ jj + 1 ] += rx*ffac;
                   f[ jj + 2 ] += rx*ffac;
                   
               }
           }
       }
       

       
       epot += epot_priv;  // omp reduction of epot
#if defined (_OPENMP)
#pragma omp barrier
#endif
       i = 1 + (sys->natoms / sys->nthreads);
       int fromidx = tid * i;
       int toidx = fromidx + i;
       if (toidx > sys->natoms) toidx = sys->natoms;
       for (i=1; i < sys->nthreads; ++i) {
         int offs = 3 * i *sys->natoms;
         for (int j=fromidx; j < toidx; ++j) {
           //sys->fx[j] += sys->fx[offs+j];
           //sys->fy[j] += sys->fy[offs+j];
           //sys->fz[j] += sys->fz[offs+j];
           int jj = 3 * j;
           sys->fx[j] += F[ offs + jj ];
           sys->fy[j] += F[ offs + jj + 1 ];
           sys->fz[j] += F[ offs + jj +2 ];
         }
       }
    } // end of parallel region
    
    sys->epot=epot;
}
