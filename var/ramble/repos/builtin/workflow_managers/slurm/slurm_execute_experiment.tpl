#!/bin/bash
{sbatch_headers_str}

cd {experiment_run_dir}

scontrol show hostnames > {experiment_run_dir}/hostfile

{command}
