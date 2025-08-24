#! /usr/bin/python3

"""
    File: pbt/__init__.py

    Desc:
        Initializer for the pbt python package.

    Usage:
        import pbt
        from pbt import logger
        from pbt import validateargs
"""

import sys
import logging
import inspect

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s | %(levelname)s | %(module)s.%(funcName)s():%(lineno)1d => %(message)s",
    handlers = [
        logging.FileHandler('/var/log/pbt.log'),
        logging.StreamHandler(sys.stderr)
    ]
)

logger = logging.getLogger(__name__)

def validateargs(func):
    """ validate arg types against type annotations """

    signature = inspect.signature(func)

    def argvalidator(*args, **kwargs):
        """ nothing (success) | raise exception (failure) """

        boundargs = signature.bind(*args, **kwargs)
        boundargs.apply_defaults()

        for param, arg in boundargs.arguments.items():
            if param in ['self']:
                continue

            type_annotation = signature.parameters[param].annotation

            if type_annotation is inspect.Parameter.empty:
                raise TypeError(
                    f"parameter '{param}' missing type annotation (required)"
                )

            if not isinstance(arg, type_annotation):
                raise TypeError(
                    f"arg '{name}' => expected: '{type_annotation}', recieved: '{type(value)}'"
                )

            return func(*args, **kwargs)
        return argvalidator
