import ai
import world
import itertools
AIClass = "CornerAI"

class CornerAI(ai.AI):
    def __init__(self, *args, **kwargs):
        ai.AI.__init__(self, *args, **kwargs)

    def _init(self):
        self.ms = self.wt.getMapSize() - 1
        self.unitsquares = {}
        self.corner_cycler = itertools.cycle([(0, 0),
                                              (self.ms, 0),
                                              (0, self.ms),
                                              (self.ms, self.ms)])


    def moveToCorner(self, unit):
        corner = self.unitsquares[unit]
        if unit.isAlive():
            if unit.getEnergy() > 0:
                if unit.getPosition() != corner:
                    unit.move(corner, )
                else:
                    shoot = True
                    target = (self.ms/2, self.ms/2)
                    bulletpath = unit.getBulletPath(target, )[:self.wt.getBulletRange()]
                    for vunit in self.getMyUnits():
                        if unit == vunit:
                            continue
                        unit_square = self.unitsquares[vunit]
                        vunitpath = vunit.getUnitPath(unit_square, )
                        if self.pathsIntersect(bulletpath, vunitpath):
                            shoot = False
                            break
                    if shoot:
                        unit.shoot((self.ms/2, self.ms/2), )

    def _spin(self):
        print "Spinning my AI and my AI tells me that it is the %s iteration" % (self.wt.getCurrentTurn())
        print "I own these units: ", self.getMyUnits()
        print "and I can see these units: %s" % self.getVisibleUnits()
        for vunit in self.getMyUnits():
          if not vunit in self.unitsquares:
            self.unitsquares[vunit] = next(self.corner_cycler)
        for unit in self.getMyUnits():
          self.moveToCorner(unit)

    def _new_unit(self, unit):
      print "Yay! I just got a new unit! %s" % (unit)
