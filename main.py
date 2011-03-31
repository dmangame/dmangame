#! /usr/bin/env python
import settings

import logging
log = logging.getLogger("MAIN")

try:
  import pyximport
  log.info('Gearing up with Cython')
  pyximport.install()
except Exception, e:
  log.info(e)


# Disable the GC on suspicions
import gc
gc.disable()

import glob
import os
import sys

sys.path.append("lib")
import imp
import traceback
from optparse import OptionParser

import cli
import gui
import world

def parseOptions():
    parser = OptionParser()
    parser.add_option("-m", "--map", dest="map",
                      help="Use map settings from MAP", default=None)
    parser.add_option("-c", "--cli", dest="cli",
                      help="Display GUI", default=False,
                      action="store_true")
    parser.add_option("-s", "--save", action="store_true",
                      help="save each world turn as a png",
                      dest="save_images", default=False)
    parser.add_option("-q", "--quiet",
                      action="store_false", dest="verbose", default=True,
                      help="don't print status messages to stdout")
    parser.add_option("-i", "--ignore",
                      action="store_false", dest="whiny",
                      default=True,
                      help="ignore AI exceptions")
    parser.add_option("-p", "--profile",
                      action="store_true", dest="profile",
                      default=False)

    (options, args) = parser.parse_args()
    return options,args


def loadAI(ais):
    if not ais:
      return

    ai_modules = []
    for filename in ais:
        try:
            log.info("Loading %s..." % (filename),)
            file = open(filename)
            split_ext = os.path.splitext(filename)
            module_name = os.path.basename(split_ext[0])
            module_type = filter(lambda x: x[0] == split_ext[1],
                                 imp.get_suffixes())[0]

            m = imp.load_module(module_name, file, filename, module_type)
            ai_modules.append(m)
            log.info("Done")
        except Exception, e:
            raise


    ai_classes = map(lambda m: getattr(m, m.AIClass),
                     ai_modules)
    return ai_classes

def loadMap(filename):
  if not filename:
    return

  try:
      log.info("Loading Map %s..." % (filename),)
      file = open(filename)
      split_ext = os.path.splitext(filename)
      module_name = os.path.basename(split_ext[0])
      module_type = filter(lambda x: x[0] == split_ext[1],
                           imp.get_suffixes())[0]

      m = imp.load_module(module_name, file, filename, module_type)
      for attr in dir(m):
        if not attr.startswith("__"):
          log.info("Setting: %s to %s", attr, getattr(m, attr))
          setattr(settings, attr, getattr(m,attr))
  except Exception, e:
      log.info("Error loading %s, %s", filename, e)

def run_game():
  options, args = parseOptions()
  ais = loadAI(args)
  loadMap(options.map)
  settings.IGNORE_EXCEPTIONS = not options.whiny
  if options.save_images:
    settings.SAVE_IMAGES = True



  ui = cli if options.cli else gui

  try:
    ui.main(ais)
  except KeyboardInterrupt, e:
    raise
  except Exception, e:
    traceback.print_exc()
  finally:
    ui.end_game()

  
def main():
  options, args = parseOptions()
  log.info(options)
  if options.profile:
    settings.PROFILE = True
    import cProfile

  if settings.PROFILE:
    cProfile.run("run_game()", "mainprof")
  else:
    run_game()

if __name__ == "__main__":
  main()
