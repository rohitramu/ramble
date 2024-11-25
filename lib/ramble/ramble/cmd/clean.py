# Copyright 2022-2024 The Ramble Authors
#
# Licensed under the Apache License, Version 2.0 <LICENSE-APACHE or
# https://www.apache.org/licenses/LICENSE-2.0> or the MIT license
# <LICENSE-MIT or https://opensource.org/licenses/MIT>, at your
# option. This file may not be copied, modified, or distributed
# except according to those terms.


import argparse
import os
import shutil

import llnl.util.tty as tty
import spack.util.spack_yaml as syaml

import ramble.caches
import ramble.config
import ramble.repository
import ramble.reports
import ramble.stage
from ramble.util.logger import logger
from ramble.paths import lib_path, var_path

description = "remove temporary files and/or downloaded archives"
section = "cleanup"
level = "long"


class AllClean(argparse.Action):
    """Activates flags -d -m and -p simultaneously"""

    def __call__(self, parser, namespace, values, option_string=None):
        parser.parse_args(["-dmp"], namespace=namespace)


def setup_parser(subparser):
    subparser.add_argument(
        "-d", "--downloads", action="store_true", help="remove cached downloads (default)"
    )
    subparser.add_argument(
        "-m", "--misc-cache", action="store_true", help="remove long-lived caches"
    )
    subparser.add_argument(
        "-p",
        "--python-cache",
        action="store_true",
        help="remove .pyc, .pyo files and __pycache__ folders",
    )
    subparser.add_argument(
        "-r",
        "--reports",
        action="store_true",
        help="remove pdf and image files generated by ramble reports",
    )
    subparser.add_argument("-a", "--all", action=AllClean, help="equivalent to -dmp", nargs=0)


def clean(parser, args):
    # If nothing was set, activate the default
    if not any([args.downloads, args.misc_cache, args.python_cache, args.reports]):
        args.downloads = True

    if args.downloads:
        logger.msg("Removing cached downloads")
        ramble.caches.fetch_cache.destroy()

    if args.misc_cache:
        logger.msg("Removing cached information on repositories")
        ramble.caches.misc_cache.destroy()

    if args.python_cache:
        logger.msg("Removing python cache files")
        remove_python_caches()

    if args.reports:
        logger.msg("Removing pdf and image files generated by ramble reports")
        remove_reports_files()


def remove_python_caches():
    logger.msg("Removing python cache files")
    for directory in [lib_path, var_path]:
        for root, dirs, files in os.walk(directory):
            for f in files:
                if f.endswith(".pyc") or f.endswith(".pyo"):
                    fname = os.path.join(root, f)
                    logger.debug(f"Removing {fname}")
                    os.remove(fname)
            for d in dirs:
                if d == "__pycache__":
                    dname = os.path.join(root, d)
                    logger.debug(f"Removing {dname}")
                    shutil.rmtree(dname)


def remove_reports_files():
    reports_path = ramble.reports.get_reports_path()
    if reports_path:

        answer = tty.get_yes_or_no(
            f"Really remove all reports and images from {reports_path}?",
            default=False,
        )
        if not answer:
            logger.die("Will not remove any files")

        for root, _, files in os.walk(reports_path, topdown=False):
            inventory_file = os.path.join(root, ramble.reports.INVENTORY_FILENAME)

            try:
                with open(inventory_file) as f:
                    inventory = syaml.load(f)
            except FileNotFoundError:
                continue

            if inventory:
                for inv_file in inventory["files"]:
                    if inv_file in files:
                        fname = os.path.join(root, inv_file)
                        logger.debug(f"Removing {fname}")
                        os.remove(fname)
                logger.debug(f"Removing {inventory_file}")
                os.remove(inventory_file)

            if not os.listdir(root):
                logger.debug(f"Removing empty directory {root}")
                os.rmdir(root)

        # Clean up symlinks in root dir
        for item in os.listdir(reports_path):
            item_path = os.path.join(reports_path, item)
            if os.path.islink(item_path):
                logger.debug(f"Removing {item_path}")
                os.remove(item_path)
