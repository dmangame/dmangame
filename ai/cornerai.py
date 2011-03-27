import ai
import itertools
AIClass = "CornerAI"

# TODO: put this in a utility library or something
def pathsIntersect(path1, path2):
    for x,y in path1:
        for m, n in path2:
            if x == m and y == n:
                return True
    return False

class CornerAI(ai.AI):
    def __init__(self, *args, **kwargs):
        ai.AI.__init__(self, *args, **kwargs)

    def _init(self):
        self.unitsquares = {}
        self.corner_cycler = itertools.cycle([(0, 0),
                                              (self.mapsize, 0),
                                              (0, self.mapsize),
                                              (self.mapsize, self.mapsize)])


    def moveToCorner(self, unit):
        corner = self.unitsquares[unit]
        if unit.is_alive:
            if unit.position != corner:
                unit.move(corner, )
            else:
                shoot = True
                target = (self.mapsize/2, self.mapsize/2)
                bulletpath = unit.calcBulletPath(target, )[:self.wt.getBulletRange()]
                for vunit in self.my_units:
                    if unit == vunit:
                        continue
                    unit_square = self.unitsquares[vunit]
                    vunitpath = vunit.calcUnitPath(unit_square, )
                    if pathsIntersect(bulletpath, vunitpath):
                        shoot = False
                        break
                if shoot:
                    unit.shoot((self.mapsize/2, self.mapsize/2), )

    def _spin(self):
        for unit in self.my_units:
          self.moveToCorner(unit)

    def _unit_spawned(self, vunit):
      self.unitsquares[vunit] = next(self.corner_cycler)
