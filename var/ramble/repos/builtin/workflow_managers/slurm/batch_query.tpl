#!/bin/bash

# Ensure job_id is present
job_id=$(< {experiment_run_dir}/.slurm_job)
if [ -z "${job_id:-}" ]; then
    echo "No valid job_id found" 1>&2
    exit 1
fi

status=$(squeue -h -o "%t" -j "${job_id}" 2>/dev/null)
if [ -z "$status" ]; then
    status=$(sacct -j "${job_id}" -o state -X -n | xargs)
fi
if [ ! -z "$status" ]; then
    # Define a mapping between sacct/squeue status to ramble counterpart
    declare -A status_map
    status_map["PD"]="SETUP"
    status_map["R"]="RUNNING"
    status_map["CF"]="SETUP"
    status_map["CG"]="COMPLETE"
    status_map["COMPLETED"]="COMPLETE"
    status_map["CANCELLED+"]="CANCELLED"
    if [ -v status_map["$status"] ]; then
        status=${status_map["$status"]}
    fi
fi
echo "job {job_name} with id ${job_id} has status: $status"
