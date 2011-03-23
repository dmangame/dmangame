
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
        buildings = self.wt.getVisibleBuildings(unit)
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
        if not unit in self.corners:
          self.corners[unit] = next(self.corner_cycler)
        corner = self.corners[unit]
        if unit.isAlive():
            if unit.getEnergy() > 0:
                if unit.getPosition() == corner:
                    x = random.randint(0, self.wt.getMapSize()-1)
                    y = random.randint(0, self.wt.getMapSize()-1)
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
        print "Spinning my AI and my AI tells me that it is the %s iteration" % (self.wt.getCurrentTurn())
        print "I own these units: ", self.getMyUnits()
        # I am gonna tell my AI to randomly shoot in a direction or move to a random square.
        # Cool, right?

        for unit in self.getMyUnits():
            self.search_for_buildings(unit)
        #print "and I can see these squares: %s" % self.getVisibleSquares()
        print "and I can see these units: %s" % self.getVisibleUnits()
