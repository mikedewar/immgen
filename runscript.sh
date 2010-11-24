#!/bin/bash
#$ -N immgen_preprocessing
#$ -M mike.dewar@columbia.edu
#$ -m beas
#$ -l mem=15G,time=24:00:00
#$ -cwd
#$ -o /ifs/home/c2b2/cw_lab/md2954/Data/immgen.out
#$ -e /ifs/home/c2b2/cw_lab/md2954/Data/immgen.err
/nfs/apps/R/2.11.1/bin/Rscript /ifs/home/c2b2/cw_lab/md2954/Projects/immgen/preprocess_rscript.r
