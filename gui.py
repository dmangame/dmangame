

import ai
import gobject
import gtk
import mapobject
import itertools
import random
import world
import worldtalker

AI_COLORS = [ (1, 0, 0), (0, 1, 0), (0, 0, 1), (1, 1, 0), (1, 0, 1), (0, 1, 1) ]


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
        self.window.resize(750, 750)
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
        print a.ai_id

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
        for owner in self.AI:
          if not owner in self.colors:
              color = random.choice(AI_COLORS)
              while color in self.colors.values():
                  color = random.choice(AI_COLORS)
              self.colors[owner] = color

        for unit in self.world.units:
            stats = self.world.units[unit]
            owner = stats.ai_id
            if not owner in self.colors:
                color = random.choice(AI_COLORS)
                while color in self.colors.values():
                    color = random.choice(AI_COLORS)
                self.colors[owner] = color

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
            owner = self.world.units[unit].ai_id
            color = map(lambda x: x/2.0, self.colors[owner])
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
            if unit.__class__ == mapobject.Unit:
                owner = self.world.units[unit].ai_id
                color = self.colors[owner]
                self.cairo_context.set_source_rgb(*color)
            elif unit.__class__ == mapobject.Bullet:
                self.cairo_context.set_source_rgb(0, 0, 0)
            elif unit.__class__ == mapobject.Building:
                owner = unit.getOwner()
                if owner:
                    color = self.colors[owner]
                    self.cairo_context.set_source_rgb(*color)
                else:
                    self.cairo_context.set_source_rgb(0.2,0.2,0.2)
            else:
                self.cairo_context.set_source_rgb(0,0,0)
            x,y = self.world.map.getPosition(unit)
            self.cairo_context.rectangle(deltax*x, deltay*y, deltax, deltay)
            self.cairo_context.fill()

    def map_expose_event_cb(self, widget, event):
        self.draw_map()


    def map_turn_event_cb(self, object):
        for ai in self.AI:
            print ""
            ai._spin()
#            try:
#               ai.spin()
#            except Exception, e:
#                print "AI raised exception %s, skipping this turn for it" % (e)
        self.world.Turn()
        self.draw_map()

    def auto_spinner(self):
        self.map_turn_event_cb(None)
        return True


if __name__ == "__main__":
    import sys
    import os
    sys.path.append("ai")
    for f in os.listdir("ai/"):
        print f
        try:
            exec "import %s" % (os.path.splitext(f)[0])
        except Exception, e:
            print e

    m = MapGUI()
#    m.add_ai(randomai.RandomAI)
    m.add_ai(cornerai.CornerAI)
    m.add_ai(sharkai.SharkAI)
#    m.add_ai(captureai.CaptureAI)
    for ai in m.AI:
      m.add_building()
    gobject.timeout_add(100, m.auto_spinner)
    gtk.main()

