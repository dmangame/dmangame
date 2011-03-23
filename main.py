#! /usr/bin/env python
try:
  import pyximport
  print 'Gearing up with Cython'
  pyximport.install(pyimport=True)
except Exception, e:
  print e


import glob
import os
import sys
import imp
from optparse import OptionParser

import cli
import gui

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
            print "Loading %s..." % (f),
            file, pathname, desc = imp.find_module(f)
            m = imp.load_module(f, file, pathname, desc)
            ai_modules.append(m)
            print "Done"
        except Exception, e:
            print e

    ai_classes = map(lambda m: getattr(m, m.AIClass),
                     ai_modules)
    return ai_classes

if __name__ == "__main__":
  options, args = parseOptions()
  print options
  ais = loadAI(args)
  if options.gui:
    gui.main(ais)
  else:
    cli.main(ais)
