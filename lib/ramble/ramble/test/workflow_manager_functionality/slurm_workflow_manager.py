# Copyright 2022-2025 The Ramble Authors
#
# Licensed under the Apache License, Version 2.0 <LICENSE-APACHE or
# https://www.apache.org/licenses/LICENSE-2.0> or the MIT license
# <LICENSE-MIT or https://opensource.org/licenses/MIT>, at your
# option. This file may not be copied, modified, or distributed
# except according to those terms.

import os

import pytest

import ramble.workspace
from ramble.main import RambleCommand

workspace = RambleCommand("workspace")

pytestmark = pytest.mark.usefixtures(
    "mutable_config",
    "mutable_mock_workspace_path",
)


def test_slurm_workflow():
    workspace_name = "test_slurm_workflow"

    test_config = """
ramble:
  variants:
    workflow_manager: '{wm_name}'
  variables:
    # This batch_submit is overridden with slurm workflow manager
    batch_submit: echo {wm_name}
    mpi_command: mpirun -n {n_ranks} -hostfile hostfile
    processes_per_node: 1
    wm_name: ['None', 'slurm']
  applications:
    hostname:
      workloads:
        local:
          experiments:
            test_{wm_name}:
              variables:
                n_nodes: 1
                extra_sbatch_headers: "#SBATCH --gpus-per-task={n_threads}"
"""
    with ramble.workspace.create(workspace_name) as ws:
        ws.write()
        config_path = os.path.join(ws.config_dir, ramble.workspace.config_file_name)
        with open(config_path, "w+") as f:
            f.write(test_config)
        ws._re_read()
        workspace("setup", "--dry-run", global_args=["-D", ws.root])

        # assert the batch_submit is overridden, pointing to the generated script
        all_exec_file = os.path.join(ws.root, "all_experiments")
        with open(all_exec_file) as f:
            content = f.read()
            assert "echo None" in content
            assert "echo slurm" not in content
            assert os.path.join("hostname", "local", "test_slurm", "batch_submit") in content

        # Assert on no workflow manager
        path = os.path.join(ws.experiment_dir, "hostname", "local", "test_None")
        files = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]
        assert "slurm_execute_experiment" not in files
        assert "batch_submit" not in files
        assert "batch_query" not in files
        assert "batch_cancel" not in files

        # Assert on slurm workflow manager
        path = os.path.join(ws.experiment_dir, "hostname", "local", "test_slurm")
        files = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]
        assert "slurm_execute_experiment" in files
        assert "batch_submit" in files
        assert "batch_query" in files
        assert "batch_cancel" in files
        with open(os.path.join(path, "batch_submit")) as f:
            content = f.read()
            assert "slurm_execute_experiment" in content
            assert ".slurm_job" in content
        with open(os.path.join(path, "slurm_execute_experiment")) as f:
            content = f.read()
            assert "scontrol show hostnames" in content
            assert "#SBATCH --gpus-per-task=1" in content
        with open(os.path.join(path, "batch_query")) as f:
            content = f.read()
            assert "squeue" in content
        with open(os.path.join(path, "batch_cancel")) as f:
            content = f.read()
            assert "scancel" in content
