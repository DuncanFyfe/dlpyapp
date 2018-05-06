'''
Application configuration classes which separate module configuration from
application defined configuration setting.
'''
import inspect
import logging
import os
import re


NS_SEP = '.'
DEFAULT_NS = '__DEFAULT'
UNSET_STR = '(unset)'
DEFAULT_CONFIG_VERSION = 1
VALID_NS_NAMES = "([A-Za-z][_a-zA-Z0-9]*)(\.?[_A-Za-z][_a-zA-Z0-9]*)*$"
VALID_PROPERTY_NAMES = "[A-Za-z][_a-zA-Z0-9]*$"


def ispropertynamevalid(name):
    '''
    Test if the given name is valid as a property name.
    Names starting with an underscore are considered internal to a module and
    therefore not suitable to be set by an external configuration.
    '''
    return name and re.match(VALID_PROPERTY_NAMES, name)


def isnsnamevalid(name):
    '''
    Test if the given name is valid as a namespace name.
    Names starting with an underscore are considered internal to a module and
    therefore not suitable to be used by an external configuration.
    '''
    return name and (name == DEFAULT_NS or re.match(VALID_NS_NAMES, name))


class ConfigPropertyValueNotSet(Exception):
    '''
    Exception to raise if a value is requested from a value which
    has not been set and for which there is no default
    '''

    def __init__(self, msg):
        super().__init__(self)
        self.msg = '%r value not set' % (msg,)


class ConfigPropertyBadName(Exception):
    '''
    Exception raised when a property name is inavlid (must match
    "[A-Za-z][_a-zA-Z0-9]*$")
    '''

    def __init__(self, msg):
        super().__init__(self)
        self.msg = 'Invalid property name: %r' % (msg,)


class ConfigPropertyNotFound(Exception):
    '''
    Exception raised when a property name is searched for and cannot be found.
    '''

    def __init__(self, msg):
        super().__init__(self)
        log = logging.getLogger(__name__)
        log.error("BUGGER OFF " + msg)
        self.msg = 'Property not found: %r' % (msg,)


class ConfigNamespaceDuplicateProperty(Exception):
    '''
    Exception raised when a property name is added more than once.
    '''

    def __init__(self, msg):
        super().__init__(self)
        self.msg = 'Duplicate property name: %r' % (msg,)


class ConfigNamespaceBadName(Exception):
    '''
    Exception raised when a property name is invalid (must match
    "[A-Za-z][_a-zA-Z0-9]*$")
    '''

    def __init__(self, msg):
        super().__init__(self)
        self.msg = 'Invalid Namespace name: %r' % (msg,)


class ConfigManagerBadVersion(Exception):
    '''
    Exception raised when given an unknown ConfigManager version.
    '''

    def __init__(self, msg):
        super().__init__(self)
        self.msg = 'Unknown Configuration Manager version number: %r' % (msg,)


class ConfigManagerDuplicateNamespace(Exception):
    '''
    Exception thrown if a namespace with the same name is added more than once.
    '''

    def __init__(self, msg):
        super().__init__(self)
        self.msg = 'Duplicate namespace: %r' % (msg,)


class ConfigManagerMissingNamespace(Exception):
    '''
    Exception thrown if a namespace is asked for, it does not exist and
    namespace walking has been supressed.
    '''

    def __init__(self, msg):
        super().__init__(self)
        self.msg = 'No namespace found: %r' % (msg,)


class ConfigPropertyRecord(object):
    '''
    Name and value property record.  An unset value is not the same as a
    value of None. A property can be instantiated with no value. In this case
    a ConfigPropertyValueNotSet exception is raised if an unset value is read.

    '''

    def __init__(self, name, **kwargs):
        '''
        name, value
        '''
        log = logging.getLogger(__name__)
        log.debug("ConfigPropertyRecord(%r,%r)", name, kwargs)
        self._name = name
        if 'value' in kwargs:
            self._value = kwargs['value']
            self._hasvalue = True
        else:
            self._value = None
            self._hasvalue = False

    def __repr__(self):

        val = UNSET_STR
        if self._hasvalue:
            val = self._value

        return '%s(%s , %r)' % (self.__class__, self._name, val, )

    @property
    def name(self):
        '''
        Property name getter.
        '''
        return self._name

    @name.setter
    def name(self, name):
        '''
        Property name setter.  Tests if the property name matches the regexp
        given by VALID_PROPERTY_NAMES and raises a ConfigPropertyBadName
        exception if it does not.
        '''
        log = logging.getLogger(__name__)
        log.debug("ConfigPropertyRecord.name(%r)", name)
        if name != self._name:
            if ispropertynamevalid(name):
                self._name = name
            else:
                raise ConfigPropertyBadName(name)
        return self._name

    @property
    def value(self):
        '''
        Property value getter.
        '''
        log = logging.getLogger(__name__)
        log.debug(
            "ConfigPropertyRecord.value(), _hasvalue=%r", self._hasvalue)
        if not self._hasvalue:
            raise ConfigPropertyValueNotSet(self.name)
        return self._value

    @value.setter
    def value(self, value):
        '''
        Property value setter.
        '''
        log = logging.getLogger(__name__)
        log.debug("ConfigPropertyRecord.value(%r)", value)
        self._value = value
        self._hasvalue = True
        return self._value


class ConfigPropertyRecordExt(ConfigPropertyRecord):
    '''
    Property record extended with optional validation function and
    callback function.

    The validation function, if given, must take the property name, current
    value and proposed
    new value as arguments. It is called before the object value is changed and
    should throw the desired exception if the given value is invalid.
    Any return value is ignored.

    The callback function, if given, must take the property name and new value
    as arguments. It is called after the object value is changed.
    Any return value is ignored.
    '''

    def __init__(self, name, **kwargs):
        '''
        name, (default) value, callback=callback function,
        validate=value validation function
        '''
        log = logging.getLogger(__name__)
        log.debug("ConfigPropertyRecordExt(%r,%r)", name, kwargs)
        if isinstance(name, ConfigPropertyRecord):
            # Copy constructor.
            self.__dict__.update(name.__dict__)
        else:
            # Capture the callback function
            callback = None
            if 'callback' in kwargs:
                callback = kwargs.pop('callback')
            # Capture the validation function
            validate = None
            if 'validate' in kwargs:
                validate = kwargs.pop('validate')
            # Initialize the base object
            super().__init__(name, **kwargs)
            # Then add the callback and validation function, assuming the base
            # object instantiation didn't throw an exception.
            self.callback = callback
            self.validate = validate

    def __repr__(self):
        '''
        Representation of ConfigPropertyRecordExt
        '''
        val = UNSET_STR
        if self._hasvalue:
            val = self._value

        return '%s(%s , %r , callback=%r , validate=%r)' % (
            self.__class__, self.name, val, self.callback, self.validate)

    @ConfigPropertyRecord.value.setter
    def value(self, value):
        '''
        Property value setter with callbacks and validation.
        '''
        log = logging.getLogger(__name__)
        log.debug("ConfigPropertyRecordExt.value(%r)", value)
        if self.validate and callable(self.validate):
            log.debug(
                "ConfigPropertyRecordExt.validate(%r , %r)", self.name, value)
            self.validate(self.name, value)
            log.debug("Validation Passed.")

        self._value = value
        self._hasvalue = True
        if self.callback and callable(self.callback):
            log.debug(
                "ConfigPropertyRecordExt.callback(%r , %r)", self.name,
                self._value)
            self.callback(self.name, self._value)
        return self._value


config_property_record_factory = ConfigPropertyRecordExt


class ConfigNamespace(object):
    '''
    Module side Configuration namespace.
    '''

    def __init__(self, nspc, **kwargs):
        log = logging.getLogger(__name__)
        log.debug("ConfigNamespace(%r,%r)", nspc, kwargs)
        # either Foo(name1=att1, name2=att2)
        # or Foo(properties={name1=att1, name2=att2})
        # properties={} form allows for future expansion eg. Foo(properties={},
        # other=[]) etc
        if not isnsnamevalid(nspc):
            raise ConfigNamespaceBadName(nspc)
        self.name = nspc
        if kwargs:
            self.add_properties(**kwargs)

    def __repr__(self):
        keys = sorted(self.__dict__)
        items = ("{}={!r}".format(k, self.__dict__[k]) for k in keys)
        return "{}({})".format(type(self).__name__, ", ".join(items))

    __str__ = __repr__

    def has_property(self, name):
        '''
        Does a property with the given name exist, Returns True or False.
        Raises a ConfigNamespaceBadName exception if the given name does
        not match the regexp given by VALID_PROPERTY_NAMES
        '''
        log = logging.getLogger(__name__)
        log.debug("ConfigNamespace.has_property(%r)", name)
        if not ispropertynamevalid(name):
            raise ConfigPropertyBadName(name)

        return name in self.__dict__

    def add_property(self, name, **kwargs):
        '''
        Use the config_property_record_factory to add a property record to
        this namespace.
        Add a property with the given name and arguments given by kwargs.
        Raises ConfigNamespaceBadName if the name cannot be validated with the
        VALID_PROPERTY_NAMES pattern.
        Raises ConfigNamespaceDuplicateProperty if the name already exists.
        '''
        log = logging.getLogger(__name__)
        log.debug("ConfigNamespace.add_property(%r,%r)", name, kwargs)
        if not ispropertynamevalid(name):
            raise ConfigPropertyBadName(name)
        if name in self.__dict__:
            raise ConfigNamespaceDuplicateProperty(name)
        log.debug("config_property_record_factory=%r",
                  (config_property_record_factory,))
        prop = config_property_record_factory(name, **kwargs)
        pdict = {name: prop}
        self.__dict__.update(pdict)
        return getattr(self, name)

    def add_properties(self, **kwargs):
        '''
        Add multiple properties in one go.
        '''
        rtn = {}
        log = logging.getLogger(__name__)
        log.debug("ConfigNamespace.add_properties(%r)", kwargs)
        properties = {}
        if 'properties' in kwargs:
            properties = kwargs['properties']
        else:
            properties = kwargs

        # Construct all records first so if one fails, they all fail.
        log.debug("config_property_record_factory=%r",
                  config_property_record_factory)
        props = {}
        for name, defn in properties.items():
            # Ignore keys that are not valid method names.
            # That means these keys can also be used to extend
            # functionality later.
            log.debug(
                "ConfigNamespace.add_properties - instantiating(%r)", name)
            if not ispropertynamevalid(name):
                raise ConfigPropertyBadName(name)
            if name in self.__dict__:
                raise ConfigNamespaceDuplicateProperty(name)
            if isinstance(defn, dict):
                props[name] = config_property_record_factory(name, **defn)
            else:
                props[name] = config_property_record_factory(name, value=defn)

        if props:

            self.__dict__.update(props)
            for name in props.keys():
                rtn[name] = getattr(self, name)

        return rtn


configuration_namespace_factory = ConfigNamespace


class ConfigurationManager(object):
    '''
    Typically a singleton instance used to manage all module
    configuration information for an application.
    '''

    def __init__(self, version=1, **kwargs):
        log = logging.getLogger(__name__)
        log.debug("ConfigurationManager(version=%r, %r)", version, kwargs)
        if version not in [1]:
            raise ConfigManagerBadVersion(version)
        self.version = version
        self.namespaces = {}
        namespaces = {}

        if 'namespaces' in kwargs:
            namespaces = kwargs['namespaces']
        else:
            namespaces = kwargs

        nspc = {}
        log.debug(
            "configuration_namespace_factory=%r",
            configuration_namespace_factory)
        for name, defn in namespaces.items():
            log.debug(
                "configuration_namespace_factory(%r, %r)", name, defn)
            nspc[name] = configuration_namespace_factory(name, **defn)

        if DEFAULT_NS not in nspc:
            log.debug("configuration_namespace_factory(%r)", DEFAULT_NS)
            nspc[DEFAULT_NS] = configuration_namespace_factory(DEFAULT_NS)

        self.namespaces.update(nspc)

    def _parents(self, nspc):
        rtn = []
        if nspc in self.namespaces:
            rtn.append(nspc)

        i = nspc.rfind(NS_SEP)
        if i > -1:
            nspc = nspc[0:i]
            rtn.extend(self._parents(nspc))
        return rtn

    def parent_namespaces(self, nspc):
        '''
        Namespaces are in a pseudo a.b.c hierarchy.  Given a.b.c returns a list
        of parent namespaces which are known to the configuration manager.
        ['b.c','c',DEFAULT_NS]
        '''
        log = logging.getLogger(__name__)
        log.debug("ConfigurationManager.parent_namespaces(%r)", nspc)
        return [*self._parents(nspc), DEFAULT_NS]

    def has_namespace(self, nspc):
        '''
        Test if a namespace with the given name exists in this configuraton
        manager.
        '''
        log = logging.getLogger(__name__)
        log.debug("ConfigurationManager.has_namespace(%r)", nspc)
        if not isnsnamevalid(nspc):
            raise ConfigNamespaceBadName(nspc)
        return nspc in self.namespaces

    def add_namespace(self, nspc, **kwargs):
        '''
        Instantiate a new namespace in this configuration manager
        '''
        log = logging.getLogger(__name__)
        log.debug("ConfigurationManager.add_namespace(%r, %r)", nspc, kwargs)
        if not isnsnamevalid(nspc):
            raise ConfigNamespaceBadName(nspc)

        log.debug(
            "configuration_namespace_factory=%r",
            configuration_namespace_factory)
        if nspc in self.namespaces:
            raise ConfigManagerDuplicateNamespace(
                'Namespace %s already exists.' % (nspc))
        log.debug(
            "configuration_namespace_factory(%r, %r)", nspc, kwargs)
        self.namespaces[nspc] = configuration_namespace_factory(
            nspc, **kwargs)
        return self.namespaces[nspc]

    def get_namespace(self, nspc, ornearest=True):
        '''
        Return the namespace with the given name.  If ornearest is True then
        if the namespace does not exist then look to the parents ending up
        at the default namespace if no others exists.
        If the namespace does not exist and ornearest is false a
        ConfigManagerMissingNamespace exception is raised.
        '''
        log = logging.getLogger(__name__)
        log.debug(
            "ConfigurationManager.get_namespace(%r, %r)", nspc, ornearest)
        if not isnsnamevalid(nspc):
            raise ConfigNamespaceBadName(nspc)

        if nspc in self.namespaces:
            return self.namespaces[nspc]
        else:
            if ornearest:
                nspc = self.parent_namespaces(nspc)[0]
                return self.namespaces[nspc]
            else:
                raise ConfigManagerMissingNamespace(nspc)


configuration_manager_factory = ConfigurationManager

configuration_manager = None


def getConfigManager(**kwargs):
    '''
    Get the (singleton) configuration manager. Instantiate it if this has
    not already happened.
    '''
    log = logging.getLogger(__name__)
    log.debug("getConfigManager(%r)", kwargs)
    global configuration_manager
    if not configuration_manager:
        log.debug(
            "configuration_manager_factory=%r", configuration_manager_factory)
        log.debug("instantiating new configuration_manager.")
        configuration_manager = configuration_manager_factory(1, **kwargs)
    return configuration_manager


def getConfig(nspc=None, ornearest=True, **kwargs):
    '''
    Get a configuration namespace from the (singleton) configuration manager.
    If nspc is None then look for one using the current module __name__ as the
    starting point.
    If nspc is a valid name then return an existing namespace or create a new
    one by that name.
    '''
    log = logging.getLogger(__name__)
    log.debug("getConfig(nspc=%r, ornearest=%r)", nspc, ornearest)
    mgr = getConfigManager()

    if nspc:

        if mgr.has_namespace(nspc):
            log.debug("Using existing ConfigManager namespace %r", nspc)
            rtn = mgr.get_namespace(nspc)
            if kwargs:
                rtn.add_properties(**kwargs)
        else:
            log.debug("Creating new ConfigManager namespace %r", nspc)
            rtn = mgr.add_namespace(nspc, **kwargs)
    else:
        nspc = inspect.getmodule(inspect.stack()[1][0]).__name__
        log.debug("using namespace %r", nspc)
        rtn = mgr.get_namespace(nspc, ornearest=ornearest)
    return rtn


def getConfigRecord(fqname, ornearest=True):
    '''
    Given an package.modue.name find and return the
    ConfigRecord appropriate to namespace(package.modue) -> record(name).
    If ornearest is true then search parent namespaces if the given one
    does not contain the requested name.
    '''
    log = logging.getLogger(__name__)
    log.debug("getConfigRecord(fqname=%r, ornearest=%r)", fqname, ornearest)
    if not fqname:
        raise ConfigPropertyBadName(fqname)
    p = fqname.rfind(NS_SEP)
    if p >= 0:
        nspc = fqname[0:p]
        propname = fqname[p + 1:]
    else:
        nspc = inspect.getmodule(inspect.stack()[1][0]).__name__
        propname = fqname
    log.debug("namespace = %r", nspc)
    log.debug("propname = %r", propname)

    if not isnsnamevalid(nspc):
        raise ConfigNamespaceBadName(nspc)
    if not ispropertynamevalid(propname):
        raise ConfigPropertyBadName(propname)

    ns = getConfig(nspc, ornearest)
    if ns.has_property(propname):
        return getattr(ns, propname)
    elif ornearest:
        for nss in getConfigManager().parent_namespaces(nspc):
            nsp = getConfig(nss, False)
            if nsp.has_property(propname):
                return getattr(nsp, propname)

    raise ConfigPropertyNotFound(fqname)


class AppConfig(object):
    '''
    Application side configuration property wrapper.
    Takes the fully qualified name of a module property record and
    possible input aliases.  When resolve is called the highest
    priority available source is used to set the property record value.
    Formatting functions can also be given which take the name of the property
    and the input format value and are expected to return a new value in the
    form needed by the module.
    The inbuilt priority is (highest to lowest):
        command line argument, environment variable, configuration parser,
        dictionary

    The configuration parser parts expect has_option() and get() methods which
    compatible with configparser.

    The dictionary parts are happy with nested dictionary keys and allow,
    for example, configurations to be read from json files.

    The configuration property can also be swet by assignment to the AppConfig
    value attribute (obj.value = v)
    '''

    def _argalias(self):
        '''
        Try to set the property value from a given argument parser.
        argalias should be the argparser namespace member (eg. parser.foo)
        '''
        log = logging.getLogger(__name__)
        log.debug("BEGIN _argalias")
        rtn = False
        if self.argalias is not None:
            val = None
            if callable(self.argalias):
                val = self.argalias()
            else:
                val = self.argalias
            log.debug(
                "argformat=%r (callable=%r)",
                self.argformat,
                callable(
                    self.argformat))
            if self.argformat and callable(self.argformat):
                val = self.argformat(self.record.name, val)
            self.record.value = val
            rtn = True
        log.debug("END _argalias = %r", rtn)
        return rtn

    def _envalias(self):
        '''
        Try to set the property value from the environment.  The envalias is
        expected to be a list and each is tried in turn until one is found.
        If envformat is set then it must be a function that takes the property
        name and input value and returns a formatted configuration value.
        '''
        log = logging.getLogger(__name__)
        log.debug("BEGIN _envalias envalias=%r", self.envalias)
        rtn = False
        for envalias in self.envalias:
            if envalias in os.environ:
                val = os.getenv(envalias)
                log.debug(
                    "envformat=%r (callable=%r)",
                    self.envformat,
                    callable(
                        self.envformat))
                if self.envformat and callable(self.envformat):
                    val = self.envformat(self.record.name, val)
                self.record.value = val
                rtn = True
                break
        log.debug("END _envalias = %r", rtn)
        return rtn

    def _cfgalias(self):
        '''
        Try to set the property value from a configparser compatible object.
        The ecfgalias is expected to be a list or lists and each is tried in
        turn until one is found.
        so [['section1','foo'], ['section2','bar']].
        '''
        rtn = False
        log = logging.getLogger(__name__)
        log.debug(
            "BEGIN _cfgalias cfgparser=%r , cfgalias=%r",
            self.cfgparser,
            self.cfgalias)
        if self.cfgparser is not None:
            for keys in self.cfgalias:
                if self.cfgparser.has_option(*keys):
                    val = self.cfgparser.get(*keys)
                    log.debug(
                        "cfgformat=%r (callable=%r)",
                        self.cfgformat,
                        callable(
                            self.cfgformat))
                    if self.cfgformat and callable(self.cfgformat):
                        val = self.cfgformat(self.record.name, val)
                    self.record.value = val
                    rtn = True
                    break
        log.debug("END _cfgalias = %r", rtn)
        return rtn

    def _getdictentry(self, *keys):
        '''
        Test if the given list of keys exist as a nested entry in the
        dictionary.  Returns a tuple where t[0] is True if the
        list led to a value and False otherwise.  t[1] is the value so yes
        (True,None,) means you got a None for a value.
        '''
        log = logging.getLogger(__name__)
        log.debug("_getdictentry(%r)", keys)
        got = True
        value = self.dictconfig
        for key in keys:
            try:
                value = value[key]
                got = True
            except KeyError:
                got = False
                value = None
                break
        return (got, value,)

    def _dictalias(self):
        '''
        Try to set the property value from a dictionary compatible object.
        The dictalias is expected to be a list or lists and each is tried in
        turn until one is found.
        so [['section1','foo'], ['section2','bar']].
        '''
        log = logging.getLogger(__name__)
        log.debug("BEGIN _dictalias dictalias=%r", self.dictalias)
        rtn = False
        if self.dictconfig is not None:
            for keys in self.dictalias:
                dictopt = (False, None,)
                if isinstance(keys, list):
                    dictopt = self._getdictentry(*keys)
                else:
                    dictopt = self._getdictentry(keys)

                if dictopt[0]:
                    val = dictopt[1]
                    log.debug(
                        "dictformat=%r (callable=%r)",
                        self.dictformat,
                        callable(
                            self.dictformat))
                    if self.dictformat and callable(self.dictformat):
                        val = self.dictformat(self.record.name, val)
                    self.record.value = val
                    rtn = True
                    break
        log.debug("END _dictalias = %r", rtn)
        return rtn

    def _default(self):
        log = logging.getLogger(__name__)
        log.debug('_default')
        rtn = False

        if self.has_default:

            self.record.value = self.default_value
            rtn = True
        return rtn

    def __init__(self, fqname, ornearest=True, **kwargs):
        self.record = getConfigRecord(fqname, ornearest)

        for kw in ['argalias', 'argformat',
                   'envformat', 'cfgparser', 'cfgformat',
                   'dictconfig', 'dictformat', 'default_value']:
            setattr(self, kw, None)
            if kw in kwargs:
                setattr(self, kw, kwargs[kw])
        for kw in ['envalias', 'cfgalias', 'dictalias']:
            setattr(self, kw, [])
            if kw in kwargs:
                setattr(self, kw, kwargs[kw])
        self.has_default = 'default_value' in kwargs

    def set_argalias(self, argalias=None, argformat=None):
        '''
        Set/reset the argument alias
        '''
        self.argalias = argalias
        self.argformat = argformat

    def set_envalias(self, envalias=[], envformat=None):
        '''
        Set/reset the environment variable aliases
        '''
        self.envalias = envalias
        self.envformat = envformat

    def set_cfgalias(self, cfgparser=None, cfgalias=[], cfgformat=None):
        '''
        Set/reset the configuration parser aliases
        '''
        self.cfgparser = cfgparser
        self.cfgalias = cfgalias
        self.cfgparser = cfgformat

    def set_dictalias(self, dictconfig=None, dictalias=[], dictformat=None):
        '''
        Set/reset the dict config aliases
        '''
        self.dictconfig = dictconfig
        self.dictalias = dictalias
        self.dictparser = dictformat

    def resolve(self):
        '''
        Actually resolve the different configuration options into a value
        and set it.
        '''
        for res in [self._argalias, self._envalias,
                    self._cfgalias, self._dictalias, self._default]:
            if res():
                break
        return self.record.value

    @property
    def value(self):
        return self.record.value

    @value.setter
    def value(self, val):
        self.record.value = val
        return self.record.value
