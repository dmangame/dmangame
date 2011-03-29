# The unit class for the game.
import random
import copy
import tuct

class MapObject:
    def __init__():
        pass

class Building(MapObject):
    def __init__(self, worldtalker):
        self.__wt = worldtalker
        self.__stats = tuct.tuct({
                        "armor"   : 1,
                        "attack"  : 1,
                        "sight"   : 1,
                        "energy"  : 1,
                        "speed"   : 1
                       })

    def getTeam(self):
        " Returns the owner of the building's team"
        return self.__wt.getTeam(self)
    team = property(getTeam)

    def getStats(self):
        " Returns a copy of this building's unit stat generation"
        return copy.copy(self.__stats)
    stats = property(getStats)

    def getPosition(self):
        " Returns the position of this Unit on the map"
        return self.__wt.getPosition(self)
    position = property(getPosition)

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

