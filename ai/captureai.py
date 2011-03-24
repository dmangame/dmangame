
import ai
import random
import world
import itertools
from collections import defaultdict
AIClass = "CaptureAI"

class CaptureAI(ai.AI):
    def __init__(self, *args, **kwargs):
        ai.AI.__init__(self, *args, **kwargs)

    def _init(self):
        self.corner_cycler = itertools.cycle([ (0, 0), (self.mapsize, 0), (0, self.mapsize), (self.mapsize, self.mapsize) ])
        self.corners = {}
        self.torandom = defaultdict(bool)

        self.squares = {}

    def prey(self, unit):
        buildings = unit.visible_buildings
        for b in buildings:
          if b.owner == self.ai_id:
            continue

          if not unit.is_capturing:
            if unit.position == b.position:
              unit.capture(b)
            else:
              unit.move(b.position)
          return True

    def search_for_buildings(self, unit):
        corner = self.corners[unit]
        if unit.is_alive:
            if unit.position == corner:
                x = random.randint(0, self.mapsize)
                y = random.randint(0, self.mapsize)
                self.squares[unit] = (x,y)
                self.torandom[unit] = True
            try:
                if unit.position == self.squares[unit]:
                    self.torandom[unit] = False
            except KeyError:
                pass

            if self.prey(unit):
                pass
            else:
                if self.torandom[unit]:
                    unit.move(self.squares[unit])
                else:
                    unit.move(self.corners[unit])

    def _spin(self):
        for unit in self.my_units:
            self.search_for_buildings(unit)

    def _new_unit(self, unit):
        self.corners[unit] = next(self.corner_cycler)
