'''
Created on 1 May 2018

@author: duncanfyfe
'''
import logging

import unittest

from dlapp.configuration import (
    ConfigPropertyValueNotSet,
    ConfigPropertyBadName, ConfigNamespaceDuplicateProperty,
    ConfigManagerMissingNamespace, ConfigNamespaceBadName,
    ConfigManagerBadVersion, ConfigManagerDuplicateNamespace, DEFAULT_NS)
import dlapp.configuration as configuration
import dlapp.logger as logger


logger.init()


class TestConfigurationMethods(unittest.TestCase):

    def test_configmanager05(self):
        '''
        Call ConfigManager.get_namespace with a bad namespace name.
        '''
        log = logging.getLogger(__name__)
        log.debug("BEGIN: unittest.TestCase.id=%r", unittest.TestCase.id(self))
        cfg = configuration.ConfigurationManager(version=1)
        eok = False

        try:
            cfg.get_namespace('!badname')
        except ConfigNamespaceBadName:
            eok = True
        self.assertTrue(eok)

    def test_configmanager06(self):
        '''
        Call ConfigManager.has_namespace with a bad namespace name.
        '''
        log = logging.getLogger(__name__)
        log.debug("BEGIN: unittest.TestCase.id=%r", unittest.TestCase.id(self))
        cfg = configuration.ConfigurationManager(version=1)
        eok = False

        try:
            cfg.has_namespace("!badname")
        except ConfigNamespaceBadName:
            eok = True
        self.assertTrue(eok)

    def test_configmanager07(self):
        '''
        Call ConfigManager.get_namespace with a bad namespace name.
        '''
        log = logging.getLogger(__name__)
        log.debug("BEGIN: unittest.TestCase.id=%r", unittest.TestCase.id(self))
        cfg = configuration.ConfigurationManager(version=1)
        eok = False

        try:
            cfg.get_namespace("!badname")
        except ConfigNamespaceBadName:
            eok = True
        self.assertTrue(eok)

    def test_configmanager08(self):
        '''
        Call ConfigManager.add_namespace with a bad namespace name.
        '''
        log = logging.getLogger(__name__)
        log.debug("BEGIN: unittest.TestCase.id=%r", unittest.TestCase.id(self))
        cfg = configuration.ConfigurationManager(version=1)
        eok = False

        try:
            cfg.add_namespace("!badname")
        except ConfigNamespaceBadName:
            eok = True
        self.assertTrue(eok)

    def test_configmanager09(self):
        '''
        Instantiate a ConfigManager with a bad version number.
        '''
        log = logging.getLogger(__name__)
        log.debug("BEGIN: unittest.TestCase.id=%r", unittest.TestCase.id(self))

        eok = False

        try:
            configuration.ConfigurationManager(version=2)
        except ConfigManagerBadVersion:
            eok = True
        self.assertTrue(eok)

    def test_configmanager10(self):
        '''
        Call ConfigManager.get_namespace with an existing namespace.
        '''
        log = logging.getLogger(__name__)
        log.debug("BEGIN: unittest.TestCase.id=%r", unittest.TestCase.id(self))
        cfg = configuration.ConfigurationManager(version=1)
        cfg.add_namespace(__name__)
        eok = False

        try:
            cfg.add_namespace(__name__)
        except ConfigManagerDuplicateNamespace:
            eok = True
        self.assertTrue(eok)

    def test_configmanager11(self):
        '''
        Instantiate a ConfigManager using the namespaces key.
        '''
        log = logging.getLogger(__name__)
        log.debug("BEGIN: unittest.TestCase.id=%r", unittest.TestCase.id(self))
        cfg = configuration.ConfigurationManager(version=1,
                                                 namespaces={'first': {},
                                                             'second': {}})
        self.assertTrue(cfg.has_namespace('first'))
        self.assertTrue(cfg.has_namespace('second'))

    def test_configmanager12(self):
        '''
        Call ConfigManager.add_namespace and ConfigManager.has_namespace with
        valid values.
        '''
        log = logging.getLogger(__name__)
        log.debug("BEGIN: unittest.TestCase.id=%r", unittest.TestCase.id(self))
        cfg = configuration.ConfigurationManager(version=1)
        cfg.add_namespace(__name__)
        self.assertTrue(cfg.has_namespace(__name__))

    def test_configmanager13(self):
        '''
        Call ConfigManager.add_namespace and ConfigManager.get_namespace with
        valid values.
        '''
        log = logging.getLogger(__name__)
        log.debug("BEGIN: unittest.TestCase.id=%r", unittest.TestCase.id(self))
        cfg = configuration.ConfigurationManager(version=1)
        cfg.add_namespace(__name__)
        ns = cfg.get_namespace(__name__)
        self.assertEqual(ns.name, __name__)

    def test_configmanager14(self):
        '''
        Call ConfigManager.parent_namespaces with only the default namespace
        available.
        '''
        log = logging.getLogger(__name__)
        log.debug("BEGIN: unittest.TestCase.id=%r", unittest.TestCase.id(self))
        cfg = configuration.ConfigurationManager(version=1)
        act = cfg.parent_namespaces(__name__)
        exp = [DEFAULT_NS]
        self.assertListEqual(exp, act)

    def test_configmanager15(self):
        '''
        Call ConfigManager.parent_namespaces with the default and one parent
        namespace available.
        '''
        log = logging.getLogger(__name__)
        log.debug("BEGIN: unittest.TestCase.id=%r", unittest.TestCase.id(self))
        cfg = configuration.ConfigurationManager(version=1)
        nm = __name__[0:__name__.rfind('.')]
        cfg.add_namespace(nm)
        act = cfg.parent_namespaces(__name__)
        exp = [nm, DEFAULT_NS]
        self.assertListEqual(exp, act)

    def test_configmanager16(self):
        '''
        Call ConfigManager.parent_namespaces with the default, one parent
        and this namespace available and one non-parent namespace.
        '''
        log = logging.getLogger(__name__)
        log.debug("BEGIN: unittest.TestCase.id=%r", unittest.TestCase.id(self))
        cfg = configuration.ConfigurationManager(version=1)
        nm = __name__[0:__name__.rfind('.')]
        cfg.add_namespace(__name__)
        cfg.add_namespace(nm)
        cfg.add_namespace("dlapp.alttree")
        act = cfg.parent_namespaces(__name__)
        exp = [__name__, nm, DEFAULT_NS]
        self.assertListEqual(exp, act)

    def test_configmanager17(self):
        '''
        Call ConfigManager.get_namespace with non existent namespace.
        '''
        log = logging.getLogger(__name__)
        log.debug("BEGIN: unittest.TestCase.id=%r", unittest.TestCase.id(self))
        cfg = configuration.ConfigurationManager(version=1)
        cfg.add_namespace("dlapp.alttree")
        eok = False
        try:
            cfg.get_namespace(__name__, ornearest=False)
        except ConfigManagerMissingNamespace:
            eok = True
        self.assertTrue(eok)

    def test_configmanager18(self):
        '''
        Call ConfigManager.get_namespace with the default, one parent
        available and ornearest True
        '''
        log = logging.getLogger(__name__)
        log.debug("BEGIN: unittest.TestCase.id=%r", unittest.TestCase.id(self))
        cfg = configuration.ConfigurationManager(version=1)
        nm = __name__[0:__name__.rfind('.')]
        cfg.add_namespace(nm)
        ns = cfg.get_namespace(__name__, ornearest=True)
        act = ns.name
        exp = nm
        self.assertEqual(exp, act)


if __name__ == '__main__':
    logger.init()
    unittest.main()
