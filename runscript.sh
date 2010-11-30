#!/bin/bash
#$ -N immgen_preprocessing
#$ -M mike.dewar@columbia.edu
#$ -m beas
#$ -l mem=15G,time=24:00:00
#$ -cwd
#$ -o /ifs/scratch/c2b2/cw_lab/md2954/Logs/immgen.out
#$ -e /ifs/scratch/c2b2/cw_lab/md2954/Logs/immgen.err

# one needs to run the following before letting this script onto the cluster
#python preprocess_setup.py /ifs/scratch/c2b2/cw_lab/md2954/immgen

/nfs/apps/R/2.11.1/bin/Rscript /ifs/home/c2b2/cw_lab/md2954/Projects/immgen/preprocess_rscript.r
