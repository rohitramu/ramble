#!/bin/bash
sbatch {slurm_execute_experiment} | tee >(awk '{print $NF}' > {experiment_run_dir}/.slurm_job)
