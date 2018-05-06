# Domen Las Python Application Library


dlpyapp is a collection of modules which are useful for bootstrapping python 
applications and separating module configuration from application configuration. 

## Description 

### dlapp


The top level package.


### dlapp.logger


Helpers for configuring application logging.  This module logger assumes logging
will use the inbuilt python logging facility.



#### logger.load_json_config(conffile=None)

Load a json formatted dictionary of logging configuration information.  

- Arguments

	- conffile: The path/name of a file containing a json formatted
	  dictionary suitable for passing to logging.dictConfig.

- Return

	- A dictionary which must be able to be passed directly to 
	  logging.dictConfig()

- Exceptions

	- LoggerConfDoesNotExist: If the given file cannot be found.
	- json.JSONDecodeError: If the decoding of the json contents fails.
	- IOError: If reading the given file fails.
	- KeyboardInterrupt: If the file reading or parsing are interuppted from the keyboard.
	- Exception: Any unexpected exception is logged and raised again.




#### logger.adjust_loglevel(logging_config=DEFAULT_LOGGING_CONFIG, verbosity=0, quiet=0)

Used for command line argument log level adjustments (eg. -v and -q).  
The log level of the root logger is set to:

	`max(configured (or DEFAULT) level + 10 * (quiet - verbosity),0)`
	
ie. The higher the *verbosity* the more will be logged.  
The higher the *quiet* the less will be logged.

- Arguments

	- A dictionary that can be passed directly to logging.dictConfig()

- Return

	- A copy of the input dictionary with adjusted log level

- Exceptions

	- None

#### init(logging_config=DEFAULT_LOGGING_CONFIG)

Initialize logging from the given dictConfig usable dictionary.


### dlapp.configuration


Module which allows packages and modules to define configuration options which
can then be set from the application which imports them. 
The recommended use is to use the getConfig function in modules and the
AppConfig class in the application.

Configuration property names must match the regexp 
`VALID_PROPERTY_NAMES = "[A-Za-z][_a-zA-Z0-9]*$"`.  If a property name is given
which does not match this expression a *ConfigPropertyBadName* exception is
raised.

Namespace names must match the regexp 
`VALID_NS_NAMES = "([A-Za-z][_a-zA-Z0-9]*)(\.?[_A-Za-z][_a-zA-Z0-9]*)*$"`.
If a namespace is given which does not match this expression a 
*ConfigNamespaceBadName* exception is raised.
The exception to this is the name of the default namespace.
This is set by DEFAULT_NS and by default is `__DEFAULT`.


#### getConfig(nspc=None, ornearest=True, **kwargs)

This is the recommended module interface.  Calling getConfig with a nspc value
creates a singleton ConfigManager (where one does not exist) and returns a
configuration namespace (nspc) from it.  Properties records can then be be 
added to that namespace.  

Calling getConfig() without a name will search for an existing namespace but
not create one.  By default the search starts with a name equal to the full
name of the calling module eg. dlapp.test.test_function1.  It then walks back
up the tree (dlapp.test, dlapp then finally the inbuilt the default namespace).

The `ornearest=False` will supress the search and instead raise an exception 
*ConfigManagerMissingNamespace*

When a new namespace is create any additional arguments (**kwargs) are passed
to the instantiation of that namespace. When an existing namespace is retrieved
any additional arguments are ignored.



#### AppConfig(fqname, ornearest=True, **kwargs)

kwargs keys can be any of `argalias`, `argformat`, `envalias`, `envformat`,
`cfgalias`, `cfgparser`, `cfgformat`, `dictalias`, `dictconfig`, `dictformat`,
`default_value`.  All of these except default_value can be set later by
calling the appropriate method.

On instantiation the function getConfigRecord(fqname) is used to retrieve the
PropertyRecord (or raise an exception if one cannot be found).

The: arg* alias command line to the selected property record.
env* alias environment variable names to the selected property record.
cfg* alias configparser compatible config to the selected property record.
dict* alias dictionary config to to the selected property record.

When the resolve() method is called on the object the aliases are tried
in arg, env, cfg and dict (then default_value) order and the first valid
alias is used to set the value of the configuration option.  

Each alias type allows a format function to be specified.  This will receive
the property record name and the value in the format supplied by that format
(eg. environment values are strings) and it should return a value formatted
as required by the module (and passing any set validation function). 
 

## Testing
-------

Run unit tests and gather coverage data

`pytest-3 --cov-report=html --cov=dlapp.configuration dlapp/test`


## Example
-------

### dlapp.logging

```python
	import logging
	import dlapp.logger as logger

	logdict=logger.load_json_config('logging.json')
	logdict=logger.adjust_loglevel(logdict, args.verbosity, args.quiet)
	logger.init(logdict)
```	
	
### dlapp.configuration

```python
mypackage/__init__.py

	class ValidationException(Exception):
	    pass

	def fnvalidate(name,value):
	    if isinstance(value, Number):
		    if value >= 0 and value < 10:
		        return True
	    raise ValidationException(value)
	    	    
	cfg=getConfig(__name__)
    cfg.app_property('favouritenumber', value=7, callback=logchange, 
        validate=fnvalidate)
```

```python
mypackage/useful.py

	def logchange(name,value):
	    log=logging.getLogger(__name__)
	    log.debug("%r changed to %r", name, value)


	def dowork():
	    log=logging.getLogger(__name__)
	    # Get the parent namespace created in __init__.py
	    cfg=getConfig() 
	    # Add a property record with a default value
	    favnum = cfg.favouritenumber
    	log.info("I love my %s.  It is %d.",(favnum.name, favnum.value,))
```
```python
myapplication/main.py
	
	if __name__ == '__main__':
		favnum=AppConfig('mypackage.favouritenumber', default_value=2)
		favnum.set_argalias(argparser.favnum)
		favnum.set_envalias(['MYAPP_FAVOURITE_NUMBER'],
		    envformat=reformatstr)
		favnum.set_dictalias( dcfg , dictalias=[['MYAPP','MYPACKAGE', 
		    'FAVNUM']])
		
		favnum.resolve()
		useful.dowork()
```


