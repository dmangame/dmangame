# The world class for the game.
import ai
import ai_exceptions
import mapobject
import worldtalker
import worldmap
import math
import settings
import tuct
from unit import Unit
import maps.default as map_settings

import copy
import itertools
import logging
import random
import traceback
import threading
from collections import defaultdict


from lib.geometry import linesIntersect

try:
  import json
except ImportError:
  from django.utils import simplejson as json

from worldmap import calcDistance

import time

log = logging.getLogger("WORLD")

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


DEFAULT_UNIT_STATS = {
                      "armor"   : 1,
                      "attack"  : 1,
                      "sight"   : 1,
                      "energy"  : 1,
                      "speed"   : 1
                     }


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

        if team:
          self.team = team

        if ai_id:
          self.ai_id = ai_id

        self.unit = None


    @classmethod
    def aiVisibleSettings(self, map_module):
      stats = Stats(**DEFAULT_UNIT_STATS)

      bulletRange = map_settings.MAP_SIZE/map_settings.BULLET_RANGE_MODIFIER
      bulletSpeed = map_settings.MAP_SIZE/map_settings.BULLET_SPEED_MODIFIER

      stats.armor  = stats.armor  * map_module.ARMOR_MODIFIER
      stats.energy = stats.energy * map_module.ENERGY_MODIFIER
      stats.attack = stats.attack * map_module.ATTACK_MODIFIER * math.log(map_module.MAP_SIZE)

      stats.sight  = int((stats.sight * bulletRange) * map_module.SIGHT_MODIFIER)

      stats.speed  = int(stats.speed * (map_module.SPEED_MODIFIER * math.log(map_module.MAP_SIZE)))


      return stats

    @classmethod
    def adjustStatsForMap(self, map_module):
      return Stats.aiVisibleSettings(map_module)

# The world is responsible for maintaining the world
# as well as running each turn, checking for end conditions
# and maintaining units and the map.
class World:
    def __init__(self, mapsize=None):
        if not mapsize:
          mapsize = map_settings.MAP_SIZE

        self.mapSize = mapsize

        self.wt = worldtalker.WorldTalker(self)
        self.AI = []
        # Map a unit or AI to a team
        self.teams = {}
        # Maps a team to its AI
        self.team_map = {}
        self.ai_cycler = itertools.cycle(self.AI)
        self.ai_profiles = {}
        self.units = {} # instead of a list, it will point to the unit's attributes.
        self.all_units = {} # instead of a list, it will point to the unit's attributes.
        self.under_attack = set()
        map_settings.MAP_SIZE = mapsize
        self.map = worldmap.Map(map_settings.MAP_SIZE)
        self.currentTurn = 0
        self.events = set()
        self.unitevents = defaultdict(set)
        self.unitstatus = defaultdict(object)
        self.ai_units = defaultdict(set)
        self.ai_new_units = defaultdict(set)
        self.ai_dead_units = defaultdict(set)
        self.ai_lost_buildings = defaultdict(set)
        self.ai_new_buildings = defaultdict(set)
        self.ai_highlighted_regions = defaultdict(set)
        self.ai_highlighted_lines = defaultdict(set)

        self.execution_times = defaultdict(lambda: defaultdict(int))

        self.buildings = {}
        self.spawn_points = {}
        # These contain the amount of time left for a building to spawn a unit
        self.spawn_counters = defaultdict(int)

        if map_settings.SPAWN_POINTS:
          for coord in map_settings.SPAWN_POINTS:
            if not isValidSquare(coord, self.mapSize):
              continue

            b = mapobject.Building(self.wt)
            self.buildings[b] = None
            self.spawn_points[b] = None
            self.map.placeObject(b, coord)

        if map_settings.BUILDINGS:
          for coord in map_settings.BUILDINGS:
            if not isValidSquare(coord, self.mapSize):
              continue

            b = mapobject.Building(self.wt)
            self.buildings[b] = None
            self.map.placeObject(b, coord)

        log.info('Adding %s buildings to map', map_settings.ADDITIONAL_BUILDINGS)
        for i in xrange(map_settings.ADDITIONAL_BUILDINGS):
          self.buildings[self.placeRandomBuilding()] = None


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
        self.bulletRange = map_settings.MAP_SIZE/map_settings.BULLET_RANGE_MODIFIER
        self.bulletSpeed = map_settings.MAP_SIZE/map_settings.BULLET_SPEED_MODIFIER
        self.__initStats()

        self.visibleunits = defaultdict(set)
        self.visiblebuildings = defaultdict(set)
        self.__calcVisibility()


    def __initStats(self):
      self.unit_stats = Stats.adjustStatsForMap(map_settings)


    def placeRandomBuilding(self):
      b = mapobject.Building(self.wt)
      # Make sure this building is not within a distance
      # from any other buildings.
      attempts = 0
      best_min_guess = 0
      best_base = None
      while True:
        min_guess = map_settings.MAP_SIZE**2
        attempts += 1
        rand_square = self.map.getRandomSquare()
        within_range_of_other_building = False
        best_square = None

        dist_from_edge = math.sqrt(map_settings.MAP_SIZE) / 2
        if rand_square[0] < dist_from_edge:
          continue
        if rand_square[1] < dist_from_edge:
          continue
        if map_settings.MAP_SIZE - rand_square[0] < dist_from_edge:
          continue
        if map_settings.MAP_SIZE - rand_square[1] < dist_from_edge:
          continue

        for building in self.buildings:
          pos = self.map.getPosition(building)
          if building == b or not pos:
            continue
          spawn_distance = map_settings.BUILDING_SPAWN_DISTANCE * math.log(map_settings.MAP_SIZE)
          dist = calcDistance(pos, rand_square)
          if dist < spawn_distance:
            within_range_of_other_building = True

          if dist < min_guess:
            min_guess = dist

        if min_guess > best_min_guess:
          best_square = rand_square
          best_min_guess = min_guess

        if not within_range_of_other_building:
          # Redistribute all buildings?
          break

        if attempts >= 5 and best_square:
          log.info("Couldn't place building far enough away after five tries, taking best guess")
          rand_square = best_square
          break

      self.map.placeObject(b, rand_square)
      return b

    # Adding AIs should be done by the creator of the world.
    # This accepts a subclass ai.AI, instantiates the class
    # and places a building on the map for that AI.
    def addAI(self, ai_class):
        if map_settings.SPAWN_POINTS and len(self.AI) >= len(map_settings.SPAWN_POINTS):
          log.warn("Not adding %s to map, all spawn points taken", ai_class)
          return

        ai_player = ai_class(self.wt)
        self.AI.append(ai_player)
        self.teams[ai_player.ai_id] = ai_player.team
        self.team_map[ai_player.team] = ai_player
        ai_player.init()

        if map_settings.SPAWN_POINTS:

          while True:
            key = random.choice(self.spawn_points.keys())
            if not self.spawn_points[key]:
              self.buildings[key] = self.ai_cycler.next()
              self.spawn_points[key] = self.buildings[key]
              break

        else:
          b = self.placeRandomBuilding()
          self.buildings[b] = self.ai_cycler.next()

        log.info("Adding %s new buildings for %s AI to map", map_settings.ADDITIONAL_BUILDINGS_PER_AI, ai_player)
        for n in xrange(map_settings.ADDITIONAL_BUILDINGS_PER_AI):
          b = self.placeRandomBuilding()
          self.buildings[b] = None

        if settings.PROFILE_AI:
          import cProfile
          self.ai_profiles[ai_player] = cProfile.Profile()

        return ai_player

#    def processSpin(self, ai):
#      exc_thread = multiprocess.Process(target=ai.turn)
#      try:
#         exc_thread.start()
#         exc_thread.join(AI_CYCLE_SECONDS)
#         if exc_thread.is_alive():
#           log.info("AI %s exceeded execution time of %s seconds",
#                    ai, AI_CYCLE_SECONDS)
#           exc_thread.terminate()
#      except Exception, e:
#          traceback.print_exc()
#          if not settings.IGNORE_EXCEPTIONS:
#            raise
#          log.info("AI raised exception %s, skipping this turn for it", e)
#
    def threadedSpin(self, ai):
      from lib import thread2
      exc_thread = thread2.Thread(target=ai.turn)
      try:
         exc_thread.start()
         exc_thread.join(AI_CYCLE_SECONDS)
         if exc_thread.isAlive():
           log.info("AI %s exceeded execution time of %s seconds",
                    ai, AI_CYCLE_SECONDS)
         try:
           exc_thread.terminate()
         except threading.ThreadError:
          pass

      except Exception, e:
          traceback.print_exc()
          if not settings.IGNORE_EXCEPTIONS:
            raise
          log.info("AI raised exception %s, skipping this turn for it", e)


    def spinAI(self):
      building_owners = set(self.buildings.values())
      for ai in self.AI:
        if not self.ai_units[ai.ai_id] and not ai in building_owners:
          continue

        start_time = time.time()
        if settings.SINGLE_THREAD or settings.PROFILE_AI:
          try:
            if settings.PROFILE_AI:
              self.ai_profiles[ai].runctx("ai.turn()", { "ai" : ai }, {})
            else:
              ai.turn()
          except Exception, e:
              traceback.print_exc()
              if not settings.IGNORE_EXCEPTIONS:
                raise
              log.info("AI raised exception %s, skipping this turn for it", e)
        else:
          self.threadedSpin(ai)
        end_time = time.time()
        self.execution_times[self.currentTurn][ai] = end_time - start_time

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
          old_owner = self.buildings[building]
          self.buildings[building] = owner

          if old_owner == owner:
            log.info("BUILDING: %s recaptured %s",
                      self.teams[owner.ai_id],
                      building.building_id)
          else:
            # Reset the unit spawn timer
            self.spawn_counters[building] = map_settings.UNIT_SPAWN_MOD

            if old_owner:
              log.info("BUILDING: %s lost %s to %s",
                        self.teams[old_owner.ai_id],
                        building.building_id,
                        self.teams[owner.ai_id])
            else:
              log.info("BUILDING: %s captured %s",
                        self.teams[owner.ai_id],
                        building.building_id)


          self.ai_new_buildings[owner.ai_id].add(building)
          if old_owner:
            self.ai_lost_buildings[old_owner.ai_id].add(building)

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
                    log.info("DEATH: %s lost a unit.", (self.teams[self.units[unit].ai_id]))
                    self.died[unit] = self.map.getPosition(unit)
                    if attacker:
                        unit.killer = set((attacker,))
                else:
                    if attacker:
                        unit.killer.add(attacker)


    def __spawnUnit(self, owner, square):
        stats = copy.copy(self.unit_stats)
        stats.ai = owner
        stats.ai_id = owner.ai_id
        stats.team = owner.team
        unit = self.__createUnit(stats, square)
        self.ai_new_units[owner.ai_id].add(unit)
        return unit

    def __spawnUnits(self):
        spawned_units = False
        for b in self.buildings:

          if self.spawn_counters[b] <= 0:
            spawned_units = True
            self.spawn_counters[b] = map_settings.UNIT_SPAWN_MOD

            log.info("Spawning Units for building %s" % b.building_id)
            owner = self.buildings[b]
            square = self.map.getPosition(b)
            if owner and square:
              self.__spawnUnit(owner, square)

              log.info("SPAWN: %s gained a unit", (self.teams[owner.ai_id]))




          self.spawn_counters[b] -= 1

        if spawned_units:
          log.info("SCORES:")
          scores = self.calcScores()
          for t in scores:
            if not t in self.team_map:
              continue

            log.info("%s\t%s", t, self.team_map[t].__class__.__name__)
            for k in scores[t]:
              log.info("  %s:\t%s", k, scores[t][k])


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
            up = self.unitpaths[victim]
            for attacker in self.bulletpaths:
                # No direct fire at self.
                if attacker == victim:
                    continue

                if not up:
                  continue

                for bp in self.bulletpaths[attacker]:
                    if (up[0] == up[-1] and up[0] in bp) or \
                      linesIntersect((up[0], up[-1]), (bp[0], bp[-1])):

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
            self.ai_units[owner.ai_id].remove(unit)
            self.ai_dead_units[owner.ai_id].add(unit)

            self.__unitCleanup(unit)
        self.died = {}


    # Creates a unit with stats on square.
    # This is not a validated creation, so it will always
    # create the unit
    def __createUnit(self, stats, square):
        # modify the stats and copy them for our world.
        stats = copy.copy(stats)

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

    def __clearAfterTurnData(self):
        self.ai_new_units = defaultdict(set)
        self.ai_dead_units = defaultdict(set)

    def __clearBeforeTurnData(self):
        self.unitpaths.clear()
        self.bulletpaths.clear()
        self.collisions.clear()
        self.survivors.clear()
        self.under_attack = set()
        self.unitstatus.clear()

        # This contains information from this turn that's
        # passed to AIs
        self.ai_lost_buildings.clear()
        self.ai_new_buildings.clear()

    def __calcVisibility(self):
        old_visibleunits = self.visibleunits
        old_visiblebuildings = self.visiblebuildings

        self.visibleunits = defaultdict(set)
        self.visiblebuildings = defaultdict(set)

        om = self.map.objectMap
        ai_ids = self.ai_units.keys()
        ai_id_l = len(ai_ids)

        for unit in self.units:
          unit_square = om[unit]
          stats = self.units[unit]
          sight = stats.sight
          # Then just loop through buildings
          # It seems like this happens more than necessary?
          for building in self.buildings:
            try:
              obj_square = om[building]

              # This should be more optimized, right?
              x_block_dist = abs(unit_square[0] - obj_square[0])
              y_block_dist = abs(unit_square[1] - obj_square[1])
              if x_block_dist + y_block_dist >= sight*2:
                continue

              dist = math.sqrt(x_block_dist**2 + y_block_dist**2)
              if dist <= sight:
                  self.visiblebuildings[unit].add(building)
                  self.visiblebuildings[stats.ai.ai_id].add(building)
            except KeyError:
              pass


        for i in xrange(ai_id_l):
          ai_id = ai_ids[i]
          ai_units = self.ai_units[ai_id]
          ai_vis_obj = self.visibleunits[ai_id]
          ai_vis_bldg = self.visiblebuildings[ai_id]

          # Do a all pairs add of unit visibility
          for j in xrange(i+1, ai_id_l):
            other_ai_id = ai_ids[j]
            other_units = self.ai_units[other_ai_id]
            other_ai_vis_obj = self.visibleunits[other_ai_id]

            for unit in ai_units:
              sight = self.units[unit].sight
              unit_square = om[unit]

              unit_vis_obj = self.visibleunits[unit]
              unit_vis_bldg = self.visiblebuildings[unit]


              for other_unit in other_units:
                obj_square = om[other_unit]

                # This should be more optimized, right?
                x_block_dist = abs(unit_square[0] - obj_square[0])
                y_block_dist = abs(unit_square[1] - obj_square[1])

                enemy_sight = self.units[other_unit].sight
                if x_block_dist + y_block_dist >= max(sight, enemy_sight)*2:
                  continue

                dist = math.sqrt(x_block_dist**2 + y_block_dist**2)

                if dist <= sight:
                  unit_vis_obj.add(other_unit)
                  ai_vis_obj.add(other_unit)

                other_unit_vis_obj = self.visibleunits[other_unit]
                if dist <= enemy_sight:
                  other_unit_vis_obj.add(unit)
                  other_ai_vis_obj.add(unit)

    # The game is over when there all buildings and units are
    # owned by one AI.
    def __checkGameOver(self):
      # If all buildings are owned:
      building_owners = set(self.buildings.values())
      if None in building_owners:
        building_owners.remove(None)

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
        if isValidSquare(square, map_settings.MAP_SIZE):
            position = self.map.getPosition(unit)
            e = ShootEvent(unit, square, range)
            self.__queueEvent(e)
        else:
            raise ai_exceptions.IllegalSquareException(square)

    def createMoveEvent(self, unit, square):
        log.debug("Creating MoveEvent: Unit %s to Square %s", unit, square)
        self.__clearQueue(unit)
        position = self.map.getPosition(unit)
        if position == square:
          return

        if isValidSquare(square, map_settings.MAP_SIZE):
            e = MoveEvent(unit, square)
            # If we've already calculated the full path to destination, we
            # don't need to recalculate it. This is so that subsequent move
            # events to the same place don't require recalculation.
            if self.endpaths[unit] != square:
              pathlong = self.map.calcUnitPath(position, square)
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
            e = CaptureEvent(unit, building, map_settings.CAPTURE_LENGTH)
            self.__queueEvent(e)
        else:
            raise ai_exceptions.IllegalCaptureEvent("The unit is not in the building.")

    def highlightLine(self, ai, start, end):
      self.ai_highlighted_lines[ai].add((start, end))

    def highlightRegion(self, ai, start, end=None):
      if not end:
        width = 1
        height = 1
      else:
        width = end[0] - start[0]
        height = end[1] - start[1]

      self.ai_highlighted_regions[ai].add((start, (width, height)))

    def clearHighlights(self, ai):
      if ai in self.ai_highlighted_regions:
        del self.ai_highlighted_regions[ai]
      if ai in self.ai_highlighted_lines:
        del self.ai_highlighted_lines[ai]

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
        over = self.__checkGameOver()
        if not over:
          log.info("TURN: %s", self.currentTurn)
        else:
          log.info("TURN: %s (POST GAME)", self.currentTurn)

        self.__clearBeforeTurnData()
        self.__processPendingEvents()

        self.__createUnitPaths()
        self.__createBulletPaths()

        self.__dealBulletDamage()
        self.__dealMeleeDamage()

        # Clear Carryover data
        self.__clearAfterTurnData()
        self.__cleanupDead()
        self.__spawnUnits()

        # Recalculate what everyone in the world can see.
        self.__calcVisibility()
        self.currentTurn += 1
        over = self.__checkGameOver()
        return over

    def calcScores(self):
        alive = 0
        base_scores = { "units" : 0, "deaths" : 0, "kills" : 0, "buildings" : 0 }
        scores = defaultdict(lambda: copy.copy(base_scores))

        for ai_id in self.ai_units:
          if ai_id in self.teams:
            scores[self.teams[ai_id]]["units"] = len(self.ai_units[ai_id])

        killed_units = filter(lambda k: k.killer, self.dead_units)

        for unit in self.dead_units:
          scores[self.teams[unit]]["deaths"] += 1

        for unit in killed_units:
          teams = set(map(lambda k: self.teams[k], unit.killer))
          for t in teams:
            scores[t]["kills"] += 1

        for b in self.buildings:
          if not self.buildings[b]:
            continue

          b_team = self.buildings[b].team
          scores[b_team]["buildings"] += 1

        return scores


    def dumpScores(self):
      ai_data = []
      scores = self.calcScores()
      for ai in self.AI:
        team = ai.team
        score = scores[team]
        ai_datum = {
                     "team"         : team,
                     "units"        : score["units"],
                     "shooting"     : 0,
                     "capturing"    : 0,
                     "moving"       : 0,
                     "kills"        : score["kills"],
                     "idle"         : 0,
                     "buildings"    : score["buildings"],
                     "deaths"       : score["deaths"],
                     "time"         : self.execution_times[self.currentTurn-1][ai],
                   }
        for unit in self.units:
          status = self.unitstatus[unit]
          if self.units[unit].ai != ai:
            continue

          if status == MOVING:
            ai_datum["moving"] += 1
          elif status == SHOOTING:
            ai_datum["shooting"] += 1
          elif status == CAPTURING:
            ai_datum["capturing"] += 1
          else:
            ai_datum["idle"] += 1

        ai_data.append(ai_datum)

      return ai_data

    def dumpWorldToDict(self):
      world_data = {
                  "AI" : [],
                  "mapsize" : map_settings.MAP_SIZE,
                  "colors"  : {},
                  "names"   : {},
                  "units"   : {},
                  "buildings" : {}
                  }
      for ai_player in self.AI:
        ai_data = { "team" : ai_player.team,
                    "color" : ai.AI_COLORS[ai_player.team] }
        world_data["AI"].append(ai_data)
        world_data["colors"][ai_player.team] = ai.AI_COLORS[ai_player.team]
        world_data["names"][ai_player.team] = ai_player.__class__.__name__

      for unit in self.all_units:
        stats = self.all_units[unit]
        unit_data = {
          "team" : self.teams[unit],
          "stats" : { "sight" : stats.sight,
                      "speed" : stats.speed }
        }
        world_data["units"][unit.unit_id] = unit_data

      for building in self.buildings:
        pos = self.map.getPosition(building)
        if pos:
          building_data = { "position" : pos }
          world_data["buildings"][building.building_id] = building_data

      return world_data

    # Default World Looks like:
    # two AIs
    # two buildings
    # one unit shooting
    # one unit getting hit
    # one unit moving
    # one unit capturing
    # one AI highlighting both a region and line
    # current turn

    # TODO: The complete world skeleton should be available
    def dumpTurnToDict(self, shorten=False):
      turn_data = {  "buildings"      : [],
                     "collisions"     : [],
                     "currentturn"    : self.currentTurn,
                     "highlights"       : [],
                     "units"          : [] }

      for unit in self.units:
        unit_data = {"position" : self.map.getPosition(unit),
                     "id"  : unit.unit_id }


        if unit in self.unitpaths:
          up = self.unitpaths[unit]
          if shorten and up:
            unit_data["unitpath"] = (up[0], up[-1])
          else:
            unit_data["unitpath"] = up


        if unit in self.bulletpaths:
          unit_data["bulletpath"] = []
          for path in self.bulletpaths[unit]:
            if shorten and path:
              unit_data["bulletpath"].append((path[0], path[-1]))
            else:
              unit_data["bulletpath"].append(path)

        turn_data["units"].append(unit_data)

      for building in self.buildings:
        building_data = {
                          "id" : building.building_id,
                          "team"    : building.team
                        }

        turn_data["buildings"].append(building_data)

      for square in self.collisions:
        count = self.collisions[square]
        survivor = self.survivors[square]
        collision_data = { "position" : square,
                           "count" : count,
                           "survivor" : survivor }
        turn_data["collisions"].append(collision_data)

      for ai in self.ai_highlighted_regions:
        if not ai.__class__ in settings.SHOW_HIGHLIGHTS:
          continue

        for region in self.ai_highlighted_regions[ai]:
          highlight_data = { "start" : region[0],
                             "end"   : region[1],
                             "team"  : ai.team,
                             "shape" : "region" }

          turn_data["highlights"].append(highlight_data)

      for ai in self.ai_highlighted_lines:
        if not ai.__class__ in settings.SHOW_HIGHLIGHTS:
          continue
        for line in self.ai_highlighted_lines[ai]:
          highlight_data = { "start" : line[0],
                             "end"   : line[1],
                             "team"  : ai.team,
                             "shape" : "line" }

          turn_data["highlights"].append(highlight_data)

      return turn_data

    def printAIProfiles(self):
      import pstats
      for ai in self.ai_profiles:
        prof = self.ai_profiles[ai]
        ai_profile_file = open("%s.prof" % (ai.__class__.__name__), "w")

        # Need to strip game engine stats out
        log.info("Saving AI profile information to %s.prof", ai.__class__.__name__)
        ai_profile_file.write("*** PROFILING OUTPUT FOR %s\n" % (ai.__class__))
        p = pstats.Stats(prof, stream=ai_profile_file)
        p = p.strip_dirs()
        ai_profile_file.write("PRINTING FUNCTIONS SORTED BY TIME\n")
        p.sort_stats('time')
        p.print_stats(10)
        p.print_callers(10)

        ai_profile_file.write("PRINTING FUNCTIONS SORTED BY # CALLS\n")
        p.sort_stats('calls')
        p.print_stats(10)
        p.print_callers(10)

        ai_profile_file.close()




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
