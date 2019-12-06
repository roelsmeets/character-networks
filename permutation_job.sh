#! /bin/bash
#SBATCH --partition=medium
permutation_test.py --permutation $SLURM_ARRAY_TASK_ID
