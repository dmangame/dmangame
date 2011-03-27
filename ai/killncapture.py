import ai
import random
from collections import defaultdict
import itertools
AIClass = "KillNCapture"

class KillNCapture(ai.AI):
    def __init__(self, *args, **kwargs):
        ai.AI.__init__(self, *args, **kwargs)

    def _init(self):
        self.corners = [
                       (0, 0),
                       (self.mapsize, 0),
                       (0, self.mapsize),
                       (self.mapsize, self.mapsize) ]
        self.torandom = defaultdict(bool)
        self.unit_corners = {}
        self.corner_cycler = itertools.cycle(self.corners)
        self.squares = {}

    def prey(self, unit):
        buildings = unit.visible_buildings
        if unit.is_capturing:
          return True

        for b in buildings:
          if b.team == self.team:
            continue

          if not unit.is_capturing:
            if unit.position == b.position:
              unit.capture(b)
            else:
              unit.move(b.position)

          return True

        victims = unit.visible_enemies # Only returns enemies
        if victims:
          unit.shoot(victims[0].position)
          return True


    def patrol(self, unit):
        if not unit in self.squares:
            x = random.randint(0, self.mapsize)
            y = random.randint(0, self.mapsize)
            self.squares[unit] = (x,y)
        corner = self.unit_corners[unit]
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

            if not self.prey(unit):
                if self.torandom[unit]:
                    unit.move(self.squares[unit])
                else:
                    unit.move(self.unit_corners[unit])

    def _spin(self):
        for unit in self.my_units:
            self.patrol(unit)

    def _unit_spawned(self, unit):
        self.unit_corners[unit] = next(self.corner_cycler)

