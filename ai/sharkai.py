import ai
import random
from collections import defaultdict
import itertools
AIClass = "SharkAI"

class SharkAI(ai.AI):
    color = (0,0,0)
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
        victims = unit.visible_enemies
        if len(victims) == 0:
            return False
        unit.shoot(victims[0].position)
        return True


    def patrol(self, unit):
        if not unit in self.unit_corners:
            self.unit_corners[unit] = next(self.corner_cycler)

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

            if self.prey(unit):
                pass
            else:
                if self.torandom[unit]:
                    unit.move(self.squares[unit])
                else:
                    unit.move(self.unit_corners[unit])

    def _spin(self):
        for unit in self.my_units:
            self.patrol(unit)
