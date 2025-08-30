#! /usr/bin/python3

"""
    File: pbt/executor.py

    Desc:
        pbt submodule whos purpose is to execute commands.

    Usage:
        import pbt.executor
        from pbt.executor import Executor
"""

import subprocess

from pbt import logger
from pbt import validateargs

class Executor:
    """ A class encapsulating functions to run commands """

    def __init__(self):
        """ initializer """

        self.command = []
        self.results = {
            'code': 0,
            'stdin': "",
            'stdout': "",
            'stderr': ""
        }


    @validateargs
    def run(self, cmd: list):
        """ True (success) | False (failure) """

        self.set_command(cmd)
        proc = subprocess.run(cmd, capture_output=True, text=True, check=False)
        self.set_results(proc.stderr, proc.stdout, proc.returncode)

        return proc.returncode == 0

   
   @validateargs
   def set_command(self, command: list):
       """ returns nothing """

       self.command = command


    @validateargs
    def set_results(self, err: str, out: str, code: int):
        """ returns nothing """

        self.results['stdout'] = out
        self.results['stderr'] = err
        self.results['code'] = code


    def get_results(self, verbose: bool=False):
        """ return instance results """

        return self.results


    @validateargs
    def print_details(self, verbose: bool=False):
        """ print details of last run command """

        logger.info('%s returned %s', self.command, self.results['code'])

        if verbose:
            if self.results['stdin']:
                formatted = ['\t' + line for line in self.results['stdin'].split('\n')]
                logger.info("\n\nstdin:\n\n%s", '\n'.join(formatted))

            if self.results['stdout']:
                formatted = ['\t' + line for line in self.results['stdout'].split('\n')]
                logger.info("\n\nstdout:\n\n%s", '\n'.join(formatted))

            if self.results['stderr']:
                formatted = ['\t' + line for line in self.results['stderr'].split('\n')]
                logger.info("\n\nstderr:\n\n%s", '\n'.join(formatted))


    @validate_args
    def set_stdin(self, inp: str):
        """ returns nothing """

        self.results['stdin'] = inp


    def get_stdin(self):
        """ returns stdin for last run command """

        return self.results['stdin']  


    @validate_args
    def set_stdout(self, out: str):
        """ returns nothing """

        self.results['stdout'] = out


    def get_stdout(self):
        """ returns stdout for last run command """

        return self.results['stdout']  


    @validate_args
    def set_stderr(self, err: str):
        """ returns nothing """

        self.results['stderr'] = err


    def get_stderr(self):
        """ returns stderr for last run command """

        return self.results['stderr']  


