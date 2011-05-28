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

import settings

import urllib2
import urllib

import copy
import glob
import os
import random
import sys

sys.path.append("lib")
import imp
import traceback
from optparse import OptionParser


import cli
IMPORT_GUI_FAILURE=False

GITHUB_URL="https://github.com/%s/dmanai/raw/master/%s"

try:
  import gui
except Exception, e:
  IMPORT_GUI_FAILURE=True
  log.info("Couldn't import GUI: %s", e)

import world


class DependencyException(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)


def parseOptions(opts=None):
    parser = OptionParser()
    parser.add_option("-m", "--map", dest="map",
                      help="Use map settings from MAP", default=None)
    parser.add_option("-c", "--cli", dest="cli",
                      help="Display GUI", default=False,
                      action="store_true")

    parser.add_option("-f", "--fps", dest="fps",
                      help="Frames Per Second", default=10)
    parser.add_option("-s", "--save", action="store_true",
                      help="save each world turn as a png",
                      dest="save_images", default=False)
    parser.add_option("-q", "--quiet",
                      action="store_false", dest="verbose", default=True,
                      help="don't print status messages to stdout")
    parser.add_option("--hl", "--highlight",
                      action="append", dest="highlight",
                      default=None, help="Show debugging highlights")
    parser.add_option("-i", "--ignore",
                      action="store_false", dest="whiny",
                      default=True,
                      help="ignore AI exceptions")
    parser.add_option("-n", "--ncurses",
                      action="store_true", dest="ncurses",
                      help="use curses output module, use with -c",
                      default=False)
    parser.add_option("-p", "--profile",
                      action="store_true", dest="profile",
                      help="enable profiling with cProfile",
                      default=False)
    parser.add_option("-t", "--tournament",
                      dest="tournament",
                      action="store", default=0, type=int,
                      help="Run app engine tournament")
    parser.add_option("-a", "--app-engine",
                      dest="app_engine",
                      action="store_true", default=False,
                      help="Run on google app engine")

    parser.add_option("-o", "--output",
                      dest="replay_file",
                      help="create HTML replay file")

    parser.add_option("-r", "--register",
                      dest="update_app_engine_ai",
                      action="store_true", default=False,
                      help="Register AI for ladder matches")
    (options, args) = parser.parse_args(opts)

    # Iterate through args and options.highlight to verify there are no
    # duplicates.
    ai_used = {}
    if options.highlight:
      highlighted_ai = []
      for ai in options.highlight:
        if ai in ai_used:
          logging.warn("Not loading duplicate file AI: %s ", ai)
        else:
          highlighted_ai.append(ai)
        ai_used[ai] = True

      options.highlight = highlighted_ais

    ais = []
    for ai in args:
      if ai in ai_used:
        logging.warn("Not loading duplicate file AI: %s ", ai)
      else:
        ais.append(ai)
      ai_used[ai] = True

    return options,ais

# Requires that module_require is setup with base_dir and locals.
def module_require(module_name, rel_path=None):
  path = module_require.base_dir
  if rel_path:
    path = os.path.abspath(os.path.join(path, rel_path))

  file,pathname,desc = imp.find_module(module_name, [path])
  def sub_module_require(module_name, rel_path=None):
    raise DependencyException("Dependencies may only be included from the main AI file supplied on the command line.")

  mod = setupModule(module_name, pathname, require_func=sub_module_require)
  module_require.locals[module_name] = mod

def setupModule(module_name, filename, require_func=None, data=None):
  if not data:
    data = open(filename).read()

  if module_name in sys.modules:
    del sys.modules[module_name]

  mod = imp.new_module(str(module_name))
  if module_name in sys.modules:
    del sys.modules[module_name]

  sys.modules[module_name] = mod

  if not require_func:
    require_func = copy.copy(module_require)

  require_func.locals = mod.__dict__
  require_func.base_dir = os.path.split(filename)[0]
  mod.__dict__["require_dependency"] = require_func
  mod.__file__ = filename
  mod.__file_content__ = data

  exec(data, mod.__dict__, mod.__dict__)
  return mod


def generate_submodule_require_func(load_method):
  def require_from_user(module_name, rel_path=None):
    path = require_from_user.base_dir
    if rel_path:
      path = os.path.join(path, rel_path)
    sub_mod = load_method("%s.py" % (os.path.join(path, module_name)))
    require_from_user.locals[module_name] = sub_mod

  return require_from_user

# Should this file be saved to disk?
def loadGithubAIData(ai_str):
  user,filenames = ai_str.split(":")
  files = filenames.split(",")
  log.info("Loading AI from github user %s", user)


  for filename in files:
    ai_mod = filename == files[-1]
    split_ext = os.path.splitext(filename)

    module_name = os.path.basename(split_ext[0])

    # URL BEING LOADED
    url = GITHUB_URL % (user, filename)
    if ai_mod:
      log.info("Loading AI module from %s" % (url))
    else:
      log.info("Loading AI dependency from %s" % (url))

    f = urllib2.urlopen(url)
    data = f.read()

    filename = "%s:%s" % (user, filename)
    require_func = generate_submodule_require_func(loadGithubAIData)
    mod = setupModule(module_name, filename, data=data,
                    require_func=require_func)
    mod.__ai_str__ = ai_str

  mod.__dict__["__ai_str__"] = ai_str
  return mod

def loadFileAIData(ai_str):
  log.info("Loading %s from local filesystem" % (ai_str))
  filename = ai_str

  split_ext = os.path.splitext(filename)

  module_name = os.path.basename(split_ext[0])

  require_func = generate_submodule_require_func(loadFileAIData)
  mod = setupModule(module_name, filename, require_func=require_func)
  mod.__ai_str__ = ai_str

  return mod

def loadAIModules(ais, highlight=False):
    if not ais:
      return

    ai_modules = []
    # for each filename, add dir to the path and then try to
    # import the actual file. if dir was not on the path
    # beforehand, make sure to pop it off again
    for filename in ais:
        try:
            log.info("Loading %s..." % (filename),)
            if filename.find(":") > 0:
              mod = loadGithubAIData(filename)
            else:
              mod = loadFileAIData(filename)

            ai_modules.append(mod)
            log.info("Done")

        except Exception, e:
            raise


    ai_classes = map(lambda m: getattr(m, m.AIClass),
                     ai_modules)
    return ai_classes

def loadMap(filename):

  try:
      log.info("Loading Map %s..." % (filename),)
      split_ext = os.path.splitext(filename)

      module_name = os.path.basename(split_ext[0])

      if module_name in sys.modules:
        mod = sys.modules[module_name]
      else:
        mod = imp.new_module(str(module_name))
        sys.modules[module_name] = mod

      mod.__file__ = filename
      execfile(filename, mod.__dict__, mod.__dict__)
      settings.MAP_NAME=filename

      for attr in dir(mod):
        if not attr.startswith("__"):
          log.info("Setting: %s to %s", attr, getattr(mod, attr))
          setattr(settings, attr, getattr(mod,attr))

  except Exception, e:
      log.info("Error loading %s, %s", filename, e)

# AI Players have a filename, skill and uncertainty.
def appengine_run_tournament(ai_files, argv_str, tournament_key):
  from google.appengine.ext import deferred
  import tournament

  options, args = parseOptions(argv_str.split())
  tournament_map =  random.choice([None, "macro.py", "village.py"])

  if tournament_map:
    use_map = "maps/%s" % tournament_map
  else:
    use_map = None

  

  
  for game in tournament.league_games(ai_files, options.tournament):
    deferred.defer(appengine_tournament_game, game, use_map, tournament_key)

def appengine_tournament_game(ai_files, map_file, tournament_key):
  from appengine import record_ladder_match
  logging.basicConfig(level=logging.INFO)
  reload(settings)
  loadMap(map_file)
  ais = loadAIModules(ai_files)

  settings.SINGLE_THREAD = True
  settings.IGNORE_EXCEPTIONS = True

  world = cli.appengine_main(ais, tournament_key=tournament_key)


  record_ladder_match(world)


def appengine_run_game(argv_str, appengine_file_name=None):
  logging.basicConfig(level=logging.INFO)
  argv = argv_str.split()
  options, args = parseOptions(argv)
  reload(settings)
  loadMap(options.map)
  ais = loadAIModules(args) or []
  highlighted_ais = loadAIModules(options.highlight, highlight=True)
  if highlighted_ais:
    ais.extend(highlighted_ais)
    settings.SHOW_HIGHLIGHTS = set(highlighted_ais)

  settings.SINGLE_THREAD = True
  settings.IGNORE_EXCEPTIONS = True

  if options.fps: settings.FPS = int(options.fps)

  cli.appengine_main(ais, appengine_file_name)

def update_ai_on_appengine():
  import yaml
  yaml_data = open("app.yaml").read()
  app_data = yaml.load(yaml_data)
  dest = "ladder/register"
  if settings.APPENGINE_LOCAL:
    url_to = "http://localhost:8080/%s"%(dest)
  else:
    url_to = "http://%s.appspot.com/%s" % (app_data["application"], dest)

  data = " ".join(sys.argv[1:])
  data_str = urllib.urlencode({"argv" : data})

  print "Posting to: ", url_to
  print "Posting with:"
  print data_str
  r = urllib2.urlopen(url_to, data_str)
  print r.read()


def post_to_appengine():
  import yaml
  yaml_data = open("app.yaml").read()
  app_data = yaml.load(yaml_data)
  if not settings.TOURNAMENT:
    mode = "run_game"
  else:
    mode = "run_tournament"

  if settings.APPENGINE_LOCAL:
    url_to = "http://localhost:8080/%s"%(mode)
  else:
    url_to = "http://%s.appspot.com/%s" % (app_data["application"], mode)

  data = " ".join(sys.argv[1:])
  data_str = urllib.urlencode({"argv" : data})

  print "Posting to: ", url_to
  print "Posting with:"
  print data_str
  r = urllib2.urlopen(url_to, data_str)
  print r.read()


def run_game():
  # Start the basic logging at INFO level
  options, args = parseOptions()

  if options.tournament:
    settings.TOURNAMENT = options.tournament

  if options.app_engine:
    post_to_appengine()
    return

  if options.update_app_engine_ai:
    update_ai_on_appengine()
    return

  logger_stream = None
  if options.ncurses:
    settings.NCURSES = True
    print "Logging game to game.log"
    logger_stream = open("game.log", "w")

  logging.basicConfig(level=logging.INFO, stream=logger_stream)

  ais = loadAIModules(args) or []
  highlighted_ais = loadAIModules(options.highlight, highlight=True)
  if highlighted_ais:
    ais.extend(highlighted_ais)
    settings.SHOW_HIGHLIGHTS = set(highlighted_ais)

  loadMap(options.map)
  settings.IGNORE_EXCEPTIONS = not options.whiny
  if options.save_images:
    settings.SAVE_IMAGES = True

  if options.replay_file:
    settings.JS_REPLAY_FILENAME = options.replay_file

  if options.fps:
    settings.FPS = int(options.fps)


  ui = cli if options.cli or IMPORT_GUI_FAILURE else gui

  try:
    ui.main(ais)
  except KeyboardInterrupt, e:
    raise
  except Exception, e:
    traceback.print_exc()
  finally:
    ui.end_threads()
    ui.end_game()


def main():
  options, args = parseOptions()
  log.info(options)
  if options.profile:
    settings.PROFILE = True
    settings.SINGLE_THREAD = True
    import cProfile

  if settings.PROFILE:
    cProfile.run("run_game()", "mainprof")
  else:
    run_game()

if __name__ == "__main__":
  main()
