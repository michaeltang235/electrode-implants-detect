#!/bin/bash
####### Reserve computing resources #############
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --time=01:30:00
#SBATCH --mem=10G
#SBATCH --partition=cpu2019

####### Set environment variables ###############
#module load matlab/r2020a

# load personal version of python
export PATH=/home/siumichael.tang/software/miniconda3/envs/conda_mtang/bin:$PATH

####### Change directory to where script is located at #######
cd /work/levan_lab/mtang/elect_locate/sub27/code_py 

#which python

####### Run your script #########################
#matlab -batch "dynamic_analysis_falff_map"
#python -u ec_detect_script_5_1_1.py
bash run_test.bash
