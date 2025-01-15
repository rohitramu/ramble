# Copyright 2022-2025 The Ramble Authors
#
# Licensed under the Apache License, Version 2.0 <LICENSE-APACHE or
# https://www.apache.org/licenses/LICENSE-2.0> or the MIT license
# <LICENSE-MIT or https://opensource.org/licenses/MIT>, at your
# option. This file may not be copied, modified, or distributed
# except according to those terms.

import webbrowser

description = "open Ramble documentation in a web browser"
section = "help"
level = "short"


def docs(parser, args):
    webbrowser.open("https://ramble.readthedocs.io/")
