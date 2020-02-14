#!/bin/bash

no_opt="-Wall -pg -no-pie"
O2="-Wall -pg -no-pie -O2"
O3="-Wall -pg -no-pie -O3"
fast_math="-Wall -pg -no-pie -O3 -ffast-math"
expensive_opt="-Wall -pg -no-pie -O3 -ffast-math -fexpensive-optimizations" 
msse="-Wall -pg -no-pie -O3 -ffast-math -fexpensive-optimizations -msse3"


opt=( "$no_opt" "${O2}" "${O3}" "${fast_math}" "${expensive_opt}" "${msse}")
#opt=( "$msse" )
names=('no_opt' 'O2' 'O3' 'fast_math' 'expensive_opt' 'msse')
#names=( 'msse' )

head -10 ../reference/argon_108.dat | awk '{printf("%d %.6f %.6f %.6f\n",$1,$2,$3,$4);}'> ref.dat

for i in $(seq 1 ${#opt[@]})
do 
  idx=$((i-1))
  name=${names[$idx]}
  make -B CFLAGS="${opt[idx]}" EXE="$name.x"
  
  /usr/bin/time ./${name}.x < argon_108.inp #2>${name}.time
  
  gprof ./${name}.x gmon.out > ${name}_analysis.txt
 
  head -10 argon_108.dat | awk '{printf("%d %.6f %.6f %.6f\n",$1,$2,$3,$4);}'> a.dat
  numdiff -a 1e-4 a.dat ref.dat || exit 1
  rm -f a.dat
done

rm argon_108.dat
rm argon_108.xyz
rm ref.dat
rm gmon.out

