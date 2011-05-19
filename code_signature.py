import hashlib
import copy
import os
import sys
import settings

CUR_DIR = os.path.dirname(os.path.abspath(__file__))

LOADED_MODULES=set()
def freezeModules():
  LOADED_MODULES=set(copy.copy(sys.modules))

def digestCode():
    child_modules = []
    md = hashlib.md5()
    modules = sys.modules.values()
    for mod in modules:
      if getattr(mod, "__file__", None):
        p = os.path.dirname(os.path.abspath(mod.__file__))
        if p.startswith(CUR_DIR):
          child_modules.append(mod)

    child_modules.sort(key=lambda m: m.__name__)

    for module in child_modules:
      # This is a major assumption, relies on the .py files
      # always being around when there is a .pyc
      f = module.__file__.replace(".pyc", ".py")

      if module in LOADED_MODULES:
        md.update(open(f).read())


    return md.hexdigest()
