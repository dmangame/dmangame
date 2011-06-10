from __future__ import with_statement

import ai
import glob
import os
import worldmap
import mapobject
import world
import worldtalker
import itertools
import settings
import logging

from lib import jsplayer
log = logging.getLogger("CLI")

import time
import sys
import os
import gc

CliWorld = None
AI = []

ncurses = None
ai_module = ai

def main(ai_classes=[]):
  w = world.World()
  ai_module.clear_ai_colors()
  global CliWorld, ncurses

  CliWorld = w
  if settings.NCURSES:
    import ncurses_gui
    ncurses_gui.redirect_outputs()
    ncurses = ncurses_gui.NcursesGui()


  for ai_class in ai_classes:
    ai_player = w.addAI(ai_class)
    ai_module.generate_ai_color(ai_player)

  w.world_turns = []
  turns_left = settings.END_GAME_TURNS
  if settings.NCURSES:
    ncurses.init(w)

  for i in xrange(settings.GAME_LENGTH):
      w.spinAI()
      if w.Turn():
        if turns_left > 0:
          turns_left -= 1
        else:
          break

      t = w.dumpTurnToDict(shorten=True)
      s = w.dumpScores()

      w.world_turns.append((t,s))

      if settings.NCURSES:
        ncurses.update(t, s)

      if len(w.world_turns) >= settings.BUFFER_SIZE:
        jsplayer.save_world_turns(w.world_turns)
        w.world_turns = []
        gc.collect()

  log.info("Finished simulating the world")

def end_threads():
  pass

def end_game():
  global CliWorld
  for ai in CliWorld.AI:
    log.info("%s:%s", ai.__class__, ai.score)

  if settings.NCURSES:
    ncurses.end()

  # Save the world information to an output file.
  if settings.JS_REPLAY_FILE or settings.JS_REPLAY_FILENAME:
    jsplayer.save_world_turns(CliWorld.world_turns)
    jsplayer.end_world(CliWorld.dumpWorldToDict())

def appengine_main(ais, appengine_file_name=None, tournament_key=None):
  from appengine.appengine import record_game_to_db
  from google.appengine.api import files
  ai_module.clear_ai_colors()
  start_time = time.time()

  if not appengine_file_name:
    appengine_file_name = files.blobstore.create(mime_type='text/html')
  settings.JS_REPLAY_FILENAME = appengine_file_name

  world_turns = []
  w = world.World()
  turns_left = settings.END_GAME_TURNS
  for ai_class in ais:
    ai_player = w.addAI(ai_class)
    ai_module.generate_ai_color(ai_player)

  try:
    for i in xrange(settings.GAME_LENGTH):
        w.spinAI()
        if w.Turn():
          if turns_left > 0:
            turns_left -= 1
          else:
            break

        t = w.dumpTurnToDict(shorten=True)
        s = w.dumpScores()

        world_turns.append((t,s))

        if len(world_turns) >= settings.BUFFER_SIZE:
          with files.open(appengine_file_name, 'a') as replay_file:
            settings.JS_REPLAY_FILE = replay_file
            jsplayer.save_world_turns(world_turns)
            replay_file.close()

          world_turns = []
          gc.collect()

    log.info("Finished simulating the world")
  except KeyboardInterrupt, e:
    raise
  except Exception, e:
    traceback.print_exc()
  finally:
    for ai in w.AI:
      log.info("%s:%s", ai.__class__, ai.score)

    with files.open(appengine_file_name, 'a') as replay_file:
      settings.JS_REPLAY_FILE = replay_file
      if world_turns:
        jsplayer.save_world_turns(world_turns)
      # Save the world information to an output file.
      if settings.JS_REPLAY_FILE or settings.JS_REPLAY_FILENAME:
        jsplayer.end_world(w.dumpWorldToDict())
      replay_file.close()


  files.finalize(appengine_file_name)
  replay_blob_key = files.blobstore.get_blob_key(appengine_file_name)

  log.info("Saved to: %s", replay_blob_key)
  log.info("Saved as: %s", appengine_file_name)
  log.info("http://localhost:8080/replays/%s", replay_blob_key)

  end_time = time.time()
  run_time = end_time - start_time

  record_game_to_db(w, replay_blob_key, run_time, tournament_key)

  return w



if __name__ == "__main__":
  main()
