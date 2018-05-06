'''
Created on 1 May 2018

@author: duncanfyfe
'''
import logging
from numbers import Number
import unittest

from dlapp.configuration import (
    ConfigPropertyValueNotSet,
    ConfigPropertyBadName)
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

    def test_propertyrecord01(self):
        '''
        Create property record, verify the name and value.
        '''
        log = logging.getLogger(__name__)
        log.debug("BEGIN: unittest.TestCase.id=%r", unittest.TestCase.id(self))
        name = 'foo'
        val = 7
        cr = configuration.ConfigPropertyRecord(name, value=val)
        self.assertEqual(cr.name, name)
        self.assertEqual(cr.value, val)
#

    def test_propertyrecord02(self):
        '''
        Create property record without a value.  Confirm correct exception
        is raised if the unset value is accessed.
        '''
        log = logging.getLogger(__name__)
        log.debug("BEGIN: unittest.TestCase.id=%r", unittest.TestCase.id(self))
        name = 'foo'
        cr = configuration.ConfigPropertyRecord(name)
        eok = False
        try:
            cr.value
        except ConfigPropertyValueNotSet:
            eok = True
        self.assertTrue(eok)

    def test_propertyrecord03(self):
        '''
        Create property record and check it is serialized (repr) correctly.
        '''
        log = logging.getLogger(__name__)
        log.debug("BEGIN: unittest.TestCase.id=%r", unittest.TestCase.id(self))
        name = 'foo'
        val = 7
        cr = configuration.ConfigPropertyRecord(name, value=val)
        act = "%r" % (cr,)

        exp = "<class 'dlapp.configuration.ConfigPropertyRecord'>(foo , 7)"
        self.assertEqual(act, exp)

    def test_propertyrecord04(self):
        '''
        Create property record without a value and check it is serialized
        (repr) correctly.
        '''
        log = logging.getLogger(__name__)
        log.debug("BEGIN: unittest.TestCase.id=%r", unittest.TestCase.id(self))
        name = 'foo'
        cr = configuration.ConfigPropertyRecord(name)
        act = "%r" % (cr,)
        exp = ("<class 'dlapp.configuration.ConfigPropertyRecord'>(foo"
               " , '(unset)')")
        self.assertEqual(act, exp)

    def test_propertyrecord05(self):
        '''
        Create a property. Set then test a new name.
        '''
        log = logging.getLogger(__name__)
        log.debug("BEGIN: unittest.TestCase.id=%r", unittest.TestCase.id(self))
        name = 'foo'
        val = 7
        cr = configuration.ConfigPropertyRecord(name, value=val)
        cr.name = 'bar'
        self.assertEqual(cr.name, 'bar')
        self.assertEqual(cr.value, val)

    def test_propertyrecord06(self):
        '''
        Create a property. Try to set a bad name, test the exception raised.
        '''
        log = logging.getLogger(__name__)
        log.debug("BEGIN: unittest.TestCase.id=%r", unittest.TestCase.id(self))
        name = 'foo'
        cr = configuration.ConfigPropertyRecord(name)
        eok = False
        try:
            cr.name = "!badname"
        except ConfigPropertyBadName:
            eok = True
        self.assertTrue(eok)

    def test_propertyrecord07(self):
        '''
        Create a property with a value.  Change the value and test the
        returned value is correct.
        '''
        log = logging.getLogger(__name__)
        log.debug("BEGIN: unittest.TestCase.id=%r", unittest.TestCase.id(self))
        name = 'foo'
        val = 7
        cr = configuration.ConfigPropertyRecord(name, value=val)
        cr.value = 3
        self.assertEqual(cr.name, name)
        self.assertEqual(cr.value, 3)

    def test_propertyrecordext01(self):
        '''
        Create an extended property record, verify the name and value.
        '''
        log = logging.getLogger(__name__)
        log.debug("BEGIN: unittest.TestCase.id=%r", unittest.TestCase.id(self))
        name = 'foo'
        val = 7
        cr = configuration.ConfigPropertyRecordExt(name, value=val)
        self.assertEqual(cr.name, name)
        self.assertEqual(cr.value, val)
#

    def test_propertyrecordext02(self):
        '''
        Create an extended property record without a value.  Confirm correct
        exception is raised if the unset value is accessed.
        '''
        log = logging.getLogger(__name__)
        log.debug("BEGIN: unittest.TestCase.id=%r", unittest.TestCase.id(self))
        name = 'foo'
        cr = configuration.ConfigPropertyRecordExt(name)
        eok = False
        try:
            cr.value
        except ConfigPropertyValueNotSet:
            eok = True
        self.assertTrue(eok)

    def test_propertyrecordext03(self):
        '''
        Create property record and check it is serialized (repr) correctly.
        '''
        log = logging.getLogger(__name__)
        log.debug("BEGIN: unittest.TestCase.id=%r", unittest.TestCase.id(self))
        name = 'foo'
        val = 7
        cr = configuration.ConfigPropertyRecordExt(name, value=val)
        act = "%r" % (cr,)
        exp = ("<class 'dlapp.configuration.ConfigPropertyRecordExt'>(foo ,"
               " 7 , callback=None , validate=None)")
        self.assertEqual(act, exp)

    def test_propertyrecordext04(self):
        '''
        Create property record without a value and check it is serialized
        (repr) correctly.
        '''
        log = logging.getLogger(__name__)
        log.debug("BEGIN: unittest.TestCase.id=%r", unittest.TestCase.id(self))
        name = 'foo'
        cr = configuration.ConfigPropertyRecordExt(name)
        act = "%r" % (cr,)
        exp = ("<class 'dlapp.configuration.ConfigPropertyRecordExt'>(foo , "
               "'(unset)' , callback=None , validate=None)")
        self.assertEqual(act, exp)

    def test_propertyrecordext05(self):
        '''
        Create a property. Set then test a new name.
        '''
        log = logging.getLogger(__name__)
        log.debug("BEGIN: unittest.TestCase.id=%r", unittest.TestCase.id(self))
        name = 'foo'
        val = 7
        cr = configuration.ConfigPropertyRecordExt(name, value=val)
        cr.name = 'bar'
        self.assertEqual(cr.name, 'bar')
        self.assertEqual(cr.value, val)

    def test_propertyrecordext06(self):
        '''
        Create a property. Try to set a bad name, test the exception raised.
        '''
        log = logging.getLogger(__name__)
        log.debug("BEGIN: unittest.TestCase.id=%r", unittest.TestCase.id(self))
        name = 'foo'
        cr = configuration.ConfigPropertyRecordExt(name)
        eok = False
        try:
            cr.name = "!badname"
        except ConfigPropertyBadName:
            eok = True
        self.assertTrue(eok)

    def test_propertyrecordext07(self):
        '''
        Create a property with a value.  Use the copy constructor to
        create a new, identical property record.
        '''
        log = logging.getLogger(__name__)
        log.debug("BEGIN: unittest.TestCase.id=%r", unittest.TestCase.id(self))
        name = 'foo'
        cr = configuration.ConfigPropertyRecordExt(name, value=5)
        cr2 = configuration.ConfigPropertyRecordExt(cr)
        self.assertEqual(cr2.name, cr.name)
        self.assertEqual(cr2.value, cr.value)

    def test_propertyrecordext08(self):
        '''
        Validate call should not be called during instantiation - valid value
        '''
        log = logging.getLogger(__name__)
        log.debug("BEGIN: unittest.TestCase.id=%r", unittest.TestCase.id(self))
        value = 5
        cr = configuration.ConfigPropertyRecordExt(
            'foo', value=value, validate=tstvalidate)
        self.assertEqual(cr.value, value)

    def test_propertyrecordext09(self):
        '''
        Validate call should not be called during instantiation - different
        type.
        '''
        log = logging.getLogger(__name__)
        log.debug("BEGIN: unittest.TestCase.id=%r", unittest.TestCase.id(self))
        value = 'foo'
        cr = configuration.ConfigPropertyRecordExt(
            'foo', value=value, validate=tstvalidate)
        self.assertEqual(cr.value, value)

    def test_propertyrecordext10(self):
        '''
        Validate call should not be called during instantiation -
        out of (valid) range value
        '''
        log = logging.getLogger(__name__)
        log.debug("BEGIN: unittest.TestCase.id=%r", unittest.TestCase.id(self))
        value = -1
        cr = configuration.ConfigPropertyRecordExt(
            'foo', value=value, validate=tstvalidate)
        self.assertEqual(cr.value, value)

    def test_propertyrecordext11(self):
        '''
        Validate call should not be called during instantiation - no value
        '''
        log = logging.getLogger(__name__)
        log.debug("BEGIN: unittest.TestCase.id=%r", unittest.TestCase.id(self))
        cr = configuration.ConfigPropertyRecordExt(
            'foo', validate=tstvalidate)
        eok = False
        try:
            cr.value
        except ConfigPropertyValueNotSet:
            eok = True
        self.assertTrue(eok)

    def test_propertyrecordext12(self):
        '''
        Validate call should occur during value assignment - valid value.
        '''
        log = logging.getLogger(__name__)
        log.debug("BEGIN: unittest.TestCase.id=%r", unittest.TestCase.id(self))
        value = 5
        cr = configuration.ConfigPropertyRecordExt(
            'foo', value=value, validate=tstvalidate)
        cr.value = 3
        self.assertEqual(cr.value, 3)

    def test_propertyrecordext13(self):
        '''
        Validate call should occur during value assignment - out of range.
        '''
        log = logging.getLogger(__name__)
        log.debug("BEGIN: unittest.TestCase.id=%r", unittest.TestCase.id(self))
        value = 5
        cr = configuration.ConfigPropertyRecordExt(
            'foo', value=value, validate=tstvalidate)
        eok = False
        try:
            cr.value = -1
        except ValidationException:
            eok = True
        self.assertTrue(eok)

    def test_propertyrecordext14(self):
        '''
        Validate call should occur during value assignment - wrong type
        '''
        log = logging.getLogger(__name__)
        log.debug("BEGIN: unittest.TestCase.id=%r", unittest.TestCase.id(self))
        value = 5
        cr = configuration.ConfigPropertyRecordExt(
            'foo', value=value, validate=tstvalidate)
        eok = False
        try:
            cr.value = "foo"
        except ValidationException:
            eok = True
        self.assertTrue(eok)

    def test_propertyrecordext15(self):
        '''
        Test that callback occurs on assignment.
        '''
        log = logging.getLogger(__name__)
        log.debug("BEGIN: unittest.TestCase.id=%r", unittest.TestCase.id(self))
        value = 5
        cr = configuration.ConfigPropertyRecordExt(
            'foo', value=value, validate=tstvalidate, callback=tstcallback)
        eok = False
        try:
            cr.value = 3
        except CallbackException:
            eok = True
        self.assertTrue(eok)


if __name__ == '__main__':
    logger.init()
    unittest.main()
