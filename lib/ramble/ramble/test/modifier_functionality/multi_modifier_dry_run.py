# Copyright 2022-2023 Google LLC
#
# Licensed under the Apache License, Version 2.0 <LICENSE-APACHE or
# https://www.apache.org/licenses/LICENSE-2.0> or the MIT license
# <LICENSE-MIT or https://opensource.org/licenses/MIT>, at your
# option. This file may not be copied, modified, or distributed
# except according to those terms.

import os

import pytest

from ramble.test.modifier_functionality.modifier_helpers import *
import ramble.workspace
from ramble.main import RambleCommand


workspace = RambleCommand('workspace')


@pytest.mark.parametrize(
    'scopes',
    [
        [SCOPES.workspace, SCOPES.workspace],
        [SCOPES.workspace, SCOPES.application],
        [SCOPES.workspace, SCOPES.workload],
        [SCOPES.workspace, SCOPES.experiment],
        [SCOPES.application, SCOPES.workspace],
        [SCOPES.application, SCOPES.application],
        [SCOPES.application, SCOPES.workload],
        [SCOPES.application, SCOPES.experiment],
        [SCOPES.workload, SCOPES.workspace],
        [SCOPES.workload, SCOPES.application],
        [SCOPES.workload, SCOPES.workload],
        [SCOPES.workload, SCOPES.experiment],
        [SCOPES.experiment, SCOPES.workspace],
        [SCOPES.experiment, SCOPES.application],
        [SCOPES.experiment, SCOPES.workload],
        [SCOPES.experiment, SCOPES.experiment],
    ]
)
@pytest.mark.parametrize(
    'factories,answers',
    [
        ([intel_aps_modifier, lscpu_modifier], [intel_aps_answer, lscpu_answer]),
    ]
)
def test_gromacs_multi_modifier_dry_run(mutable_mock_workspace_path,
                                        mutable_applications,
                                        scopes, factories, answers):
    workspace_name = 'test_gromacs_multi_modifier_dry_run'

    test_modifiers = []

    for scope, factory in zip(scopes, factories):
        test_modifiers.append((scope, factory()))

    software_tests = []
    script_tests = []
    for answer in answers:
        sw_test, script_test = answer()
        for sw in sw_test:
            software_tests.append(sw)
        for script in script_test:
            script_tests.append(script)

    with ramble.workspace.create(workspace_name) as ws1:
        ws1.write()

        config_path = os.path.join(ws1.config_dir, ramble.workspace.config_file_name)

        dry_run_config(test_modifiers, config_path)

        ws1._re_read()

        workspace('concretize', global_args=['-D', ws1.root])
        workspace('setup', '--dry-run', global_args=['-D', ws1.root])

        # Test software directories
        software_base_dir = ws1.software_dir

        check_software_env(software_base_dir, software_tests)

        exp_script = os.path.join(ws1.experiment_dir, 'gromacs', 'water_bare',
                                  'test_exp', 'execute_experiment')

        check_execute_script(exp_script, script_tests)
