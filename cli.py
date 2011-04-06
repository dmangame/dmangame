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

LIFESPAN = 2000

import sys
import os

CliWorld = None
AI = []


def main(ai_classes=[]):
  w = world.World()
  global CliWorld
  CliWorld = w

  for ai_class in ai_classes:
    ai_player = w.addAI(ai_class)
    ai.generate_ai_color(ai_player)

  if settings.SAVE_IMAGES:
    import cairo
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, 200, 200)
    cairo_context = cairo.Context(surface)

  w.world_turns = []
  turns_left = settings.END_GAME_TURNS
  for i in xrange(LIFESPAN):
      w.spinAI()
      if w.Turn():
        if turns_left > 0:
          turns_left -= 1
        else:
          break
      if settings.SAVE_IMAGES:
        worldmap.draw_map(cairo_context, 200, 200, w.dumpTurnToDict())
      w.world_turns.append((w.dumpTurnToDict(), w.dumpScores()))
  log.info("Finished simulating the world")

  sys.exit(0)


def end_threads():
  pass

def end_game():
  global CliWorld
  for ai in CliWorld.AI:
    log.info("%s:%s", ai.__class__, ai.score)

  
  # Save the world information to an output file.
  if settings.JS_REPLAY_FILE:
    jsplayer.save_to_js_file(CliWorld.world_turns)

if __name__ == "__main__":
  main()
