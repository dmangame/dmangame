#! /usr/bin/env python
import settings

import logging
log = logging.getLogger("MAIN")

try:
  import pyximport
  log.info('Gearing up with Cython')
  pyximport.install(pyimport=True)
except Exception, e:
  log.info(e)


import glob
import os
import sys
import imp
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
                      dest="save_images", default=False)
    parser.add_option("-q", "--quiet",
                      action="store_false", dest="verbose", default=True,
                      help="don't print status messages to stdout")

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
            log.info("Error loading %s, %s", filename, e)

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

def main():
  options, args = parseOptions()
  log.info(options)
  ais = loadAI(args)
  loadMap(options.map)
  if options.save_images:
    settings.SAVE_IMAGES = True
  if options.cli:
    try:
      cli.main(ais)
    except KeyboardInterrupt, e:
      pass
    finally:
      cli.end_game()
  else:
    try:
      gui.main(ais)
    except KeyboardInterrupt, e:
      pass
    finally:
      gui.end_game()

if __name__ == "__main__":
  import cProfile
  cProfile.run("main()", "mainprof")
#  main()
