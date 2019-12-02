#! /bin/bash
#SBATCH --partition=all
permutation_test.py --permutation $SLURM_ARRAY_TASK_ID
