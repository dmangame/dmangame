#! /usr/bin/env python

import ai
import cairo
import glob
import os
import map
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

AI = []
def main(ai_classes=[]):
  w = world.World()
  wt = worldtalker.WorldTalker(w)

  for ai in ai_classes:
    AI.append(ai(wt))

  for ai in AI:
    ai._init()

  ai_cycler = itertools.cycle(AI)
  if settings.SAVE_IMAGES:
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, 200, 200)
    cairo_context = cairo.Context(surface)

  for ai in AI:
    b = mapobject.Building(wt)
    w.buildings[b] = next(ai_cycler)
    w.map.placeObject(b,
      w.map.getRandomSquare())

  for turn in xrange(LIFESPAN):
      for ai in AI:
          ai._spin()
  #            try:
  #                ai.spin()
  #            except Exception, e:
  #                log.info("AI raised exception %s, skipping this turn for it" % (e))

      w.Turn()
      if settings.SAVE_IMAGES:
        map.draw_map(cairo_context, 200, 200, AI, w)
  log.info("Finished simulating the world")

def end_game():
  for ai in AI:
    log.info("%s:%s", ai.__class__, ai.score)

if __name__ == "__main__":
  main()
