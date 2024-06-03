# Copyright 2022-2024 The Ramble Authors
#
# Licensed under the Apache License, Version 2.0 <LICENSE-APACHE or
# https://www.apache.org/licenses/LICENSE-2.0> or the MIT license
# <LICENSE-MIT or https://opensource.org/licenses/MIT>, at your
# option. This file may not be copied, modified, or distributed
# except according to those terms.


from ramble.application import ApplicationBase
import ramble.spack_runner
import ramble.keywords

header_color = "@*b"
level1_color = "@*g"
plain_format = "@."


def section_title(s):
    return header_color + s + plain_format


def subsection_title(s):
    return level1_color + s + plain_format


class SpackApplication(ApplicationBase):
    """Specialized class for applications that are installed from spack.

    This class can be used to set up an application that will be installed
    via spack.

    It currently only utilizes phases defined in the base class.
    """

    uses_spack = True

    _spec_groups = [
        ("compilers", "Compilers"),
        ("mpi_libraries", "MPI Libraries"),
        ("software_specs", "Software Specs"),
    ]
    _spec_keys = ["pkg_spec", "compiler_spec", "compiler"]

    def __init__(self, file_path):
        super().__init__(file_path)

        self.keywords = ramble.keywords.keywords

        self.spack_runner = ramble.spack_runner.SpackRunner()
        self.application_class = "SpackApplication"
