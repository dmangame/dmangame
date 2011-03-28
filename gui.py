
import ai
import mapobject
import settings
import world
import worldmap
import worldtalker

import cairo
import glib
import glob
import gobject
import gtk
import itertools
import traceback
import sys
import time

gtk.gdk.threads_init()
from threading import Thread, RLock

import Queue

import logging
log = logging.getLogger("GUI")

BUFFER_SIZE=100





class MapGUI:
    def __init__(self):
        # Initialize Widgets
        self.window = gtk.Window()
        box = gtk.VBox()

        screen = gtk.gdk.screen_get_default()
        self.drawSize = min(screen.get_width(), screen.get_height())


        self.map_area = gtk.DrawingArea()

        box.pack_start(self.map_area)
        self.window.add(box)
        self.window.show_all()
        self.map_area.connect("expose-event", self.map_expose_event_cb)
        self.window.resize(250, 250)
        self.window.connect("destroy", end_threads)

        # Initialize the world
        self.world = world.World()
        self.wt = worldtalker.WorldTalker(self.world)
        self.AI = []
        self.ai_cycler = itertools.cycle(self.AI)
        self.colors = {}
        self.guiTurn = 0

        # Initialize our pixbuf queue
        self.stopped = False
        self.frame_queue = Queue.Queue(BUFFER_SIZE)
        self.lock = RLock()

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

    def draw_map(self):

        try:
          surface = self.frame_queue.get(False)
        except Queue.Empty, e:
          return


        self.guiTurn += 1

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


    def map_expose_event_cb(self, widget, event):
        self.draw_map()

    def save_map_to_queue(self):

        width = self.drawSize
        height = self.drawSize

        surface = cairo.ImageSurface (cairo.FORMAT_ARGB32, width, height)
        cr = cairo.Context (surface)
        gdkcr = gtk.gdk.CairoContext (cr)
        worldmap.draw_map(gdkcr, width, height,
                     self.AI, self.world)

        self.frame_queue.put(surface)


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
              self.save_map_to_queue()
        except Exception, e:
            if not settings.IGNORE_EXCEPTIONS:
              self.stopped = True
              end_game()
              sys.exit(1)

    def gui_spinner(self):
        log.info("GUI Showing Turn: %s", self.guiTurn)
        try:
          if self.stopped:
            sys.exit(0)

          self.draw_map()
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
