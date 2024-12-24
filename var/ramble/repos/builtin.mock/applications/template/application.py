# Copyright 2022-2024 The Ramble Authors
#
# Licensed under the Apache License, Version 2.0 <LICENSE-APACHE or
# https://www.apache.org/licenses/LICENSE-2.0> or the MIT license
# <LICENSE-MIT or https://opensource.org/licenses/MIT>, at your
# option. This file may not be copied, modified, or distributed
# except according to those terms.

from ramble.appkit import *


class Template(ExecutableApplication):
    """An app for testing object templates."""

    name = "template"

    executable("foo", template=["bash {bar}"])

    workload("test_template", executable="foo")

    workload_variable(
        "hello_name",
        default="world",
        description="hello name",
        workload="test_template",
    )

    register_phase(
        "ingest_dynamic_variables",
        pipeline="setup",
        run_before=["make_experiments"],
    )

    def _ingest_dynamic_variables(self, workspace, app_inst):
        expander = self.expander
        val = expander.expand_var('"hello {hello_name}"')
        self.define_variable("dynamic_hello_world", val)

    register_template("bar", src_name="bar.tpl", dest_name="bar.sh")
