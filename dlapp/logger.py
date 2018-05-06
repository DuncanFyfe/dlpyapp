#!/usr/bin/env python3
# encoding: utf-8
'''
Created on 19 Apr 2018

@author: duncanfyfe
'''
import copy
import json
import logging
from logging.config import dictConfig
import os
import sys


class LoggerConfDoesNotExist(Exception):
    '''
    Exception to raise if a logging configuration file does not exist.
    '''

    def __init__(self, msg):
        super().__init__(self)
        self.msg = 'Logging configuration file does not exist: %r' % (msg,)


class _DebugInfoOnly(logging.Filter):
    '''
    Logging filter which keeps only DEBUG and INFO messages.
    Default logging configuration uses this to split DEBUG and INFO messages
    to stdout and WARNING and above messages to stderr.
    '''

    def __init__(self):
        super().__init__()

    def filter(self, record):
        return record.levelno <= logging.INFO


# This should equal the logging module default log level.
DEFAULT_LOGLEVEL = logging.WARNING

# Default logging configuration if none othewr is provided.
DEFAULT_LOGGING_CONFIG = dict(
    version=1,
    disable_existing_loggers=False,
    formatters={
        'default': {'format':
                    '%(asctime)s %(name)-12s [%(filename)s:%(lineno)d] \
                   %(levelname)-8s %(message)s'}
    },
    filters={
        "debug_info_only": {
            '()': _DebugInfoOnly
        }
    },
    handlers={
        "console_stdout": {
            "class": "logging.StreamHandler",
            "level": "DEBUG",
            "formatter": "default",
            "stream": "ext://sys.stdout",
            "filters": ['debug_info_only']
        },
        "console_stderr": {
            "class": "logging.StreamHandler",
            "level": "WARNING",
            "formatter": "default",
            "stream": "ext://sys.stderr"
        }
    },
    root={
        'handlers': ['console_stdout', 'console_stderr'],
        'level': logging.DEBUG,
    },
)


def load_json_config(configfile):
    ''' Load a json formatted dictionary of logging configuration
        information.  Throw exceptions if the given file cannot be read or
        there is an error parsing the file contents.
    '''
    rtn = {}
    if os.path.exists(configfile) and os.path.isfile(configfile):
        try:
            with open(configfile, 'r', encoding='utf-8') as fp:
                tmp = json.load(fp)
                rtn = tmp

        except json.JSONDecodeError as e:
            print(
                "Error parsing logging configuration file: %r" %
                (configfile,), file=sys.stderr)
            print(e, file=sys.stderr)
            raise e
        except IOError as e:
            print(
                "IOError opening logging configuration file: " %
                (configfile,), file=sys.stderr)
            print(e, file=sys.stderr)
            raise e
        except KeyboardInterrupt as e:
            print(
                "Interrupted reading logging configuration file: " %
                (configfile), file=sys.stderr)
            print(e, file=sys.stderr)
            raise e
        except Exception as e:
            print(
                "Unexpected exception reading logging configuration file: "
                + str(configfile), file=sys.stderr)
            print(e, file=sys.stderr)
            raise e
    else:
        raise LoggerConfDoesNotExist(configfile)
    return rtn


def adjust_loglevel(logging_config=DEFAULT_LOGGING_CONFIG,
                    verbosity=0, quiet=0):
    ''' It is assumed the effect of the verbosity level is to lower the
        log level by -10  for every '-v' down to 0.  The effect of every quiet
        level is to raise the log level by 10.
        If either is set then the configured root (and/or '') logging level
        is chenged.
    '''
    config = copy.deepcopy(logging_config)
    try:
        loglevel_delta = 0
        if quiet:
            loglevel_delta = 10 * quiet
        if verbosity:
            loglevel_delta -= 10 * verbosity

        if loglevel_delta:
            for name in ['root', '']:
                cfg_level = config.get(name, None)
                if cfg_level:
                    level = cfg_level.get(
                        'level', DEFAULT_LOGLEVEL) + loglevel_delta
                    if level < 0:
                        level = 0
                    config[name]['level'] = level

    except KeyboardInterrupt as e:
        print(
            "Interrupted adjusting loglevel.", file=sys.stderr)
        print(e, file=sys.stderr)
        raise e
    except Exception as e:
        print(
            "Unexpected exception adjusting loglevel.")
        print(e, file=sys.stderr)
        raise e
    return config


def init(logging_config=DEFAULT_LOGGING_CONFIG,
         verbosity=0, quiet=0):
    '''
    Configure logging
    '''
    dictConfig(logging_config)


def _runtest():
    '''
    Manual test if logging works.
    '''
    init()
    logger = logging.getLogger(__name__)
    logger.debug('Test debug message')
    logger.info('Test info message')
    logger.warning('Test warning message')
    logger.error('Test error message')


if __name__ == '__main__':
    _runtest()
