# The world class for the game.
import ai
import ai_exceptions
import mapobject
import worldtalker
import worldmap
import math
import settings
from unit import Unit

import copy
import itertools
import logging
import traceback
from lib import thread2
from collections import defaultdict

import json

from worldmap import calcDistance

log = logging.getLogger("WORLD")
logging.basicConfig(level=logging.INFO)

AI_CYCLE_SECONDS=1.0
# There are three types of events that can exist:
# capture event
# move event
# shoot event
MOVING=0

# This isn't really a possible status for a unit, since
# shooting only lasts one turn.
SHOOTING=1
CAPTURING=2


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
    def __init__(self, mapsize=None):
        if not mapsize:
          mapsize = settings.MAP_SIZE

        self.AI = []
        self.teams = {}
        self.ai_cycler = itertools.cycle(self.AI)
        self.units = {} # instead of a list, it will point to the unit's attributes.
        self.all_units = {} # instead of a list, it will point to the unit's attributes.
        self.under_attack = set()
        self.mapSize = mapsize
        self.map = worldmap.Map(self.mapSize)
        self.currentTurn = 0
        self.events = set()
        self.unitevents = defaultdict(set)
        self.unitstatus = defaultdict(object)
        self.ai_units = defaultdict(set)

        self.buildings = {}
        #self.eventQueue = EventQueue(self.events, self.mapSize)

        self.unitfullpaths = defaultdict(bool)
        self.endpaths = defaultdict(object)
        self.unitpaths = {}
        self.bulletpaths = {}
        self.bullets = {}
        self.died = {}
        self.corpses = {}
        self.collisions = defaultdict(int)
        self.survivors = {}
        self.dead_units = {}
        self.oldbullets = []
        self.bullet_endings = defaultdict(bool)
        self.bulletRange = self.mapSize/settings.BULLET_RANGE_MODIFIER
        self.bulletSpeed = self.mapSize/settings.BULLET_SPEED_MODIFIER



        self.__calcVisibility()
        self.wt = worldtalker.WorldTalker(self)


    # Adding AIs should be done by the creator of the world.
    # This accepts a subclass ai.AI, instantiates the class
    # and places a building on the map for that AI.
    def addAI(self, ai_class):
        ai_player = ai_class(self.wt)
        self.AI.append(ai_player)
        self.teams[ai_player.ai_id] = ai_player.team
        ai_player._init()
        b = mapobject.Building(self.wt)
        self.buildings[b] = next(self.ai_cycler)

        # Make sure this building is not within a distance
        # from any other buildings.
        attempts = 0
        while True:
          attempts += 1
          rand_square = self.map.getRandomSquare()
          within_range_of_other_building = False
          for building in self.buildings:
            pos = self.map.getPosition(building)
            if building == b or not pos:
              continue
            spawn_distance = settings.BUILDING_SPAWN_DISTANCE * math.log(self.mapSize)
            if calcDistance(pos, rand_square) < spawn_distance:
              within_range_of_other_building = True


          if not within_range_of_other_building:
            # Redistribute all buildings?
            break

          if attempts >= 5:
            log.info("Couldn't place %s's building far enough away after five tries, taking last guess", ai_player)


        self.map.placeObject(b, rand_square)
        return ai_player

    def processSpin(self, ai):
      exc_thread = multiprocess.Process(target=ai._spin)
      try:
         exc_thread.start()
         exc_thread.join(AI_CYCLE_SECONDS)
         if exc_thread.is_alive():
           log.info("AI %s exceeded execution time of %s seconds",
                    ai, AI_CYCLE_SECONDS)
           exc_thread.terminate()
      except Exception, e:
          traceback.print_exc()
          if not settings.IGNORE_EXCEPTIONS:
            raise
          log.info("AI raised exception %s, skipping this turn for it", e)

    def threadedSpin(self, ai):
      exc_thread = thread2.Thread(target=ai._spin)
      try:
         exc_thread.start()
         exc_thread.join(AI_CYCLE_SECONDS)
         if exc_thread.isAlive():
           log.info("AI %s exceeded execution time of %s seconds",
                    ai, AI_CYCLE_SECONDS)
           exc_thread.terminate()
      except Exception, e:
          traceback.print_exc()
          if not settings.IGNORE_EXCEPTIONS:
            raise
          log.info("AI raised exception %s, skipping this turn for it", e)


    def spinAI(self):
      for ai in self.AI:
        if settings.PROFILE:
          ai._spin()
        else:
          self.threadedSpin(ai)

    # Private Functions
    def __handleShootEvent(self, event, garbage, to_queue):
        unit = event.getUnit()
        target = event.getTarget()
        # Build the bullet with shooter, target square and range
        log.debug("%s shoots towards %s", unit, target)
        bullet = mapobject.Bullet(unit, target)
        position = self.map.getPosition(unit)
        self.unitstatus[unit] = SHOOTING

        path = self.map.calcBulletPath(position, target, self.bulletRange)
        log.debug("Path is: %s", path)

        self.bullets[bullet] = path
        self.map.placeObject(bullet, position)

        garbage.append(event)


    def __handleMoveEvent(self, event, garbage, to_queue):
        unit = event.getUnit()
        speed = self.units[unit].speed

        self.unitstatus[unit] = MOVING
        pathlong = self.unitfullpaths[unit]

        # Go the distance
        pathshort = list(itertools.islice(iter(pathlong), 0, speed))

        path_len = len(pathshort)
        if not path_len >= speed:
          # If we pulled off no moves, check if we can make any more moves this
          # turn There is nothing remaining in the unit's path to its
          # destination, so we can finish movement.
          event_endsquare = event.getEndSquare()
          pos = self.map.getPosition(unit)
          if pos != event_endsquare:
            if pathshort:
              pos = pathshort[-1]

            log.debug("Didn't land on square, calculating new path")
            e = MoveEvent(unit, event_endsquare)
            pathlong = self.map.calcUnitPath(pos, event_endsquare)
            pathshort.insert(0, pos)
            pathshort += list(itertools.islice(iter(pathlong), 0, (speed-path_len)))
            to_queue.append(e)
          else:
            self.unitstatus[unit] = None

          garbage.append(event)

        # update internal paths.
        self.unitpaths[unit] = pathshort
        self.unitfullpaths[unit] = pathlong


        if pathshort:
          endsquare = pathshort[-1]
          log.debug("Moving %s from %s to %s" , unit, self.map.getPosition(unit), endsquare)
          self.map.placeObject(unit, endsquare)

    def __handleCaptureEvent(self, event, garbage, to_queue):
        event.spinCounter()
        unit = event.getUnit()

        if not self.units[unit]:
          garbage.append(event)
          log.debug("Died while capturing square")

        self.unitstatus[unit] = CAPTURING
        if event.isFinished():
          log.debug("Finished capturing square")
          building = event.getBuilding()
          stats = self.units[unit]
          owner = stats.ai
          self.buildings[building] = owner
          garbage.append(event)


    def __processPendingEvents(self):
        events = self.events #self.__eventQueue.getPendingEvents()
        garbage = [] # Put events to be removed in here
        to_queue = [] # Put events to be added here
        for event in events:
            log.debug("Handling %s", event)
            if event.getType() == 'Capture':
                self.__handleCaptureEvent(event, garbage, to_queue)
            elif event.getType() == 'Shoot':
                self.__handleShootEvent(event, garbage, to_queue)
            elif event.getType() == 'Move':
                self.__handleMoveEvent(event, garbage, to_queue)

        # Events are placed in the garbage in the handler and
        # are trashed at the end of all processing
        for event in garbage:
            events.remove(event)

        for event in to_queue:
            self.__queueEvent(event)

    def __isDead(self, unit, attacker=None):
        if unit in self.units:
            if self.units[unit].energy < 1:

                if not unit in self.died:
                    log.info("%s died", (unit))
                    self.died[unit] = self.map.getPosition(unit)
                    if attacker:
                        unit.killer = set((attacker,))
                else:
                    if attacker:
                        unit.killer.add(attacker)

    def __spawnUnit(self, statsdict, owner, square):
        stats = Stats(**statsdict)
        stats.ai = owner
        stats.ai_id = owner.ai_id
        stats.team = owner.team
        unit = self.__createUnit(stats, square)
        try:
          owner._unit_spawned(unit)
        except Exception, e:
          if settings.IGNORE_EXCEPTIONS:
            log.info("Spawn exception")
            log.info(e)
          else:
            traceback.print_exc()
            raise
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

        self.__clearQueue(unit)

        if unit in self.unitfullpaths:
            del self.unitfullpaths[unit]

        if unit in self.unitpaths:
            del self.unitpaths[unit]

        if unit in self.unitstatus:
            del self.unitstatus[unit]

        if unit in self.unitevents:
            del self.unitevents[unit]

    def __dealMeleeDamage(self):
        square_histogram = defaultdict(list)
        for square in self.map.squareMap:
          occupants = self.map.squareMap[square]
          square_histogram.clear()
          for occupant in occupants:
            if occupant.__class__ == Unit:
              square_histogram[self.teams[occupant]].append(occupant)

          if len(square_histogram) > 1:
            hist_counts = map(lambda x: len(square_histogram[x]), square_histogram)
            subtract_count = hist_counts[1]

            for team in square_histogram:
              units = square_histogram[team]
              for unit in units[:subtract_count]:
                # Kill Units
                self.units[unit].energy = 0
                self.__isDead(unit)
                self.collisions[square] += 1

              # There should only ever be 1 survivor from a
              # collision
              if len(units) > subtract_count:
                self.survivors[square] = team

          if not square in self.survivors:
            self.survivors[square] = None

    def __dealBulletDamage(self):
        victims = []
        attackers = []
        for victim in self.unitpaths:
            for (x, y) in self.unitpaths[victim]:
                for attacker in self.bulletpaths:
                    # No direct fire at self.
                    if attacker == victim:
                      continue

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
            damage = attack - armor
            if damage > 0:
                self.units[victim].energy -= int(damage)
                self.under_attack.add(victim)
            index += 1
            self.__isDead(victim, attacker)

    def __cleanupDead(self):
        for unit in self.died:
            stats = self.units[unit]
            self.dead_units[unit] = copy.copy(stats)
            self.corpses[unit] = self.map.getPosition(unit)
            owner = stats.ai
            try:
              owner._unit_died(unit)
            except Exception, e:
              if settings.IGNORE_EXCEPTIONS:
                log.info("Death exception")
                log.info(e)
              else:
                traceback.print_exc()
                raise e

            self.ai_units[owner.ai_id].remove(unit)

            self.__unitCleanup(unit)
        self.died = {}


    # Creates a unit with stats on square.
    # This is not a validated creation, so it will always
    # create the unit
    def __createUnit(self, stats, square):

        # modify the stats and copy them for our world.
        stats = copy.copy(stats)
        stats.armor  = stats.armor  * settings.ARMOR_MODIFIER
        stats.energy = stats.energy * settings.ENERGY_MODIFIER
        stats.attack = stats.attack * settings.ATTACK_MODIFIER * math.log(self.mapSize)
        stats.sight  = int((stats.sight * self.bulletRange) * settings.SIGHT_MODIFIER)
        stats.speed  = int(stats.speed * (settings.SPEED_MODIFIER * math.log(settings.MAP_SIZE)))

        unit = Unit(self.wt, stats)
        self.units[unit] = stats
        self.all_units[unit] = stats
        self.ai_units[stats.ai_id].add(unit)
        self.teams[unit] = stats.team

        stats.unit = unit

        # This is only temporary, but place the units at the 0, 0 square.
        self.map.placeObject(unit, square)
        return unit

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
            path = self.bullets[bullet]
            unit = bullet.getUnit()
            traversed_path = path[:self.bulletSpeed]
            remaining_path = path[self.bulletSpeed:]

            if traversed_path:

              try:
                  self.bulletpaths[unit].append(traversed_path)
              except KeyError:
                  self.bulletpaths[unit] = [traversed_path]

              endsquare = traversed_path[-1]

            if remaining_path:
                bullets[bullet] = remaining_path
            else:
                oldbullets.append(bullet)

            # modify the bullet to reflect its new location
            self.map.placeObject(bullet, endsquare)
        self.bullets = bullets
        self.oldbullets = oldbullets

    def __clearTurnData(self):
        self.unitpaths = {}
        self.bulletpaths = {}
        self.collisions.clear()
        self.survivors.clear()
        self.under_attack = set()
        self.unitstatus.clear()

    def __calcVisibility(self):
        self.visibleobjects = defaultdict(set)
        all_obj = self.map.getAllObjects()
        om = self.map.objectMap
        for unit in self.units:
          stats = self.units[unit]
          sight = stats.sight
          unit_square = om[unit]
          ai_id = stats.ai_id
          for obj in all_obj:
            obj_square = om[obj]
            if calcDistance(unit_square, obj_square) <= sight:
              self.visibleobjects[unit].add(obj)
              self.visibleobjects[ai_id].add(obj)

    # The game is over when there all buildings and units are
    # owned by one AI.
    def __checkGameOver(self):
      # If all buildings are owned:
      building_owners = set(self.buildings.values())
      if len(building_owners) == 1:
        # Check number of alive AI units?
        ai_units = filter(lambda x: x, self.ai_units.values())
        if len(ai_units) == 1:
          self.__winner = building_owners.pop()
          return True

    def __queueEvent(self, event):
        self.events.add(event)
        self.unitevents[event.getUnit()].add(event)

    def __clearQueue(self, unit):
        to_remove = []
        for event in self.unitevents[unit]:
            to_remove.append(event)

        for event in to_remove:
            try:
              self.events.remove(event)
            except KeyError:
              pass

        self.unitevents[unit].clear()

    # Public Functions
    # Creaters

    def createShootEvent(self, unit, square, range):
        log.debug("Creating ShootEvent: Unit %s to Square %s", unit, square)
        self.__clearQueue(unit)
        if isValidSquare(square, self.mapSize):
            position = self.map.getPosition(unit)
            e = ShootEvent(unit, square, range)
            self.__queueEvent(e)
        else:
            raise ai_exceptions.IllegalSquareException(square)

    def createMoveEvent(self, unit, square):
        log.debug("Creating MoveEvent: Unit %s to Square %s", unit, square)
        self.__clearQueue(unit)
        if isValidSquare(square, self.mapSize):
            e = MoveEvent(unit, square)
            # If we've already calculated the full path to destination, we
            # don't need to recalculate it. This is so that subsequent move
            # events to the same place don't require recalculation.
            if self.endpaths[unit] != square:
              pathlong = self.map.calcUnitPath(self.map.getPosition(unit),
                          square)
              self.unitfullpaths[unit] = pathlong
              self.endpaths[unit] = square

            self.__queueEvent(e)
        else:
            raise ai_exceptions.IllegalSquareException(square)

    def createCaptureEvent(self, unit, building):
        log.debug("Creating CaptureEvent: Unit %s to Building %s", unit, building)
        if self.unitstatus[unit] is CAPTURING:
          # If the unit is already in capture mode, let's
          # ignore this event.
          return

        self.__clearQueue(unit)
        if self.map.getPosition(unit) == self.map.getPosition(building):
        #I'm trying to check if the unit is inside the building
        #we will also have to check if there are enemies inside
        #the building, but I'm not sure how
            e = CaptureEvent(unit, building, settings.CAPTURE_LENGTH)
            self.__queueEvent(e)
        else:
            raise ai_exceptions.IllegalCaptureEvent("The unit is not in the building.")

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
      return self.all_units[unit]

    # Runs the world one iteration
    def Turn(self):
        log.info("Turning the World, %s", self.currentTurn)
        self.__clearTurnData()
        self.__processPendingEvents()
        self.__createUnitPaths()
        self.__createBulletPaths()
        self.__dealBulletDamage()
        self.__dealMeleeDamage()
        self.__cleanupDead()
        self.__spawnUnits()
        # Recalculate what everyone in the world can see.
        self.__calcVisibility()
        self.currentTurn += 1
        return self.__checkGameOver()

    def calcScore(self, team):
        alive = 0
        for unit in self.units:
          if self.teams[unit] == team:
            alive += 1

        kills = 0
        killed_units = filter(lambda k: k.killer, self.dead_units)

        deaths = 0
        for unit in self.dead_units:
          if self.teams[unit] == team:
            deaths += 1

        for unit in killed_units:
          teams = set(map(lambda k: self.teams[k], unit.killer))
          for t in teams:
            if t == team:
              kills += 1

        buildings = 0
        for b in self.buildings:
          if self.buildings[b].team == team:
            buildings += 1

        return { "units" : alive, "kills" : kills, "buildings" : buildings, "deaths" : deaths }


    def dumpScores(self):
      ai_data = {}
      for ai in self.AI:
        team = ai.team
        score = self.calcScore(team)
        ai_data[team] = { "units" : score["units"], "shooting" : 0, "capturing" : 0, "moving" : 0, "kills" : score["kills"], "idle" : 0, "bldgs" : score["buildings"], "name" : str(ai.__class__), "deaths" : score["deaths"] }
        for unit in self.units:
          status = self.unitstatus[unit]
          if self.units[unit].ai != ai:
            continue

          if status == MOVING:
            ai_data[team]["moving"] += 1
          elif status == SHOOTING:
            ai_data[team]["shooting"] += 1
          elif status == CAPTURING:
            ai_data[team]["capturing"] += 1
          else:
            ai_data[team]["idle"] += 1
      return ai_data

    def dumpWorldToDict(self):
      world_data = {
                  "AI" : [],
                  "mapsize" : self.mapSize,
                  "colors"  : {},
                  "units"   : {},
                  "buildings" : {}
                  }
      for ai_player in self.AI:
        ai_data = { "team" : ai_player.team,
                    "color" : ai.AI_COLORS[ai_player.team] }
        world_data["AI"].append(ai_data)
        world_data["colors"][ai_player.team] = ai.AI_COLORS[ai_player.team]

      for unit in self.units:
        stats = self.units[unit]
        unit_data = {
          "team" : self.teams[unit],
          "stats" : { "sight" : stats.sight,
                      "speed" : stats.speed }
        }
        world_data["units"][unit.unit_id] = unit_data

      for building in self.buildings:
        building_data = {
          "position" : building.position
        }
        world_data["buildings"][building.building_id] = building_data

      return world_data


    def dumpTurnToDict(self):
      turn_data = {  "units" : [],
                     "buildings" : [],
                     "bullets" : [],
                     "currentturn" : self.currentTurn,
                     "collisions"  : [] }


      for unit in self.units:
        unit_data = {"position" : self.map.getPosition(unit),
                     "unit_id"  : unit.unit_id }
        if unit in self.unitpaths:
          unit_data["unitpath"] = self.unitpaths[unit]

        if unit in self.bulletpaths:
          unit_data["bulletpath"] = self.bulletpaths[unit]

        turn_data["units"].append(unit_data)

      for building in self.buildings:
        building_data = {
                          "building_id" : building.building_id,
                          "team"    : building.team
                        }

        turn_data["buildings"].append(building_data)

      for bullet in self.bullets:
        bullet_data = { "position" : self.map.getPosition(bullet) }

        turn_data["bullets"].append(bullet_data)

      for square in self.collisions:
        count = self.collisions[square]
        survivor = self.survivors[square]
        collision_data = { "position" : square,
                           "count" : count,
                           "survivor" : survivor }
        turn_data["collisions"].append(collision_data)

      return turn_data

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
