
import sys
import ai
import glib
import glob
import gobject
import gtk
import mapobject
import itertools
import time
import world
import worldtalker
import map

gtk.gdk.threads_init()
from threading import Thread, RLock

import Queue

import logging
log = logging.getLogger("GUI")





class MapGUI:
    def __init__(self):
        # Initialize Widgets
        self.window = gtk.Window()
        box = gtk.VBox()

        screen = gtk.gdk.screen_get_default()
        self.drawSize = min(screen.get_width(), screen.get_height()) / 4


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

        # Initialize our pixmap queue
        self.stopped = False
        self.pixmap_queue = Queue.Queue(100)
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
          pixmap = self.pixmap_queue.get(False)
        except Queue.Empty, e:
          return

        self.guiTurn += 1

        allocation = self.map_area.get_allocation()
        width = allocation.width
        height = allocation.height
        pixbuf = gtk.gdk.Pixbuf(gtk.gdk.COLORSPACE_RGB, True, 8, self.drawSize, self.drawSize)
        pixbuf.get_from_drawable(pixmap, self.map_area.window.get_colormap(), 0, 0, 0, 0, self.drawSize, self.drawSize)

        scaled_buf = pixbuf.scale_simple(width, height, gtk.gdk.INTERP_NEAREST)
        cairo_context_final = self.map_area.window.cairo_create()
        cairo_context_final.set_source_pixbuf(scaled_buf, 0, 0)
        cairo_context_final.paint()


    def map_expose_event_cb(self, widget, event):
        self.draw_map()

    def save_map_to_queue(self):

        width = self.drawSize
        height = self.drawSize
        pixmap = gtk.gdk.Pixmap(self.map_area.window,width,height)
        cairo_context = pixmap.cairo_create()
        map.draw_map(cairo_context, width, height,
                     self.AI, self.world)

        self.pixmap_queue.put(pixmap)


    def threaded_world_spinner(self):
        t = Thread(target=self.world_spinner)
        t.start()

    def world_spinner(self):
        while not self.stopped:

          while self.pixmap_queue.full():
            if self.stopped:
              sys.exit(0)
              return
            time.sleep(0.05)

          for ai in self.AI:
              ai._spin()
  #            try:
  #               ai.spin()
  #            except Exception, e:
  #                log.info("AI raised exception %s, skipping this turn for it", e)
          self.world.Turn()

          # Save world into a canvas that we put on a thread
          # safe queue
          while not self.lock.acquire(False):
            time.sleep(0.01)
            if self.stopped:
              sys.exit(0)

          try:
            if self.stopped:
              sys.exit(0)
            gtk.gdk.threads_enter()
            try:
              self.save_map_to_queue()
            finally:
              gtk.gdk.threads_leave()
          finally:
            self.lock.release()


    def gui_spinner(self):
        log.info("GUI Showing Turn: %s", self.guiTurn)
        try:
          self.lock.acquire()
          gtk.gdk.threads_enter()
          self.draw_map()
        except Exception, e:
          if self.map_area.window is None:
            self.stopped = True
            sys.exit(1) #window has closed
          self.stopped = False
        finally:
          gtk.gdk.threads_leave()
          self.lock.release()
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
    gobject.timeout_add(1000, m.threaded_world_spinner)
    gtk.main()

def end_game():
  for ai in m.AI:
    log.info("%s:%s", ai.__class__, ai.score)

def end_threads(*args, **kwargs):
  m.stopped = True
  gtk.gdk.threads_leave()

if __name__ == "__main__":
  main()
