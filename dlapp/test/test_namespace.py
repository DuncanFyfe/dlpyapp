'''
Created on 1 May 2018

@author: duncanfyfe
'''
import logging
from numbers import Number
import unittest

from dlapp.configuration import (
    ConfigNamespaceBadName,
    ConfigPropertyBadName, ConfigNamespaceDuplicateProperty)
import dlapp.configuration as configuration
import dlapp.logger as logger


logger.init()


class CallbackException(Exception):
    '''
    An exception which can be thrown to show the callback function was called.
    '''
    pass


class ValidationException(Exception):
    '''
    An exception which can be thrown to show the consequences of the
    validation function.
    '''
    pass


def tstcallback(name, value):
    '''
    A function which raises a CallbackException exception to demonstrate it
    was called. Used to test the callback functionality.
    '''
    log = logging.getLogger(__name__)
    log.debug("tstcallback(%r, %r)", name, value)
    raise CallbackException()


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


class TestConfigurationMethods(unittest.TestCase):

    def test_namespace01(self):
        '''
        '''
        log = logging.getLogger(__name__)
        log.debug("BEGIN: unittest.TestCase.id=%r", unittest.TestCase.id(self))
        name = 'foo'
        cr = configuration.ConfigNamespace(name)
        self.assertEqual(cr.name, name)

    def test_namespace02(self):
        '''
        Clear the singleton configuration manager.
        Get a configuration namespace (triggering instantiation of a
        new configuration manager).
        Add a property record without value, callable or validate arguments.
        Test the exception raised when a configuration record value is
        unset and the value is read.
        '''
        log = logging.getLogger(__name__)
        log.debug("BEGIN: unittest.TestCase.id=%r", unittest.TestCase.id(self))
        name = '!badname'
        eok = False
        try:
            configuration.ConfigNamespace(name)
        except ConfigNamespaceBadName:
            eok = True
        self.assertTrue(eok)

    def test_namespace03(self):
        '''
        '''
        log = logging.getLogger(__name__)
        log.debug("BEGIN: unittest.TestCase.id=%r", unittest.TestCase.id(self))
        name = 'foo'
        cr = configuration.ConfigNamespace(name, foo={'value': 5}, bar=7)
        self.assertEqual(cr.name, name)
        self.assertEqual(cr.foo.name, 'foo')
        self.assertEqual(cr.foo.value, 5)

    def test_namespace04(self):
        '''
        Clear the singleton configuration manager.
        Get a configuration namespace (triggering instantiation of a
        new configuration manager).
        Use the add_properties() interface.
        Test the correct properties were added.
        '''
        log = logging.getLogger(__name__)
        log.debug("BEGIN: unittest.TestCase.id=%r", unittest.TestCase.id(self))
        name = 'foo'
        cr = configuration.ConfigNamespace(name, foo={'value': 5}, bar=7)
        eok = False
        try:
            cr.has_property('!bad')
        except ConfigPropertyBadName:
            eok = True
        self.assertTrue(eok)

    def test_namespace05(self):
        '''
        '''
        log = logging.getLogger(__name__)
        log.debug("BEGIN: unittest.TestCase.id=%r", unittest.TestCase.id(self))
        name = 'foo'
        cr = configuration.ConfigNamespace(name, foo={'value': 5}, bar=7)
        self.assertTrue(cr.has_property('foo'))

    def test_namespace06(self):
        '''
        '''
        log = logging.getLogger(__name__)
        log.debug("BEGIN: unittest.TestCase.id=%r", unittest.TestCase.id(self))
        name = 'foo'
        cr = configuration.ConfigNamespace(name, foo={'value': 5}, bar=7)
        self.assertFalse(cr.has_property('Idonotexist'))

    def test_namespace07(self):
        '''
        '''
        log = logging.getLogger(__name__)
        log.debug("BEGIN: unittest.TestCase.id=%r", unittest.TestCase.id(self))
        name = 'foo'
        cr = configuration.ConfigNamespace(name, foo={'value': 5}, bar=7)
        cr.add_property('baz', value=9)
        self.assertEqual(cr.baz.value, 9)

    def test_namespace08(self):
        '''
        '''
        log = logging.getLogger(__name__)
        log.debug("BEGIN: unittest.TestCase.id=%r", unittest.TestCase.id(self))
        name = 'foo'
        cr = configuration.ConfigNamespace(name)
        cr.add_properties(properties={'foo': {'value': 5}, 'bar': 7})
        self.assertEqual(cr.foo.value, 5)

    def test_namespace09(self):
        '''
        '''
        log = logging.getLogger(__name__)
        log.debug("BEGIN: unittest.TestCase.id=%r", unittest.TestCase.id(self))
        name = 'foo'
        cr = configuration.ConfigNamespace(name)
        cr.add_properties(properties={'foo': {'value': 5}, 'bar': 7})
        act = "%r" % (cr,)
        log.debug("(1) ACTUAL=" + act)
        exp = ("ConfigNamespace(bar=<class "
               "'dlapp.configuration.ConfigPropertyRecordExt'>(bar , 7 ,"
               " callback=None , validate=None), foo=<class "
               "'dlapp.configuration.ConfigPropertyRecordExt'>(foo , 5 ,"
               " callback=None , validate=None), name='foo')")
        self.assertEqual(act, exp)

    def test_namespace10(self):
        '''
        '''
        log = logging.getLogger(__name__)
        log.debug("BEGIN: unittest.TestCase.id=%r", unittest.TestCase.id(self))
        name = 'foo'
        cr = configuration.ConfigNamespace(name, foo={'value': 5}, bar=7)
        eok = False
        try:
            cr.add_property('foo', value=9)
        except ConfigNamespaceDuplicateProperty:
            eok = True
        self.assertTrue(eok)

    def test_namespace11(self):
        '''
        '''
        log = logging.getLogger(__name__)
        log.debug("BEGIN: unittest.TestCase.id=%r", unittest.TestCase.id(self))
        name = 'foo'
        cr = configuration.ConfigNamespace(name, foo={'value': 5}, bar=7)
        eok = False
        try:
            cr.add_property('!badname', value=9)
        except ConfigPropertyBadName:
            eok = True
        self.assertTrue(eok)

    def test_namespace12(self):
        '''
        '''
        log = logging.getLogger(__name__)
        log.debug("BEGIN: unittest.TestCase.id=%r", unittest.TestCase.id(self))
        name = 'foo'
        cr = configuration.ConfigNamespace(name)
        eok = False
        try:
            cr.add_properties(properties={'foo': {'value': 5}, '!badname': 7})
        except ConfigPropertyBadName:
            eok = True
        self.assertTrue(eok)

    def test_namespace13(self):
        '''
        '''
        log = logging.getLogger(__name__)
        log.debug("BEGIN: unittest.TestCase.id=%r", unittest.TestCase.id(self))
        name = 'foo'
        cr = configuration.ConfigNamespace(name, foo={'value': 5}, bar=7)
        eok = False
        try:
            cr.add_properties(properties={'foo': {'value': 5}})
        except ConfigNamespaceDuplicateProperty:
            eok = True
        self.assertTrue(eok)


if __name__ == '__main__':
    logger.init()
    unittest.main()
