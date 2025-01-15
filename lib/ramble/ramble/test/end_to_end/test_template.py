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

pytestmark = pytest.mark.usefixtures(
    "mutable_config", "mutable_mock_workspace_path", "mutable_mock_apps_repo"
)

workspace = RambleCommand("workspace")


def test_template():
    test_config = """
ramble:
  variables:
    mpi_command: mpirun -n {n_ranks}
    batch_submit: 'batch_submit {execute_experiment}'
    processes_per_node: 1
  applications:
    template:
      workloads:
        test_template:
          experiments:
            test:
              variables:
                n_nodes: 1
                hello_name: santa
"""
    workspace_name = "test_template"
    ws = ramble.workspace.create(workspace_name)
    ws.write()
    config_path = os.path.join(ws.config_dir, ramble.workspace.config_file_name)
    with open(config_path, "w+") as f:
        f.write(test_config)
    ws._re_read()

    workspace("setup", "--dry-run", global_args=["-w", workspace_name])
    run_dir = os.path.join(ws.experiment_dir, "template/test_template/test/")
    script_path = os.path.join(run_dir, "bar.sh")
    assert os.path.isfile(script_path)
    with open(script_path) as f:
        content = f.read()
        assert "echo foobar" in content
        assert "echo hello santa" in content
        assert "echo not_exist" not in content
    execute_path = os.path.join(run_dir, "execute_experiment")
    with open(execute_path) as f:
        content = f.read()
        assert script_path in content

    script_path = os.path.join(ws.shared_dir, "script.sh")
    assert os.path.isfile(script_path)


def test_template_inherited():
    test_config = """
ramble:
  variables:
    mpi_command: mpirun -n {n_ranks}
    batch_submit: 'batch_submit {execute_experiment}'
    processes_per_node: 1
    n_nodes: 1
  applications:
    template-inherited:
      workloads:
        test_template:
          experiments:
            test: {}
"""
    workspace_name = "test_template_inherited"
    ws = ramble.workspace.create(workspace_name)
    ws.write()
    config_path = os.path.join(ws.config_dir, ramble.workspace.config_file_name)
    with open(config_path, "w+") as f:
        f.write(test_config)
    ws._re_read()

    workspace("setup", "--dry-run", global_args=["-w", workspace_name])
    run_dir = os.path.join(ws.experiment_dir, "template-inherited/test_template/test/")
    script_path = os.path.join(run_dir, "bar.sh")
    assert os.path.isfile(script_path)
    with open(script_path) as f:
        content = f.read()
        assert "echo hello world-inherited" in content
    execute_path = os.path.join(run_dir, "execute_experiment")
    with open(execute_path) as f:
        content = f.read()
        assert script_path in content

    script_path = os.path.join(ws.shared_dir, "script.sh")
    assert os.path.isfile(script_path)
