

import ai
import glob
import gobject
import gtk
import mapobject
import itertools
import world
import worldtalker
import map

import logging
log = logging.getLogger("GUI")





class MapGUI:
    def __init__(self):
        # Initialize Widgets
        self.window = gtk.Window()
        box = gtk.VBox()

        self.map_area = gtk.DrawingArea()

        box.pack_start(self.map_area)
        self.window.add(box)
        self.window.show_all()
        self.map_area.connect("expose-event", self.map_expose_event_cb)
        self.window.resize(250, 250)
        self.window.connect("destroy", gtk.main_quit)

        # Initialize the world
        self.world = world.World()
        self.wt = worldtalker.WorldTalker(self.world)
        self.AI = []
        self.ai_cycler = itertools.cycle(self.AI)
        self.colors = {}

    def add_ai(self, ai):
        a = ai(self.wt)
        self.AI.append(a)
        a._init()

    def add_building(self, ai=None):
        b = mapobject.Building(self.wt)
        self.world.buildings[b] = next(self.ai_cycler)
        self.world.map.placeObject(b,
          self.world.map.getRandomSquare())

    def draw_grid(self, context):
        allocation = self.map_area.get_allocation()

        width = allocation.width
        height = allocation.height
        deltax = float(width)/self.world.mapSize
        deltay = float(height)/self.world.mapSize
        for i in xrange(self.world.mapSize):
            context.move_to(0, deltay*i)
            context.line_to(width, deltay*i)
            context.stroke()
            context.move_to(deltax*i, 0)
            context.line_to(deltax*i, height)
            context.stroke()

    def draw_map(self):
        allocation = self.map_area.get_allocation()

        cairo_context = self.map_area.window.cairo_create()

        width = allocation.width
        height = allocation.height
        map.draw_map(cairo_context, width, height,
                     self.AI, self.world)


    def map_expose_event_cb(self, widget, event):
        self.draw_map()


    def map_turn_event_cb(self, object):
        for ai in self.AI:
            ai._spin()
#            try:
#               ai.spin()
#            except Exception, e:
#                log.info("AI raised exception %s, skipping this turn for it", e)
        self.world.Turn()
        self.draw_map()

    def auto_spinner(self):
        self.map_turn_event_cb(None)
        return True

m = None
def main(ais=[]):
    import sys
    import os

    global m
    m = MapGUI()
    for ai in ais:
      m.add_ai(ai)

    for ai in m.AI:
      m.add_building()
    gobject.timeout_add(100, m.auto_spinner)
    gtk.main()

def end_game():
  for ai in m.AI:
    log.info("%s:%s", ai.__class__, ai.score)

if __name__ == "__main__":
  main()
