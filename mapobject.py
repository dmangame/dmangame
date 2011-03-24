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
                        "sight"   : 1,
                        "energy"  : 1,
                        "speed"   : 5
                       }

    def getOwner(self):
        return self.__wt.getOwner(self)
    owner = property(getOwner)

    def getStats(self):
        return copy.copy(self.__stats)
    stats = property(getStats)

class Bullet(MapObject):
    def __init__(self, unit, target):
        self.__target = target
        self.__unit = unit
    def getUnit(self):
        return self.__unit
    unit = property(getUnit)

    def getTarget(self):
        return self.__target
    target = property(getTarget)

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
        " Returns the position of this Unit on the map"
        return self.__wt.getPosition(self)
    position = property(getPosition)

    def isAlive(self):
        " Returns if this unit is alive or not in the world"
        return self.__wt.isAlive(self)
    is_alive = property(isAlive)

    def isCapturing(self):
        " Returns if this unit is currently 'capturing' "
        return self.__wt.isCapturing(self)
    is_capturing = property(isCapturing)

    def isVisible(self, unit):
        " Returns if unit is visible (in sight range) to this unit "
        return self.__wt.isVisible(unit)
    is_visible = property(isVisible)

    def getEnergy(self):
        "The energy of the unit, represents the health of the unit"
        return self.__wt.getStats(self).energy
    energy = property(getEnergy)

    def getTeam(self):
        " The owner of the unit (an ai_id) "
        return self.__wt.getTeam(self)
    team = property(getTeam)

    def getBulletPath(self, target_square):
        return self.__wt.getBulletPath(self, target_square)

    def getDistance(self, target_square):
        "Calculate distance from this unit to target square"
        return self.__wt.getDistance(self, target_square)

    def getUnitPath(self, target_square):
        "Calculate the path this unit would take to get to target square"
        return self.__wt.getUnitPath(self, target_square)

    def getVictims(self, target_square):
        "If the unit shot at target square, who would be hit?"
        return self.__wt.getVictims(self, target_square)

    def getVisibleSquares(self):
        "Return all squares that are in the range of sight of this unit"
        return self.__wt.getVisibleSquares(self)
    visible_squares = property(getVisibleSquares)

    def getVisibleBuildings(self):
        "Return all buildings that are in the range of sight of this unit"
        return self.__wt.getVisibleBuildings(self)
    visible_buildings = property(getVisibleBuildings)

    def getVisibleEnemies(self):
        "Return all enemy units that are in the range of sight of this unit"
        # Returns all (enemy?) units in shooting range
        return self.__wt.inRange(self)
    visible_enemies = property(getVisibleEnemies)

    # Main events
    def capture(self, b):
        "Queue a capture event on building b"
        return self.__wt.capture(self, b)

    def move(self, (x,y)):
        "Queue a move event to x,y"
        return self.__wt.move(self, (x, y))

    def shoot(self, (x, y)):
        "Shoot a bullet towards x,y"
        return self.__wt.shoot(self, (x, y))

