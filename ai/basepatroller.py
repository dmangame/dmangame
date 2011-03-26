
import ai
import random
import itertools
from collections import defaultdict
AIClass = "BasePatrollerAI"

class BasePatrollerAI(ai.AI):
    def __init__(self, *args, **kwargs):
        ai.AI.__init__(self, *args, **kwargs)

    def _init(self):
        self.corner_cycler = itertools.cycle([ (0, 0), (self.mapsize, 0), (0, self.mapsize), (self.mapsize, self.mapsize) ])

        self.destinations = {}
        self.bases = []
        self.on_patrol = set()


    def capture_building(self, unit):
        for b in unit.visible_buildings:
          if not b in self.bases:
            self.bases.append(b)

        if unit.is_capturing:
          return True

        for b in unit.visible_buildings:
          if b.team == self.team:
            continue

          if unit.position == b.position:
            unit.capture(b)
          else:
            unit.move(b.position)

          return True

    def patrol(self, unit):
      b = random.choice(self.bases)
      self.destinations[unit] = b.position

    def explore(self, unit):
      x = random.randint(0, self.mapsize)
      y = random.randint(0, self.mapsize)
      self.destinations[unit] = (x,y)

    def search_for_buildings(self, unit):
        if not self.capture_building(unit):
            if not unit in self.destinations:
              if unit in self.on_patrol:
                self.patrol(unit)
                self.on_patrol.remove(unit)
              else:
                self.explore(unit)
                self.on_patrol.add(unit)

            if unit.position == self.destinations[unit]:
              del self.destinations[unit]
            else:
              unit.move(self.destinations[unit])

    def _spin(self):
        for unit in self.my_units:
            self.search_for_buildings(unit)
