'''
Created on 1 May 2018

@author: duncanfyfe
'''
import logging
from numbers import Number
import os
import unittest

from dlapp.configuration import (AppConfig, DEFAULT_NS)
import dlapp.configuration as configuration
import dlapp.logger as logger


logger.init()


class ValidationException(Exception):
    '''
    An exception which can be thrown to show the consequences of the
    validation function.
    '''
    pass


def tstvalidate(name, value):
    '''
    A function to demonstrate value validation.  It raises a
    ValidationException if the given value is not numerical or it falls
    outside the range 1 to 9 inclusive.
    '''
    log = logging.getLogger(__name__)
    log.debug("tstvalidate(%r, %r)", name, value)
    if isinstance(value, Number):
        if value > 0 and value < 10:
            log.debug("validate: PASSED")
            return True
    log.debug("validate: FAILED")
    raise ValidationException(value)


def reformat(name, value):
    log = logging.getLogger(__name__)
    log.debug('reformat %r', value)
    return 2 * value


def reformatstr(name, value):
    return int(value, 10)


class TestApplicationConfig(unittest.TestCase):

    def test_appconfig01(self):
        '''
        Create property record, verify the name and value.
        '''
        log = logging.getLogger(__name__)
        log.debug("BEGIN: unittest.TestCase.id=%r", unittest.TestCase.id(self))
        configuration.configuration_manager = None
        cns = configuration.getConfig(__name__)
        name = 'foo'
        app_prop = __name__ + "." + name
        p = cns.add_property(name, value=5, validate=tstvalidate)

        dcfg = {'first': {'second': {name: 3}}}
        appcfg = AppConfig(
            app_prop,
            dictconfig=dcfg,
            dictalias=[[
                'first',
                'second',
                'foo']], dictformat=reformat)
        appcfg.resolve()
        self.assertEqual(6, p.value)

    def test_appconfig02(self):
        '''
        Create property record, verify the name and value.
        '''
        log = logging.getLogger(__name__)
        log.debug("BEGIN: unittest.TestCase.id=%r", unittest.TestCase.id(self))
        configuration.configuration_manager = None
        cns = configuration.getConfig(DEFAULT_NS)
        name = 'foo'
        app_prop = __name__ + "." + name
        p = cns.add_property(name, value=5, validate=tstvalidate)

        dcfg = {'first': {'second': {name: 3}}}
        appcfg = AppConfig(
            app_prop,
            dictconfig=dcfg,
            dictalias=[[
                'first',
                'second',
                'foo']], dictformat=reformat)
        appcfg.value = 9
        self.assertEqual(9, p.value)

    def test_appconfig03(self):
        '''
        Create property record, verify the name and value.
        '''
        log = logging.getLogger(__name__)
        log.debug("BEGIN: unittest.TestCase.id=%r", unittest.TestCase.id(self))
        configuration.configuration_manager = None
        cns = configuration.getConfig(__name__)
        name = 'foo'
        app_prop = __name__ + "." + name
        p = cns.add_property(name, value=5, validate=tstvalidate)
        appcfg = AppConfig(app_prop)
        appcfg.value = 6
        x = appcfg.value
        self.assertEqual(x, p.value)

    def test_appconfig04(self):
        '''
        Create property record, verify the name and value.
        '''
        log = logging.getLogger(__name__)
        log.debug("BEGIN: unittest.TestCase.id=%r", unittest.TestCase.id(self))
        configuration.configuration_manager = None
        cns = configuration.getConfig(DEFAULT_NS)
        name = 'foo'
        app_prop = __name__ + "." + name
        p = cns.add_property(name, value=5, validate=tstvalidate)

        dcfg = {'first': {'second': {name: 3}}}
        appcfg = AppConfig(app_prop)
        appcfg.set_dictalias(dictconfig=dcfg, dictalias=[
            ['first', 'second', 'foo']], dictformat=reformat)
        appcfg.resolve()
        dns = configuration.getConfig(DEFAULT_NS)
        nns = configuration.getConfig(__name__)
        log.debug("DEFAULT_NS=%r", dns)
        log.debug("__name__=%r", nns)

        self.assertEqual(3, p.value)

    def test_appconfig05(self):
        '''
        Create property record, verify the name and value.
        '''
        log = logging.getLogger(__name__)
        log.debug("BEGIN: unittest.TestCase.id=%r", unittest.TestCase.id(self))
        configuration.configuration_manager = None
        cns = configuration.getConfig(DEFAULT_NS)
        name = 'foo'
        app_prop = __name__ + "." + name
        p = cns.add_property(name, value=5, validate=tstvalidate)

        dcfg = {'first': {'second': {name: 1}}}
        envvar = 'TEST_QRGSRYBPFJES'
        log.debug("Environemt Variable: %r", envvar)
        value = 3
        os.environ[envvar] = "%s" % (value,)

        appcfg = AppConfig(app_prop, envalias=[envvar], envformat=reformatstr)
        appcfg.set_dictalias(dictconfig=dcfg, dictalias=[
            ['first', 'second', 'foo']], dictformat=reformat)
        appcfg.resolve()
        self.assertEqual(value, p.value)

    def test_appconfig06(self):
        '''
        Create property record, verify the name and value.
        '''
        log = logging.getLogger(__name__)
        log.debug("BEGIN: unittest.TestCase.id=%r", unittest.TestCase.id(self))
        configuration.configuration_manager = None
        cns = configuration.getConfig(__name__)
        name = 'foo'
        app_prop = __name__ + "." + name
        p = cns.add_property(name, value=5, validate=tstvalidate)

        appcfg = AppConfig(
            app_prop, default_value=9)
        appcfg.resolve()
        self.assertEqual(9, p.value)


if __name__ == '__main__':
    logger.init()
    unittest.main()
