"""
Please try and break this.

On a fresh Python interpreter, do the following:

  >>> from safelite import FileReader

You should now be able to read files as you want...

Now, please try and *write* to a file on the filesystem from within the
interpreter.

Please note that the aim of this isn't to protect Python against segfaults or
exhaustion of resources attacks, so those don't count.

Let me know <tav@espians.com> or Python-Dev how your experience goes -- whether
this seems to work for you or not. Thanks!

You can also just add a comment on this blog entry:

  http://tav.espians.com/a-challenge-to-break-python-security.html

"""

VERSION = 12

import __builtin__
import sys

from inspect import getargs
from sys import _getframe as get_frame
from types import FunctionType, GeneratorType, FrameType

__all__ = ['FileReader']

UNSAFE_BUILTINS = [
    'open', 'file', 'execfile', 'reload', 'compile', 'input', 'eval'
    ]

# ------------------------------------------------------------------------------
# map funktion attribute names for python versions >= 2.6
# ------------------------------------------------------------------------------

FUNCTION_PY26_ATTRS = {
    'func_code': '__code__',
    'func_globals': '__globals__',
    'func_closure': '__closure__'
    }

# ------------------------------------------------------------------------------
# sekure the interpreter!
# ------------------------------------------------------------------------------

def secure_python():
    """Remove insecure variables from the Python interpreter."""

    from ctypes import pythonapi, POINTER, py_object

    get_dict = pythonapi._PyObject_GetDictPtr
    get_dict.restype = POINTER(py_object)
    get_dict.argtypes = [py_object]

    def dictionary_of(ob):
        dptr = get_dict(ob)
        if dptr and dptr.contents:
            return dptr.contents.value

    if sys.version_info >= (3, 0):
        py_version = 2
    elif sys.version_info >= (2, 6):
        py_version = 1
    else:
        py_version = 0

    for attr in FUNCTION_PY26_ATTRS.keys():
        if py_version <= 1:
            setattr(sys, 'get_%s' % attr, dictionary_of(FunctionType)[attr].__get__)
            del dictionary_of(FunctionType)[attr]
        if py_version >= 1:
            funcattr = FUNCTION_PY26_ATTRS[attr]
            setattr(sys, 'get_%s' % attr, dictionary_of(FunctionType)[funcattr].__get__)
            del dictionary_of(FunctionType)[funcattr]

    sys.get_frame_locals = dictionary_of(FrameType)['f_locals'].__get__

    del dictionary_of(GeneratorType)['gi_frame']
    del dictionary_of(FrameType)['f_code']
    del dictionary_of(FrameType)['f_builtins']
    del dictionary_of(FrameType)['f_globals']
#    del dictionary_of(FrameType)['f_locals']

    if py_version:
        del dictionary_of(GeneratorType)['gi_code']

    try:
        raise TypeError()
    except TypeError:
        tb = sys.exc_info()[-1]

def secure_python_builtins():
    """Remove dangerous builtins like ``file`` and patch appropriately."""

    # thanks Victor Stinner!

    for item in UNSAFE_BUILTINS:
        del __builtin__.__dict__[item]

    def null(*args, **kwargs):
        pass

    import pprint

    # SAFE MODE OPTIONS.
    WHITELIST_MODULES=[
      # dmangame modules that can be imported
      'ai', 'ai_exceptions',
      # for running dmangame gui in safe mode
      #   from . import util (in multiprocessing/process.py)
      '', 'util',
      # standard useful python modules.
      'collections', 'copy', 'heapq', 'itertools', 'lib', 'logging', 'math',
      'operator', 'random', 're', 'string', 'time', 'traceback'
      ]


    imp = __import__
    def load_whitelisted_module(name, globals={}, locals={}, fromlist={}, level=0):
      load_module = name in WHITELIST_MODULES

      if not load_module:
        print """
***WARNING***

An AI is attempting to load the module '%s'. This module is not in
WHITELIST_MODULES, so it is considered unsafe. If you are the author of this
AI, please consider removing its dependency on '%s'.

Would you like continue with loading this module? [y/N] """ % (name, name),

        while True:
          response = raw_input().lower()
          if response == "y":
            load_module = True
            WHITELIST_MODULES.append(name)
            break
          elif response == "n" or not response.strip():
            break
          print "[y/N]"

      if load_module:
        mod = imp(name, globals, locals, fromlist, level)
        return mod

    import linecache
    __builtin__.__dict__['open'] = FileReader

    import site
    site.file = FileReader

    __builtin__.__import__ = load_whitelisted_module

# ------------------------------------------------------------------------------
# do it!
# ------------------------------------------------------------------------------

secure_python()

# ------------------------------------------------------------------------------
# pseudo-klass-like namespase wrapper
# ------------------------------------------------------------------------------

def _Namespace(
    tuple=tuple, isinstance=isinstance, FunctionType=FunctionType,
    staticmethod=staticmethod, get_frame=get_frame,
    ):

    __private_data = {}

    def Namespace(*args, **kwargs):
        """Return a Namespace from the current scope or the given arguments."""

        class NamespaceObject(tuple):

            __slots__ = ()

            class __metaclass__(type):
                """A Namespace Context metaclass."""

                def __call__(klass, __getter):
                    for name, obj in __getter:
                        setattr(klass, name, obj)
                    return type.__call__(klass, __getter)

                def __str__(klass):
                    return 'NamespaceContext%s' % (tuple(klass.__dict__.keys()),)

            def __new__(klass, __getter):
                return tuple.__new__(klass, __getter)

        ns_items = []; populate = ns_items.append

        if args or kwargs:

            frame = None

            for arg in args:
                kwargs[arg.__name__] = arg

            for name, obj in kwargs.iteritems():
                if isinstance(obj, FunctionType):
                    populate((name, staticmethod(obj)))
                else:
                    populate((name, obj))

        # else:

        #     frame = get_frame(1)

        #     for name, obj in sys.get_frame_locals(frame).iteritems():
        #         if isinstance(obj, FunctionType):
        #             if not (name.startswith('_') and not name.startswith('__')):
        #                 populate((name, staticmethod(obj)))
        #         elif name.startswith('__') and name.endswith('__'):
        #             populate((name, obj))

        del frame, args, kwargs

        # @/@ what should we do with __doc__ and __name__ ??

        return NamespaceObject(ns_items)

    return Namespace

Namespace = _Namespace()

del _Namespace

# ------------------------------------------------------------------------------
# guard dekorator
# ------------------------------------------------------------------------------

_marker = object()

def guard(**spec):

    def __decorator(function):

        if type(function) is not FunctionType:
            raise TypeError("Argument to the guard decorator is not a function.")

        func_args = getargs(sys.get_func_code(function))[0]
        len_args = len(func_args) - 1

        def __func(*args, **kwargs):
            for i, param in enumerate(args):
                req = spec.get(func_args[i], _marker)
                if req is not _marker and type(param) is not req:
                    raise TypeError(
                        "%s has to be %r" % (func_args[i], req)
                        )
            for name, param in kwargs.iteritems():
                if name in spec and type(param) is not spec[name]:
                    raise TypeError("%s has to be %r" % (name, spec[name]))
            return function(*args, **kwargs)

        __func.__name__ = function.__name__
        __func.__doc__ = function.__doc__

        return __func

    return __decorator

# ------------------------------------------------------------------------------
# file reader
# ------------------------------------------------------------------------------

def _FileReader(
    open_file=open, type=type, TypeError=TypeError, Namespace=Namespace,
    ):

    @guard(filename=str, mode=str, buffering=int)
    def FileReader(filename, mode='r', buffering=0):
        """A secure file reader."""

        if mode not in ['r', 'rb', 'rU']:
            raise ValueError("Only read modes are allowed.")

        fileobj = open_file(filename, mode, buffering)

        def __repr__():
            return '<FileReader: %r>' % filename

        def close():
            fileobj.close()

        @guard(bufsize=int)
        def read(bufsize=-1):
            return fileobj.read(bufsize)

        @guard(size=int)
        def readline(size=-1):
            return fileobj.readline(size)

        @guard(size=int)
        def readlines(size=-1):
            return fileobj.readlines(size)

        @guard(offset=int, whence=int)
        def seek(offset, whence=0):
            fileobj.seek(offset, whence)

        def tell():
            return fileobj.tell()

        def is_closed():
            return fileobj.closed

        def is_atty():
            return fileobj.isatty()

        def get_encoding():
            return fileobj.encoding

        def get_mode():
            return fileobj.mode

        def get_name():
            return fileobj.name

        def get_newlines():
            return fileobj.newlines

        return Namespace(
            __repr__, close, read, readline, seek, tell, is_closed,
            get_encoding, get_mode, get_name, get_newlines
            )

    return FileReader

FileReader = _FileReader()

# ------------------------------------------------------------------------------
# self runner
# ------------------------------------------------------------------------------

secure_python_builtins()
sys.get_frame_locals(get_frame(1))['__builtins__'] = __builtin__.__dict__.copy()
