import ai
import random
import world
from collections import defaultdict
import itertools
AIClass = "KillNCapture"

class KillNCapture(ai.AI):
    def __init__(self, *args, **kwargs):
        ai.AI.__init__(self, *args, **kwargs)

    def _init(self):
        self.ms = self.wt.getMapSize() - 1
        self.corners = [
                       (0, 0),
                       (self.ms, 0),
                       (0, self.ms),
                       (self.ms, self.ms) ]
        self.torandom = defaultdict(bool)
        self.unit_corners = {}
        self.corner_cycler = itertools.cycle(self.corners)
        self.squares = {}

    def prey(self, unit):
        buildings = unit.getVisibleBuildings()
        if unit.isCapturing():
          return True

        for b in buildings:
          pos = self.wt.getPosition(b)
          if b.getOwner() == self.ai_id:
            continue

          if not unit.isCapturing():
            if unit.getPosition() == pos:
              unit.capture(b)
            else:
              unit.move(pos)

          return True

        victims = unit.getVisibleEnemies() # Only returns enemies
        if victims:
          unit.shoot(victims[0].getPosition())
          return True


    def patrol(self, unit):
        if not unit in self.squares:
            x = random.randint(0, self.ms)
            y = random.randint(0, self.ms)
            self.squares[unit] = (x,y)
        corner = self.unit_corners[unit]
        if unit.isAlive():
            if unit.getEnergy() > 0:
                if unit.getPosition() == corner:
                    x = random.randint(0, self.ms)
                    y = random.randint(0, self.ms)
                    self.squares[unit] = (x,y)
                    self.torandom[unit] = True
                try:
                    if unit.getPosition() == self.squares[unit]:
                        self.torandom[unit] = False
                except KeyError:
                    pass

                if not self.prey(unit):
                    if self.torandom[unit]:
                        unit.move(self.squares[unit])
                    else:
                        unit.move(self.unit_corners[unit])

    def _spin(self):
        for unit in self.getMyUnits():
            self.patrol(unit)

    def _new_unit(self, unit):
        self.unit_corners[unit] = next(self.corner_cycler)

