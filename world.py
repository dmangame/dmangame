# The world class for the game.
import copy
import map
import mapobject
import math
from collections import defaultdict
import settings

import logging
log = logging.getLogger("WORLD")
logging.basicConfig(level=logging.INFO)


# Exceptions
class DeadUnitException(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

class IllegalSquareException(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

class InvalidStatsException(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

class InvalidOwnerException(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

class IllegalCaptureEvent(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)



# There are three types of events that can exist:
# capture event
# move event
# shoot event


class Event:
    def __init__(self):
        self.__type == None
    def getType(self):
        return self.__type

# Consists of a counter that counts down
# until square is captured.
class CaptureEvent:
    def __init__(self, unit, building, counter):
        self.__unit = unit
        self.__building = building
        self.__type = 'Capture'
        self.__count = counter

    def getType(self):
        return self.__type

    def getUnit(self):
        return self.__unit

    def getBuilding(self):
        return self.__building

    def spinCounter(self):
        self.__count -= 1

    def isFinished(self):
        return self.__count <= 0

# Consists of a unit and an end square.
class MoveEvent:
    def __init__(self, unit, square):
        self.__unit = unit
        self.__endsquare = square
        self.__type = 'Move'

    def getType(self):
        return self.__type

    def getUnit(self):
        return self.__unit


    def getEndSquare(self):
        return self.__endsquare

# Consists of a unit and a target square.
class ShootEvent:
    def __init__(self, unit, square, range):
        self.__type = 'Shoot'
        self.__unit = unit
        self.__target = square


    def getType(self):
        return self.__type

    def getUnit(self):
        return self.__unit

    def getTarget(self):
        return self.__target


def isValidSquare(square, N):
    x, y = square
    return x < N and x >= 0 and y < N and y >= 0

class Stats:
    def __init__(self, armor=1, attack=1, energy=1, sight=1, speed=1, team=None, ai_id=None):
        self.armor = armor
        self.attack = attack
        self.energy = energy
        self.sight = sight
        self.speed = speed
        self.unit = None
        self.team = team
        self.ai_id = ai_id

# The world is responsible for maintaining the world
# as well as running each turn, checking for end conditions
# and maintaining units and the map.
class World:
    def __init__(self, mapsize=settings.MAP_SIZE):
        self.AI = []
        self.units = {} # instead of a list, it will point to the unit's attributes.
        self.mapSize = mapsize
        self.map = map.Map(self.mapSize)
        self.bullets = []
        self.currentTurn = 0
        self.events = []

        self.capturing = defaultdict(bool)
        self.buildings = {}
        #self.eventQueue = EventQueue(self.events, self.mapSize)
        self.unitpaths = {}
        self.bulletpaths = {}
        self.bullets = {}
        self.alive = {}
        self.died = []
        self.dead_units = {}
        self.oldbullets = []
        self.bulletRange = self.mapSize/8
        self.bulletSpeed = self.mapSize/10


    # Private Functions
    def __handleShootEvent(self, event, garbage):
        unit = event.getUnit()
        target = event.getTarget()
        # Build the bullet with shooter, target square and range
        bullet = mapobject.Bullet(unit, target)

        self.bullets[bullet] = self.bulletRange # set the bullets range
        self.map.placeObject(bullet, self.map.getPosition(unit))
        log.debug("%s shoots towards %s", unit, target)

        garbage.append(event)


    def __handleMoveEvent(self, event, garbage):
        unit = event.getUnit()
        endsquare = event.getEndSquare()
        speed = self.units[unit].speed

        pathlong = self.map.getUnitPath(self.map.getPosition(unit), endsquare)
        pathshort = pathlong[:speed]
        self.unitpaths[unit] = pathshort
        endsquare = pathshort[-1]
        log.debug("Moving %s from %s to %s" , unit, self.map.getPosition(unit), endsquare)
        self.map.placeObject(unit, endsquare)
        if pathlong == pathshort:
            garbage.append(event)

    def __handleCaptureEvent(self, event, garbage):
        event.spinCounter()
        unit = event.getUnit()
        self.capturing[unit] = True
        if event.isFinished():
          log.debug("Finished capturing square")
          building = event.getBuilding()
          stats = self.units[unit]
          owner = stats.ai
          self.capturing[unit] = False
          self.buildings[building] = owner
          garbage.append(event)


    def __processPendingEvents(self):
        events = self.events #self.__eventQueue.getPendingEvents()
        garbage = [] # Put events to be removed in here
        for event in events:
            log.debug("Handling %s", event)
            if event.getType() == 'Capture':
                self.__handleCaptureEvent(event, garbage)
            elif event.getType() == 'Shoot':
                self.__handleShootEvent(event, garbage)
            elif event.getType() == 'Move':
                self.__handleMoveEvent(event, garbage)

        # Events are placed in the garbage in the handler and
        # are trashed at the end of all processing
        for event in garbage:
            events.remove(event)


    def __isDead(self, unit, attacker=None):
        if unit in self.units:
            if self.units[unit].energy < 1:
                self.alive[unit] = False

                if not unit in self.died:
                    log.info("%s died", (unit))
                    self.died.append(unit)
                    if attacker:
                        unit.killer = set((attacker,))
                else:
                    if attacker:
                        unit.killer.add(attacker)

    def __spawnUnit(self, statsdict, owner, square):
        stats = Stats(**statsdict)
        stats.ai = owner
        stats.ai_id = owner.ai_id
        unit = self.createUnit(stats, square)
        try:
          owner._new_unit(unit)
        except Exception, e:
          log.info("Spawn exception")
          log.info(e)
        return unit

    def __spawnUnits(self):
        if self.currentTurn % settings.UNIT_SPAWN_MOD == 0:
          log.info("Spawning Units")
          for b in self.buildings:
            owner = self.buildings[b]
            square = self.map.getPosition(b)
            if owner and square:
              self.__spawnUnit(b.getStats(), owner, square)


    def __unitCleanup(self, unit):
        del self.units[unit]
        self.map.removeObject(unit)

        # Delete any events pertaining to this nucka.
        remove_bullets = []
        for bullet in self.bullets:
            if bullet.getUnit() == unit:
              remove_bullets.append(bullet)

        for bullet in remove_bullets:
            self.map.removeObject(bullet)
            del self.bullets[bullet]

        for event in self.events:
            if event.getUnit() == unit:
                self.events.remove(event)
        if unit in self.unitpaths:
            del self.unitpaths[unit]


    def __dealBulletDamage(self):
        victims = []
        attackers = []
        for victim in self.unitpaths.keys():
            for (x, y) in self.unitpaths[victim]:
                for attacker in self.bulletpaths.keys():
                    for path in self.bulletpaths[attacker]:
                        for (m, n) in path:
                            if (x == m and y == n):
                                victims.append(victim)
                                attackers.append(attacker)
                                break
        log.debug("Attackers: %s", attackers)
        log.debug("Victims:   %s", victims)
        index = 0
        while index < len(victims):
            victim = victims[index]
            attacker = attackers[index]
            attack = self.units[attacker].attack
            armor = self.units[victim].armor
            damage = attack * math.log(self.mapSize) - armor
            if damage > 0:
                self.units[victim].energy -= int(damage)
            index += 1
            self.__isDead(victim, attacker)

    def __cleanupDead(self):
        for unit in self.died:
            self.dead_units[unit] = copy.copy(self.units[unit])
            self.__unitCleanup(unit)
        self.died = []


    # Generate unit paths for units that haven't moved this turn, so when
    # we are doing bullet/path intersections stationary units will get hit.
    def __createUnitPaths(self):
        for unit in self.units:
            if not unit in self.unitpaths:
                self.unitpaths[unit] = [self.map.getPosition(unit)]

    # Create bullet paths and move bullets to their proper place on the map.
    def __createBulletPaths(self):
        bullets = {}
        oldbullets = []
        for bullet in self.oldbullets:
            self.map.removeObject(bullet)
        for bullet in self.bullets:
            position = self.map.getPosition(bullet)
            target = bullet.getTarget()
            unit = bullet.getUnit()
            range = self.bullets[bullet]

            # Build the bullet path from the event's current position to the
            # target, with the range being the minimum of the range left on the
            # bullet and the allowed range (mapsize/10) of bullets.
            path = self.map.getBulletPath(position, target, min(range, self.bulletSpeed))
            try:
                self.bulletpaths[unit].append(path)
            except KeyError:
                self.bulletpaths[unit] = [path]
            endsquare = path[-1]

            range -= self.mapSize / 10

            # If the bullet has no more range left on it, we don't put it back
            # in our bullet list, otherwise it goes back in.
            if range > 0:
                bullets[bullet] = range
            else:
                oldbullets.append(bullet)

            # modify the bullet to reflect its new location
            self.map.placeObject(bullet, endsquare)
        self.bullets = bullets
        self.oldbullets = oldbullets

    def __clearPaths(self):
        self.unitpaths = {}
        self.bulletpaths = {}


    # Public Functions
    # Creaters
    def createUnit(self, stats, square):

        # modify the stats and copy them for our world.
        stats = copy.copy(stats)
        stats.armor  = stats.armor  * settings.ARMOR_MODIFIER
        stats.energy = stats.energy * settings.ENERGY_MODIFIER
        stats.attack = stats.attack * settings.ATTACK_MODIFIER
        stats.sight  = int((stats.sight * self.bulletRange) * settings.SIGHT_MODIFIER)

        unit = mapobject.Unit(self.wt, stats)
        self.units[unit] = stats

        stats.unit = unit
        self.alive[unit] = True

        # This is only temporary, but place the units at the 0, 0 square.
        self.map.placeObject(unit, square)
        return unit

    def createShootEvent(self, unit, square, range):
        log.debug("Creating ShootEvent: Unit %s to Square %s", unit, square)
        if isValidSquare(square, self.mapSize):
            e = ShootEvent(unit, square, range)
            self.events.append(e)
        else:
            raise IllegalSquareException(square)

    def createMoveEvent(self, unit, square):
        log.debug("Creating MoveEvent: Unit %s to Square %s", unit, square)
        if isValidSquare(square, self.mapSize):
            e = MoveEvent(unit, square)
            self.events.append(e)
        else:
            raise IllegalSquareException(square)

    def createCaptureEvent(self, unit, building):
        log.debug("Creating CaptureEvent: Unit %s to Building %s", unit, building)
        if self.map.getPosition(unit) == self.map.getPosition(building):
        #I'm trying to check if the unit is inside the building
        #we will also have to check if there are enemies inside
        #the building, but I'm not sure how
            e = CaptureEvent(unit, building, settings.CAPTURE_LENGTH)
            self.events.append(e)
        else:
            raise IllegalCaptureEvent("The unit is not in the building.")

    # GETTERS
    def getPendingEvents(self):
        return self.events

    def getQueue(self):
        return self.eventQueue

    def getLifeTime(self):
        return self.currentTurn

    def getStats(self, unit):
      # Doing the actual exception check is way slower than
      # doing the exception handling, for some reason
      try:
        try:
          return self.units[unit]
        except:
          return self.dead_units[unit]
      except:
        pass

    # Runs the world one iteration
    def Turn(self):
        log.debug("Turning the World, %s", self.currentTurn)
        self.__clearPaths()
        self.__processPendingEvents()
        self.__createUnitPaths()
        self.__createBulletPaths()
        self.__dealBulletDamage()
        self.__cleanupDead()
        self.__spawnUnits()
        self.currentTurn += 1

    def calculateScore(self, ai_id):
        alive = 0
        for unit in self.units:
          if self.wt.getOwner(unit) == ai_id:
            alive += 1

        kills = 0
        for unit in self.dead_units:
          for killer in unit.killer:
            if self.wt.getOwner(killer) == ai_id:
              kills += 1

        return alive+kills

#Map1 = {unit:position, building:position}
#2Map = {}
#for key in Map1.keys():
#    Map2[Map1[key]] = key



if __name__ == "__main__":
    world = World()
    print world
    eq = world.getQueue()
    eq.createShootEvent(None, (3,2))
    eq.createMoveEvent(None, (2,3))
    print eq
    #print eq.getPendingEvents()
    print "Pending Events"
    for event in eq.getPendingEvents():
        print event
    world.Turn()
    print "Pending Events"
    for event in eq.getPendingEvents():
        print event
