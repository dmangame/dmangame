#! /usr/bin/env python

import ai
import cairo
import glob
import os
import worldmap
import mapobject
import world
import worldtalker
import itertools
import settings
import logging
log = logging.getLogger("CLI")

LIFESPAN = 800

import sys
import os

World = None
AI = []

def main(ai_classes=[]):
  w = world.World()
  global World
  World = w

  for ai_class in ai_classes:
    w.addAI(ai_class)

  if settings.SAVE_IMAGES:
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, 200, 200)
    cairo_context = cairo.Context(surface)

  for i in xrange(LIFESPAN):
      w.spinAI()
      w.Turn()
      if settings.SAVE_IMAGES:
        worldmap.draw_map(cairo_context, 200, 200, AI, w)
  log.info("Finished simulating the world")


def end_game():
  for ai in World.AI:
    log.info("%s:%s", ai.__class__, ai.score)

if __name__ == "__main__":
  main()
