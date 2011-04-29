#! /usr/bin/env python

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

import sys
import os

CliWorld = None
AI = []

ncurses = None

def main(ai_classes=[]):
  w = world.World()
  global CliWorld, ncurses

  CliWorld = w
  if settings.NCURSES:
    import ncurses_gui
    ncurses_gui.redirect_outputs()
    ncurses = ncurses_gui.NcursesGui()


  for ai_class in ai_classes:
    ai_player = w.addAI(ai_class)
    ai.generate_ai_color(ai_player)

  if settings.SAVE_IMAGES:
    import cairo
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, 200, 200)
    cairo_context = cairo.Context(surface)

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
      if settings.SAVE_IMAGES:
        worldmap.draw_map(cairo_context, 200, 200, t)

      if settings.NCURSES:
        ncurses.update(t, s)
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
  if settings.JS_REPLAY_FILE:
    jsplayer.save_to_js_file(CliWorld.dumpWorldToDict(), CliWorld.world_turns)

if __name__ == "__main__":
  main()
