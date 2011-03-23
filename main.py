#! /usr/bin/env python

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
    parser.add_option("-g", "--gui", dest="gui",
                      help="Display GUI", default=False,
                      action="store_true")
    parser.add_option("-q", "--quiet",
                      action="store_false", dest="verbose", default=True,
                      help="don't print status messages to stdout")

    (options, args) = parser.parse_args()
    return options,args


def loadAI(ais):
    if not ais:
      return

    ai_modules = []
    sys.path.append("ai")
    for f in ais:
        try:
            log.info("Loading %s..." % (f),)
            file, pathname, desc = imp.find_module(f)
            m = imp.load_module(f, file, pathname, desc)
            ai_modules.append(m)
            log.info("Done")
        except Exception, e:
            log.info("Load Exception", e)

    ai_classes = map(lambda m: getattr(m, m.AIClass),
                     ai_modules)
    return ai_classes

def main():
  options, args = parseOptions()
  log.info(options)
  ais = loadAI(args)
  if options.gui:
    try:
      gui.main(ais)
    except KeyboardInterrupt, e:
      pass
    finally:
      gui.end_game()
  else:
    try:
      cli.main(ais)
    except KeyboardInterrupt, e:
      pass
    finally:
      cli.end_game()

if __name__ == "__main__":
  import cProfile
  cProfile.run("main()", "mainprof")
#  main()
