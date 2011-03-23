#! /usr/bin/env python

import ai
import glob
import os
import mapobject
import world
import worldtalker
import itertools

LIFESPAN = 100

import sys
import os

def main(ai_classes=[]):
  w = world.World()
  wt = worldtalker.WorldTalker(w)

  AI = []

  for ai in ai_classes:
    AI.append(ai(wt))

  for ai in AI:
    ai._init()

  ai_cycler = itertools.cycle(AI)

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
  #                print "AI raised exception %s, skipping this turn for it" % (e)

      w.Turn()
  print "Finished simulating the world, press Enter to exit"
  raw_input()

if __name__ == "__main__":
  main()
