# The unit class for the game.
import random
import copy

class MapObject:
    def __init__():
        pass

# Buildings have to have owners, but the owner should only be settable by the World,
# therefore, we are going to use the world as a key when trying to set the owner, so for each building instantiated,
# it should be passed the World in the constructor
class Building(MapObject):
    def __init__(self, worldtalker):
        self.__wt = worldtalker
        self.__stats = {
                        "armor"   : 1,
                        "attack"  : 1,
                        "sight"   : 5,
                        "energy"  : 1,
                        "speed"   : 5
                       }

    def getOwner(self):
        return self.__wt.getOwner(self)

    def getStats(self):
        return copy.copy(self.__stats)

    def spawnUnit(self):
        pass

class Bullet(MapObject):
    def __init__(self, unit, target):
        self.__target = target
        self.__unit = unit
    def getUnit(self):
        return self.__unit
    def getTarget(self):
        return self.__target

class Unit(MapObject):
    # What can a unit do?
    # It can shoot, move and capture a square. Can two units occupy the same
    # square? I forget.

    def __init__(self, worldtalker, stats):
        self.__wt = worldtalker
        self.__stats = stats

    def testFunc(self):
        return self.__wt.getID()

    # Some functions the unit has access to.
    # The way it will use all these functions is by asking the worldtalker to do all
    # teh dirty business.

    def getPosition(self):
        return self.__wt.getPosition(self)

    def inRange(self):
        # Returns all (enemy?) units in shooting range
        return self.__wt.inRange(self)

    def isAlive(self):
        return self.__wt.isAlive(self)

    def isCapturing(self):
        return self.__wt.isCapturing(self)

    def getVictims(self, target_square):
        return self.__wt.getVictims(self, target_square)

    def getDistance(self, target_square):
        return self.__wt.getDistance(self, target_square)

    def getBulletPath(self, target_square):
        return self.__wt.getBulletPath(self, target_square)

    def getUnitPath(self, target_square):
        return self.__wt.getUnitPath(self, target_square)

    def getVisibleSquares(self):
        return self.__wt.getVisibleSquares(self)

    def isVisible(self, unit):
        return self.__wt.isVisible(unit)

    def getEnergy(self):
        return self.__wt.getStats(self).energy

    def getTeam(self):
        return self.__wt.getTeam(self)


    # Main events
    def capture(self, b):
        return self.__wt.capture(self, b)

    def move(self, (x,y)):
        return self.__wt.move(self, (x, y))

    def shoot(self, (x, y)):
        return self.__wt.shoot(self, (x, y))

