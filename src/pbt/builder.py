#! /usr/bin/python3

"""
    File: pbt/builer.py

    Desc:
        Initializer for pbt submodule containing
        package build utilities

    Usage:
        import pbt.builder
        from pbt.builder import builder
"""

import os
import glob

from pbt import logger
from pbt import validateargs

from pbt.executor import Executor

class Builder:
    """ functions related to building/testing debian packages """

    def __init__(self):
        """ initializer """

        self.user = os.getenv('USER')
        self.executor = Executor()


    ##########
    # static #
    ##########

    @staticmethod
    @validateargs
    def valid_dist(dist: str) -> bool:
        """ True (success) | False (failure) """

        available_dists = Builder.get_files("/usr/share/debootstrap/scripts/*")

        if not available_dists:
            logger.error("no dists found")
            return False

        if dist not in available_dists:
            logger.error("invalid dist '%s', must be in %s", dist, available_dists)
            return False

        return True


    @staticmethod
    def list_dists():
        """ returns nothing """

        dists = Builder.get_files("/usr/share/debootstrap/scripts/*")

        logger.info("Available dists to create chroots for:\n\n\t%s",
                    "\n\t".join([", ".join(dists[i:i+6]) for i in range(0, len(dists), 6)]))


    @staticmethod
    def list_chroots():
        """ returns nothing """

        chroots = Builder.get_files("/var/cache/pbuilder/*.cow")

        logger.info("Available chroots to build packages against:\n\n\t%s",
                    "\n\t".join([", ".join(chroots[i:i+6]) for i in range(0, len(chroots), 6)]))


    @staticmethod
    @validateargs
    def get_files(path: str) -> list|bool:
        """ list of files (success) | False (failure) """

        return [os.path.basename(p) for p in glob.glob(path)]



    ############
    # instance #
    ############

    @validateargs
    def create_chroot(self, dist: str) -> bool:
        """ True (success) | False (failure) """

        if not Builder.valid_dist(dist):
            return False

        # must be run with sudo because dirs are owned by root
        cmds = (
            ['sudo', 'rm', '-f', f'/var/cache/pbuilder/base-{dist}-amd64.tar.xz'],
            ['sudo', f'DIST={dist}', 'pbuilder', 'create'],
            ['sudo', 'rm', '-r', '-f', f'/var/cache/pbuilder/base-{dist}-amd64.cow/'],
            ['sudo', f'DIST={dist}', 'cowbuilder', 'create']
        )

        for cmd in cmds:
            logger.info('running %s', cmd)

            if not self.executor.run(cmd):
                return False

        return True


    @validateargs
    def build_package(self, dist: str, flag: str, use_deps: bool=False) -> bool:
        """ True (success) | False (failure) """

        if not Builder.valid_dist(dist):
            return False

        valid_flags = ("tar", "native", "dist")

        if flag not in valid_flags:
            logger.error("flag must be one of %s, see DEBMAKE(1)", valid_flags)
            return False

        if not os.path.isdir("debian"):
            logger.error("could not find debian/ directory")
            return False

        result_dir = f"/var/cache/pbuilder/{dist}-amd64/result/"
        logger.info("building in %s chroot...", dist)
        logger.info("deb will be placed in %s", result_dir)

        env = os.environ.copy()
        env["DIST"] = dist

        if use_deps:
            env["DEPS"] = "y"

        cmd = [
            "debmake", f"--{flag}", "--yes", "--invoke",
            "pdebuild --pbuilder cowbuilder"
        ]

        logger.debug("running [%s%s%s]",
                     f"DIST='{env['DIST']}' ",
                     f"DEPS='{env['DEPS']}' " if use_deps else "",
                     " ".join([f"'{c}'" if " " in c else c for c in cmd]))

        return self.executor.run(cmd, env)
