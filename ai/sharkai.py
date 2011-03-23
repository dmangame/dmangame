import ai
import random
import world
from collections import defaultdict
import itertools
AIClass = "SharkAI"

class SharkAI(ai.AI):
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
        victims = unit.inRange()
        if len(victims) == 0:
            return False
        unit.shoot(victims[0].getPosition())
        return True


    def patrol(self, unit):
        if not unit in self.unit_corners:
            self.unit_corners[unit] = next(self.corner_cycler)

        if not unit in self.squares:
            x = random.randint(0, self.wt.getMapSize()-1)
            y = random.randint(0, self.wt.getMapSize()-1)
            self.squares[unit] = (x,y)
        corner = self.unit_corners[unit]
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
                        unit.move(self.unit_corners[unit])

    def _spin(self):
        print "Spinning my AI and my AI tells me that it is the %s iteration" % (self.wt.getCurrentTurn())
        print "I own these units: ", self.getMyUnits()
        # I am gonna tell my AI to randomly shoot in a direction or move to a random square.
        # Cool, right?

        for unit in self.getMyUnits():
            self.patrol(unit)
        #print "and I can see these squares: %s" % self.getVisibleSquares()
        print "and I can see these units: %s" % self.getVisibleUnits()
