'''
Created on 1 May 2018

@author: duncanfyfe
'''
import logging
from numbers import Number
import unittest

from dlapp.configuration import (
    ConfigManagerMissingNamespace,
    DEFAULT_NS,
    ConfigNamespaceBadName,
    ConfigPropertyNotFound, ConfigPropertyBadName)
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

    def test_getConfigManager01(self):
        '''
        Call getConfigManager check the returned manager is the same as
        the singleton version and the default namespace was created.
        '''
        log = logging.getLogger(__name__)
        log.debug("BEGIN: unittest.TestCase.id=%r", unittest.TestCase.id(self))
        configuration.configuration_manager = None
        cfg = configuration.getConfigManager()
        self.assertEqual(configuration.configuration_manager, cfg)

        self.assertTrue(
            DEFAULT_NS in configuration.configuration_manager.namespaces)

    def test_getConfigManager02(self):
        '''
        Call getConfigManager check the returned manager is the same as
        the singleton version.
        '''
        log = logging.getLogger(__name__)
        log.debug("BEGIN: unittest.TestCase.id=%r", unittest.TestCase.id(self))
        configuration.configuration_manager = None
        configuration.getConfigManager(dlapp={'foo': {'value': 7}})
        self.assertTrue(
            'dlapp' in configuration.configuration_manager.namespaces)

    def test_getconfig01(self):
        '''
        Clear the singleton configuration manager.
        Get a configuration namespace (triggering instantiation of a
        new configuration manager).
        Use the add_properties() interface.
        Test the correct properties were added.
        '''
        log = logging.getLogger(__name__)
        log.debug("BEGIN: unittest.TestCase.id=%r", unittest.TestCase.id(self))
        configuration.configuration_manager = None
        configuration.getConfig(
            __name__, False, properties={
                'foo': {
                    'value': 5}, 'bar': 7})
        cfg = configuration.getConfig(
            __name__, False, properties={
                'baz': {
                    'value': 1}, 'aaa': 2})
        self.assertEqual(cfg.baz.value, 1)
        self.assertEqual(cfg.aaa.value, 2)

    def test_getconfig02(self):
        '''
        Trigger the creation of a parent namespace.
        Test that the parent namespace is retrieved by default.
        '''
        log = logging.getLogger(__name__)
        log.debug("BEGIN: unittest.TestCase.id=%r", unittest.TestCase.id(self))
        configuration.configuration_manager = None
        configuration.getConfig('dlapp')
        cfg = configuration.getConfig()
        log.debug("cfg.name=%r", cfg.name)
        self.assertEqual(cfg.name, 'dlapp')
#

    def test_getconfig03(self):
        '''
        Trigger the creation of a non-parent namespace.
        Test that the default namespace is returned.
        '''
        log = logging.getLogger(__name__)
        log.debug("BEGIN: unittest.TestCase.id=%r", unittest.TestCase.id(self))
        configuration.configuration_manager = None
        configuration.getConfig('foobar')
        cfg = configuration.getConfig()
        log.debug("cfg.name=%r", cfg.name)
        self.assertEqual(cfg.name, configuration.DEFAULT_NS)

    def test_getconfig04(self):
        '''
        Trigger the creation of a parent namespace.
        Test that ornearest=False causes an exception rather than the
        parent namespace to be returned.
        '''
        log = logging.getLogger(__name__)
        log.debug("BEGIN: unittest.TestCase.id=%r", unittest.TestCase.id(self))
        configuration.configuration_manager = None
        configuration.getConfig('dlapp')
        eok = False
        try:
            configuration.getConfig(ornearest=False)
        except ConfigManagerMissingNamespace:
            eok = True
        self.assertTrue(eok)
#

    def test_getconfig05(self):
        '''
        Trigger the creation of a non-parent namespace.
        Test that ornearest=False causes an exception rather than the
        default namespace to be returned.
        '''
        log = logging.getLogger(__name__)
        log.debug("BEGIN: unittest.TestCase.id=%r", unittest.TestCase.id(self))
        configuration.configuration_manager = None
        configuration.getConfig('foobar')
        eok = False
        try:
            configuration.getConfig(ornearest=False)
        except ConfigManagerMissingNamespace:
            eok = True
        self.assertTrue(eok)

    def test_getConfigRecord01(self):
        '''
        Create a property record then retrieve it using the getConfigRecord
        function.
        '''
        log = logging.getLogger(__name__)
        log.debug("BEGIN: unittest.TestCase.id=%r", unittest.TestCase.id(self))
        configuration.configuration_manager = None
        configuration.getConfig(
            __name__, False, properties={
                'foo': {
                    'value': 5}, 'bar': 7})
        p = configuration.getConfigRecord(__name__ + ".foo")
        self.assertEqual(p.name, "foo")
        self.assertEqual(p.value, 5)

    def test_getConfigRecord02(self):
        '''
        call getConfigRecord with nonexistent property name
        '''
        log = logging.getLogger(__name__)
        log.debug("BEGIN: unittest.TestCase.id=%r", unittest.TestCase.id(self))
        configuration.configuration_manager = None
        configuration.getConfig(
            __name__, False, properties={
                'foo': {
                    'value': 5}, 'bar': 7})
        eok = False
        try:
            configuration.getConfigRecord(__name__ + ".baz")
        except ConfigPropertyNotFound:
            eok = True
        self.assertTrue(eok)

    def test_getConfigRecord03(self):
        '''
        call getConfigRecord with a bad namespace name
        '''
        log = logging.getLogger(__name__)
        log.debug("BEGIN: unittest.TestCase.id=%r", unittest.TestCase.id(self))
        configuration.configuration_manager = None
        configuration.getConfig(
            __name__, False, properties={
                'foo': {
                    'value': 5}, 'bar': 7})
        eok = False
        try:
            configuration.getConfigRecord("!badname.baz")
        except ConfigNamespaceBadName:
            eok = True
        self.assertTrue(eok)

    def test_getConfigRecord04(self):
        '''
        call getConfigRecord with a bad property name
        '''
        log = logging.getLogger(__name__)
        log.debug("BEGIN: unittest.TestCase.id=%r", unittest.TestCase.id(self))
        configuration.configuration_manager = None
        configuration.getConfig(
            __name__, False, properties={
                'foo': {
                    'value': 5}, 'bar': 7})
        eok = False
        try:
            configuration.getConfigRecord("good.!badname")
        except ConfigPropertyBadName:
            eok = True
        self.assertTrue(eok)

    def test_getConfigRecord05(self):
        '''
        Call getConfigRecord without a namespace element to the name
        '''
        log = logging.getLogger(__name__)
        log.debug("BEGIN: unittest.TestCase.id=%r", unittest.TestCase.id(self))
        configuration.configuration_manager = None
        configuration.getConfig(
            __name__, False, properties={
                'foo': {
                    'value': 5}, 'bar': 7})
        p = configuration.getConfigRecord("foo")
        self.assertEqual(p.name, "foo")
        self.assertEqual(p.value, 5)

    def test_getConfigRecord06(self):
        '''
        Call getConfigRecord where the property exists in the default rather
        than current namespace and ornearest is True
        '''
        log = logging.getLogger(__name__)
        log.debug("BEGIN: unittest.TestCase.id=%r", unittest.TestCase.id(self))
        configuration.configuration_manager = None
        configuration.getConfig(
            DEFAULT_NS, False, properties={
                'foo': {
                    'value': 5}, 'bar': 7})
        p = configuration.getConfigRecord("foo", True)
        self.assertEqual(p.name, "foo")
        self.assertEqual(p.value, 5)

    def test_getConfigRecord07(self):
        '''
        Call getConfigRecord where the property exists in the default rather
        than current namespace and ornearest is False
        '''
        log = logging.getLogger(__name__)
        log.debug("BEGIN: unittest.TestCase.id=%r", unittest.TestCase.id(self))
        configuration.configuration_manager = None
        configuration.getConfig(
            DEFAULT_NS, False, properties={
                'foo': {
                    'value': 5}, 'bar': 7})
        eok = False
        try:
            configuration.getConfigRecord("foo", False)
        except ConfigPropertyNotFound:
            eok = True
        self.assertTrue(eok)

    def test_getConfigRecord08(self):
        '''
        Call getConfigRecord with an empty name.
        '''
        log = logging.getLogger(__name__)
        log.debug("BEGIN: unittest.TestCase.id=%r", unittest.TestCase.id(self))
        configuration.configuration_manager = None
        configuration.getConfig(
            DEFAULT_NS, False, properties={
                'foo': {
                    'value': 5}, 'bar': 7})
        eok = False
        try:
            configuration.getConfigRecord("", False)
        except ConfigPropertyBadName:
            eok = True
        self.assertTrue(eok)


if __name__ == '__main__':
    logger.init()
    unittest.main()
