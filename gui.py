

import ai
import gc
import glob
import gobject
import gtk
import mapobject
import itertools
import random
import world
import worldtalker

import logging
log = logging.getLogger("GUI")



def random_ai_color():
  r = random.randint(0, 10)
  g = random.randint(0, 10)
  b = random.randint(0, 10)
  return map(lambda x: x/float(10), [r,g,b])



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

    def draw_grid(self):
        allocation = self.map_area.get_allocation()

        width = allocation.width
        height = allocation.height
        deltax = float(width)/self.world.mapSize
        deltay = float(height)/self.world.mapSize
        for i in xrange(self.world.mapSize):
            self.cairo_context.move_to(0, deltay*i)
            self.cairo_context.line_to(width, deltay*i)
            self.cairo_context.stroke()
            self.cairo_context.move_to(deltax*i, 0)
            self.cairo_context.line_to(deltax*i, height)
            self.cairo_context.stroke()

    def draw_map(self):
        allocation = self.map_area.get_allocation()
        self.pango_context = self.map_area.create_pango_context()
        self.gc = self.map_area.window.new_gc()
        self.cairo_context = self.map_area.window.cairo_create()
        self.surface = self.cairo_context.get_target()

        width = allocation.width
        height = allocation.height
        deltax = float(width)/self.world.mapSize
        deltay = float(height)/self.world.mapSize
        self.cairo_context.set_source_rgb(1, 1, 1)
        self.cairo_context.rectangle(0, 0, width, height)
        self.cairo_context.fill()
        self.cairo_context.set_source_rgb(0,0,0)
        self.cairo_context.set_line_width(1.0)

        #self.draw_grid()

#       Draw the squares a unit sees ( using circle) in a really light unit color.
#
        # try getting the color from our color dictionary.
        for ai in self.AI:
          if not ai.ai_id in self.colors:
              try:
                color = ai.__class__.color
              except:
                color = random_ai_color()
                while color in self.colors.values():
                    color = random_ai_color()
              self.colors[ai.ai_id] = color

        for unit in self.world.units:
            stats = self.world.units[unit]
            ai_id = stats.ai_id
            color = self.colors[ai_id]

        for building in self.world.buildings:
            owner = building.owner
            try:
              x, y = self.world.map.getPosition(building)
              self.cairo_context.set_source_rgb(0,0,0)
              self.cairo_context.rectangle(deltax*x-(deltax/2), deltay*y-(deltay/2), 2*deltax, 2*deltay)
              self.cairo_context.fill()
            except TypeError:
              pass

        for unit in self.world.units:
            if self.world.alive[unit]:
                stats = self.world.units[unit]
                x, y = self.world.map.getPosition(unit)
                color = self.colors[stats.ai_id]
                color = (color[0], color[1], color[2], .15)
                self.cairo_context.set_source_rgba(*color)
                self.cairo_context.arc(deltax*x, deltay*y, (stats.sight+1)*deltax, 0, 360.0)
                self.cairo_context.fill()

        # Draw the unit paths
        for unit in self.world.unitpaths:
            path = self.world.unitpaths[unit]
            ai_id = self.world.units[unit].ai_id
            color = map(lambda x: x/2.0, self.colors[ai_id])
            self.cairo_context.set_source_rgb(*color)
            for x,y in path:
                self.cairo_context.rectangle(deltax*x, deltay*y, deltax, deltay)
                self.cairo_context.fill()

        # Draw the bullet paths
        self.cairo_context.set_source_rgb(.75, .75, .75)
        for unit in self.world.bulletpaths:
            for path in self.world.bulletpaths[unit]:
                for x,y in path:
                    self.cairo_context.rectangle(deltax*x, deltay*y, deltax, deltay)
                    self.cairo_context.fill()

        # Draw the mapobjects in different colors (based on whether it is a bullet or unit)
        for unit in self.world.map.getAllObjects():
            x,y = self.world.map.getPosition(unit)
            if unit.__class__ == mapobject.Unit:
                ai_id = self.world.units[unit].ai_id
                color = self.colors[ai_id]
                self.cairo_context.set_source_rgb(*color)
            elif unit.__class__ == mapobject.Bullet:
                self.cairo_context.set_source_rgb(0, 0, 0)
            elif unit.__class__ == mapobject.Building:
                ai_id = unit.owner
                if ai_id in self.colors:
                    color = self.colors[ai_id]
                    self.cairo_context.set_source_rgb(*color)
                else:
                    self.cairo_context.set_source_rgb(0.2,0.2,0.2)
            else:
                self.cairo_context.set_source_rgb(0,0,0)
            self.cairo_context.rectangle(deltax*x, deltay*y, 
                                         deltax, deltay)
            self.cairo_context.fill()

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
