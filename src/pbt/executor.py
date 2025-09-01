#! /usr/bin/python3

"""
    File: pbt/executor.py

    Desc:
        Initializer for pbt submodule whos purpose
        is to execute commands.

    Usage:
        import pbt.executor
        from pbt.executor import Executor
"""

import subprocess

from pbt import logger
from pbt import validateargs

class Executor:
    """ A class containing functions to run commands """

    def __init__(self):
        """ initializer """

        self._stdout = None
        self._stderr = None
        self._rc = 0
        self._command = []


    @validateargs
    def run(self, cmd: list, env: dict|None=None) -> bool:
        """ True (success) | False (failure) """

        self.command = cmd

        if env:
            proc = subprocess.run(cmd, env=env, capture_output=True, text=True, check=False)
        else:
            proc = subprocess.run(cmd, capture_output=True, text=True, check=False)

        self.rc = proc.returncode
        self.stdout = proc.stdout
        self.stderr = proc.stderr

        if self.rc != 0:
            self.print_details(True)
            return False

        self.print_details()
        return True


    @property
    def command(self) -> list|None:
        """ list | None """

        return self._command


    @command.setter
    @validateargs
    def command(self, value: list):
        """ returns nothing """

        self._command = value


    @validateargs
    def print_details(self, verbose: bool=False):
        """ print details of last run command """

        logger.info('%s returned %s', self.command, self.rc)

        if verbose:
            if self.stdout:
                formatted = ['\t' + line for line in self.stdout.split('\n')]
                logger.info("\n\nstdout:\n\n%s", '\n'.join(formatted))

            if self.stderr:
                formatted = ['\t' + line for line in self.stderr.split('\n')]
                logger.info("\n\nstderr:\n\n%s", '\n'.join(formatted))


    @property
    def rc(self):
        """ int """

        return self._rc


    @rc.setter
    @validateargs
    def rc(self, value: int):
        """ returns nothing """

        self._rc = value


    @property
    def stdout(self) -> str|None:
        """ str|None """

        return self._stdout


    @stdout.setter
    @validateargs
    def stdout(self, value: str|None):
        """ returns nothing """

        self._stdout = value


    @property
    def stderr(self) -> str|None:
        """ str|None """

        return self._stderr


    @stderr.setter
    @validateargs
    def stderr(self, value: str|None):
        """ returns nothing """

        self._stderr = value
