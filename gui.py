
import ai
import mapobject
import settings
import world
import worldmap
import worldtalker

# For Key
import pygtk_chart
import pygtk_chart.pie_chart
import pygtk_chart.bar_chart

import cairo
import glib
import glob
import gobject
import gtk
import itertools
import traceback
import sys
import time
import traceback

gtk.gdk.threads_init()
from threading import Thread, RLock

import Queue

import logging
log = logging.getLogger("GUI")

BUFFER_SIZE=100

import pango
AI_FONT = pango.FontDescription('Sans 10')


AI_STATS=[
  'moving',
  'shooting',
  'capturing',
  'idle',
  'kills',
  'units'
  ]

AI_STAT_COLORS={
  'bldgs'          : (0.0,0.5,0.0),
  'moving'         : (0.0,0.5,0.0),
  'shooting'       : (0.5,0.0,0.0),
  'capturing'      : (0.0,0.0,0.5),
  'idle'           : (0.5,0.5,0.5),
  'kills'          : (0.5,0.0,0.0),
  'units'          : (0.0,0.0,0.5),
  }

class MapGUI:
    def __init__(self):
        # Initialize Widgets

        self.initialize_map_window()
        # Initialize the world
        self.world = world.World()
        self.wt = worldtalker.WorldTalker(self.world)
        self.AI = []
        self.ai_drawables = {}
        self.ai_cycler = itertools.cycle(self.AI)
        self.colors = {}
        self.guiTurn = 0

        # Initialize our pixbuf queue
        self.stopped = False
        self.frame_queue = Queue.Queue(BUFFER_SIZE)
        self.lock = RLock()

    def initialize_map_window(self):
        self.window = gtk.Window()
        box = gtk.HBox()
        self.key_area = gtk.VBox()
        key_outer = gtk.ScrolledWindow()
        key_outer.add_with_viewport(self.key_area)
        key_outer.set_size_request(200, -1)

        screen = gtk.gdk.screen_get_default()
        self.drawSize = min(screen.get_width(), screen.get_height())
        box.pack_end(key_outer, False)


        self.map_area = gtk.DrawingArea()

        box.pack_start(self.map_area, True)
        self.window.add(box)
        self.window.show_all()
        self.map_area.connect("expose-event", self.map_expose_event_cb)
        self.window.resize(250, 250)
        self.window.connect("destroy", end_threads)


    def draw_key_data(self):
        pass


    def add_ai(self, ai_class):
        a = ai_class(self.wt)
        self.AI.append(a)
        vbox = gtk.VBox()
        vbox.pack_start(gtk.Label(str(ai_class).split(".")[-1]))
        p_chart = pygtk_chart.bar_chart.BarChart()
        p_chart.set_mode(pygtk_chart.bar_chart.MODE_HORIZONTAL)
        b_chart = pygtk_chart.bar_chart.BarChart()
        vbox.pack_start(p_chart)
        vbox.pack_start(b_chart)
        for stat in ['moving', 'shooting', 'capturing', 'idle']:
          bar = pygtk_chart.bar_chart.Bar(stat, 0, stat[:3])
          bar.set_color(gtk.gdk.Color(*AI_STAT_COLORS[stat]))
          p_chart.add_bar(bar)


        for stat in ['units', 'kills', 'bldgs']:
          area = pygtk_chart.bar_chart.Bar(stat, 0, stat)
          area.set_color(gtk.gdk.Color(*AI_STAT_COLORS[stat]))
          b_chart.add_bar(area)

        b_chart.grid.set_visible(False)
        b_chart.set_draw_labels(True)
        p_chart.set_draw_labels(True)
        p_chart.grid.set_visible(False)
        self.ai_drawables[a] = (p_chart, b_chart)
        self.key_area.pack_start(vbox)
        a._init()

    def add_building(self, ai=None):
        b = mapobject.Building(self.wt)
        self.world.buildings[b] = next(self.ai_cycler)
        self.world.map.placeObject(b,
          self.world.map.getRandomSquare())

    def draw_grid(self, context):
        width = self.drawSize
        height = self.drawSize
        deltax = float(width)/self.drawSize
        deltay = float(height)/self.drawSize
        for i in xrange(self.world.mapSize):
            context.move_to(0, deltay*i)
            context.line_to(width, deltay*i)
            context.stroke()
            context.move_to(deltax*i, 0)
            context.line_to(deltax*i, height)
            context.stroke()

    def draw_map(self, surface):

        self.guiTurn += 1

        # Draw the map
        cairo_context_final = self.map_area.window.cairo_create()
        pattern = cairo.SurfacePattern(surface)

        allocation = self.map_area.get_allocation()

        width = allocation.width
        height = allocation.height

        sx = width / float(self.drawSize)
        sy = height / float(self.drawSize)
        matrix = cairo.Matrix(xx=sx, yy=sy)
        cairo_context_final.transform(matrix)
        cairo_context_final.set_source(pattern)
        cairo_context_final.paint()



    def draw_map_and_ai_data(self):
        try:
          surface, ai_data = self.frame_queue.get(False)
        except Queue.Empty, e:
          return

        self.draw_map(surface)
        self.update_ai_stats(ai_data)

    def update_ai_stats(self, ai_data):
        for ai_player in ai_data:

          p_chart, b_chart = self.ai_drawables[ai_player]
          color = gtk.gdk.Color(*ai.AI_COLORS[ai_player.team])
          b_chart.background.set_property('color', color)
          p_chart.background.set_property('color', color)
          for k in ['units', 'kills','bldgs']:
            v = ai_data[ai_player][k]
            bar = b_chart.get_area(k)
            bar.set_value(v)

          for k in ['moving', 'shooting', 'idle', 'capturing']:
            v = ai_data[ai_player][k]
            bar = p_chart.get_area(k)
            bar.set_value(v)

        self.key_area.show_all()



    def map_expose_event_cb(self, widget, event):
        self.draw_map_and_ai_data()

    def save_map_and_ai_data_to_queue(self):

        width = self.drawSize
        height = self.drawSize

        surface = cairo.ImageSurface (cairo.FORMAT_ARGB32, width, height)
        cr = cairo.Context (surface)
        gdkcr = gtk.gdk.CairoContext (cr)
        worldmap.draw_map(gdkcr, width, height,
                     self.AI, self.world)

        ai_data = {}
        for ai in self.AI:
          ai_data[ai] = { "units" : ai.score["units"], "shooting" : 0, "capturing" : 0, "moving" : 0, "kills" : ai.score["kills"], "idle" : 0, "bldgs" : ai.score["buildings"]}
          for unit in self.world.units:
            status = self.world.unitstatus[unit]
            if self.world.units[unit].ai != ai:
              continue

            if status == world.MOVING:
              ai_data[ai]["moving"] += 1
            elif status == world.SHOOTING:
              ai_data[ai]["shooting"] += 1
            elif status == world.CAPTURING:
              ai_data[ai]["capturing"] += 1
            else:
              ai_data[ai]["idle"] += 1

        self.frame_queue.put((surface, ai_data))


    def threaded_world_spinner(self):
        t = Thread(target=self.world_spinner)
        t.start()

    def world_spinner(self):

        try:
            while not self.stopped:

              while self.frame_queue.full():
                if self.stopped:
                  sys.exit(0)
                  return
                time.sleep(0.05)

              for ai in self.AI:
                  try:
                     ai._spin()
                  except Exception, e:
                      traceback.print_exc()
                      if not settings.IGNORE_EXCEPTIONS:
                        raise
                      log.info("AI raised exception %s, skipping this turn for it", e)
              self.world.Turn()

              # Save world into a canvas that we put on a thread
              # safe queue
              self.save_map_and_ai_data_to_queue()
        except Exception, e:
            traceback.print_exc()
            if not settings.IGNORE_EXCEPTIONS:
              self.stopped = True
              end_game()
              sys.exit(1)

    def gui_spinner(self):
        log.info("GUI Showing Turn: %s", self.guiTurn)
        try:
          if self.stopped:
            sys.exit(0)

          self.draw_map_and_ai_data()
        except Exception, e:
          traceback.print_exc()
          if not settings.IGNORE_EXCEPTIONS:
            if self.map_area.window is None:
              self.stopped = True
              end_game()
              sys.exit(1) #window has closed
            self.stopped = False
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
    gobject.timeout_add(100, m.gui_spinner)
    m.threaded_world_spinner()
    gtk.main()

def end_game():
  for ai in m.AI:
    log.info("%s:%s", ai.__class__, ai.score)

def end_threads(*args, **kwargs):
  m.stopped = True
  gtk.gdk.threads_leave()

if __name__ == "__main__":
  main()
