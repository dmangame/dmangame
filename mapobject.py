# The unit class for the game.
import random
import copy

class MapObject:
    def __init__():
        pass

def building_id_generator():
  i = 0
  while True:
    yield i
    i += 1

ID_GENERATOR=building_id_generator()

class Building(MapObject):
    @classmethod
    def aiVisibleSettings(self, map_settings):
      settings = { "capture_time" : map_settings.CAPTURE_LENGTH,
                   "spawn_time" : map_settings.UNIT_SPAWN_MOD }
      return settings

    def __init__(self, worldtalker):
        self.__wt = worldtalker
        self.__building_id = ID_GENERATOR.next()

    def getBuildingID(self):
      return self.__building_id
    building_id = property(getBuildingID)

    def getTeam(self):
        " Returns the owner of the building's team"
        return self.__wt.getTeam(self)
    team = property(getTeam)

    def getPosition(self):
        " Returns the position of this Unit on the map"
        return self.__wt.getPosition(self)
    position = property(getPosition)

class Bullet(MapObject):
    @classmethod
    def aiVisibleSettings(self, map_settings):
      bulletRange = map_settings.MAP_SIZE/map_settings.BULLET_RANGE_MODIFIER
      bulletSpeed = map_settings.MAP_SIZE/map_settings.BULLET_SPEED_MODIFIER
      settings = { "speed" : bulletSpeed,
                   "range" : bulletRange }
      return settings


    def __init__(self, unit, target):
        self.__target = target
        self.__unit = unit
    def getUnit(self):
        return self.__unit
    unit = property(getUnit)

    def getTarget(self):
        return self.__target
    target = property(getTarget)

