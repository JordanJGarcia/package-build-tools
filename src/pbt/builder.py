#! /usr/bin/python3

"""
    File: pbt/builer.py

    Desc:
        pbt submodule containing package build utilities

    Usage:
        import pbt.builder
        from pbt.builder import builder
"""

import os
import re

from pathlib import Path

from pbt import logger
from pbt import validateargs
from pbt.executor import Executor

class Builder:
    """ class containing functions related to building/testing debian packages """

    def __init__(self):
        """ initializer """

        self.user = os.getenv('USER')
        self.exec = Executor()


    @validateargs
    def valid_dist(self, dist: str):
        """ True (success) | False (failure) """

        available_dists = self.get_files('/usr/share/debootstrap/scripts')

        if not available_dists:
            return False

        if dist not in available_dists:
            logger.error("invalid dist '%s', must be in %s", dist, available_dists)
            return False

        return True


    @validateargs
    def get_files(self, directory: str, extensions: list|None = None)
        """ list of files (success) | False (failure) """

        path = Path(directory)

        try:
            if extensions:
                return [f.name for f in path.iterdir() if f.is_file() and f.suffix in extensions]

            return [f.name for f in path.iterdir() if f.is_file()]
        except FileNotFoundError:
            logger.error("'%s' does not exist", directory)
            return False


    @validateargs
    def create_chroot(self, args: list):
        """ True (success) | False (failure) """

        assert len(args) == 1
        assert self.valid_dist(args[0])

        dist = args[0]

        # do these need sudo?
        cmds = (
            ['sudo', 'rm', '-f', f'base-{dist}-amd64.tar.xz'],
            ['sudo', f'DIST={dist}', 'pbuilder', 'create'],
            ['sudo', 'rm', '-r', '-f', f'base-{dist}-amd64.cow/'],
            ['sudo', f'DIST={dist}', 'cowbuilder', 'create']
        )

        for cmd in cmds:
            logger.info('running %s', cmd)

            result = self.exec.run(cmd)
            self.exec.print_details(result is False)

            if not result:
                break

        return result


    @validateargs
    def build_package(self, args: list):
        """ True (success) | False (failure) """

        assert len(args) == 2
        assert self.valid_dist(args[1])

        flag, dist = args
        valid_flags = ('tar', 'native', 'dist')

        if flag not in valid_flags:
            logger.error('flag must be one of %s, see DEBMAKE(1)', valid_flags)
            return False

        if not os.path.isdir('debian'):
            logger.error('could not find debian/ directory')
            return False

        logger.info('building in %s chroot...', dist)

        cmd = [
            'sudo', f'DIST={dist}',
            'debmake', f'--{flag}', '--yes', '--invoke',
            'pdebuild --pbuilder cowbuilder'
        ]

        result = self.exec.run(cmd)
        self.exec.print_details(result is False)

        return result


    @validateargs
    def sync_packages(self, args: list):
        """ True (success) | False (failure) """

        assert len(args) == 2

        dest, dist = args

        assert self.valid_dist(dist)
        assert len(dest.split('@')) == 2

        #debs = self.get_files(f'/var/cache/pbuilder/{dist}-amd64/result/', ['.deb'])
        debs = f'/var/cache/pbuilder/{dist}-amd64/result/*.deb'

        user, host = dest.split('@')

        if user != 'root':
            logger.error('need to be root on remote machine to sync packages')
            return False

        logger.info('syncing %s to %s', debs, dest)

        cmds = (
            ['scp', f'/home/{self.user}/.junk.list', f'{dest}:/etc/apt/sources.list.d/junk.list'],
            ['ssh', dest, '(mkdir ~/packages; apt-get install --yes rsync)'],
            ['rsync', '-avz', '--progress', '--partial', '--stats', '--delete', '{debs} {dest}:/root/packages/'],
            ['ssh', dest, " ".join(('(cd /root/packages;', 'apt-ftparchive packages . > Packages;', 'apt-ftparchive releaseeee . > Release);', 'apt-get update'))]
        )

        for cmd in cmds:
            logger.info('running %s', cmd)
            result = self.exec.run(cmd)
            self.exec.print_details(result is False)

            if not result:
                break

        return result
