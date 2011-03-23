
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
        self.ms = self.wt.getMapSize() - 1
        self.corner_cycler = itertools.cycle([ (0, 0), (self.ms, 0), (0, self.ms), (self.ms, self.ms) ])
        self.corners = {}
        self.torandom = defaultdict(bool)

        self.squares = {}

    def prey(self, unit):
        buildings = unit.getVisibleBuildings()
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

    def search_for_buildings(self, unit):
        corner = self.corners[unit]
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

                if self.prey(unit):
                    pass
                else:
                    if self.torandom[unit]:
                        unit.move(self.squares[unit])
                    else:
                        unit.move(self.corners[unit])

    def _spin(self):
        for unit in self.getMyUnits():
            self.search_for_buildings(unit)

    def _new_unit(self, unit):
        self.corners[unit] = next(self.corner_cycler)
