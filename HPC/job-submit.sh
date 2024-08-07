#!/bin/bash
#PBS -N hangxu-test-create-and-copy
#PBS -l walltime=00:10:00
#PBS -l nodes=1:ppn=1
#PBS -q cpuq
#PBS -o my_job.out
#PBS -e my_job.err

cd $PBS_O_WORKDIR

module load python/3.8

python3 pbs-python.py