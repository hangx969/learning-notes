#!/bin/bash
#PBS -N hangxu-tesst-create_and_copy
#PBS -l walltime=00:10:00
#PBS -l nodes=1:ppn=1
#PBS -q batch

# 转到工作目录if needed
#cd $PBS_O_WORKDIR

# 加载Python模块 if needed
#module load python/3.8

# 执行Python脚本
python create_and_copy.py
