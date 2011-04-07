# The world talker is how the AI and units talk to the world.
import ai
import ai_exceptions
import copy
import mapobject
import random
from unit import Unit
import world
from collections import defaultdict
import sys
import math

from worldmap import calcDistance

# TODO: add permissions checking for all commands that are issued on a unit.
# Including visible_enemies, visible_units, etc
class WorldTalker:
    def __init__(self, world):
        self.__world = world
        self.__world.wt = self
        self.__visible_en_cache = {}
        self.__visible_en_cached_turn = -1
        self.__visible_sq_cache = {}
        self.__visible_sq_cached_turn = -1
        self.__scores_cached_turn = -1
        self.__scores_cached = {}
        self.__cached_turn = None
        self.__teams = []
        self.__stats_cache = defaultdict(dict)
        #self.__eq = world.getQueue()

    def __getStats(self, unit):
        return self.__world.all_units[unit]

    def __getOwner(self, unit):
        if unit.__class__ == Unit:
            return self.__world.all_units[unit].ai_id
        elif unit.__class__ == mapobject.Building:
            ai = self.__world.buildings[unit]
            if ai:
                return ai.ai_id


    def isAlive(self, unit):
        unit_ai_id = self.__getOwner(unit)
        if unit_ai_id == self.getID():
            return unit in self.__world.units

    def isCapturing(self, unit):
        if self.__isVisibleObject(unit):
            return self.__world.unitstatus[unit] == world.CAPTURING

    def isMoving(self, unit):
        if self.__isVisibleObject(unit):
            return self.__world.unitstatus[unit] == world.MOVING

    def isShooting(self, unit):
        if self.__isVisibleObject(unit):
            return self.__world.unitstatus[unit] == world.SHOOTING


    def __isVisibleObject(self, obj, unit=None, ai_id=None):
        if not obj: return
        if not ai_id: ai_id = self.getID()

        if self.__getOwner(obj) == ai_id:
            return True

        if unit:
            return obj in self.__world.visibleunits[unit] or obj in self.__world.visiblebuildings[unit]
        else:
            return obj in self.__world.visibleunits[ai_id] or obj in self.__world.visiblebuildings[ai_id]

    def isUnderAttack(self, unit):
        if self.__isVisibleObject(unit):
            return unit in self.__world.under_attack

    def inRange(self, unit):
        # Find all visible enemy units in range of this unit's firing
        # capabilities.
        units = []
        om = self.__world.map.objectMap
        unit_square = om[unit]
        unit_ai_id = self.__getOwner(unit)

        for vunit in self.__world.visibleunits[unit_ai_id]:
            square = om[vunit]
            if calcDistance(unit_square, square) < self.__world.bulletRange:
                units.append(vunit)
        return units

    # Get functions

    def getBulletRange(self):
        return self.__world.bulletRange

    def getCurrentTurn(self):
        return self.__world.getLifeTime()

    def getMapSize(self):
        return self.__world.mapSize

    def getPosition(self, unit):
        if unit.__class__ == mapobject.Building:
            return self.__world.map.objectMap[unit]

        if self.__isVisibleObject(unit):
            try:
                return self.__world.map.objectMap[unit]
            except KeyError:
                unit_ai_id = self.__getOwner(unit)
                ai_id = self.getID()
                if unit_ai_id == ai_id:
                    return self.__world.corpses[unit]

    def getStats(self, unit):
        ai_id = self.getID()
        stats = copy.copy(self.__world.units[unit])
        stats.ai_id = None
        return stats

    def getArmor(self, unit):
        self.checkOwner(unit)
        return self.__getStats(unit).armor

    def getAttack(self, unit):
        self.checkOwner(unit)
        return self.__getStats(unit).attack

    def getEnergy(self, unit):
        self.checkOwner(unit)
        return self.__getStats(unit).energy

    def getSight(self, unit):
        self.checkOwner(unit)
        return self.__getStats(unit).sight

    def getSpeed(self, unit):
        self.checkOwner(unit)
        return self.__getStats(unit).speed

    def getTeam(self, unit):
        try:
            return self.__world.teams[unit]
        except KeyError:
            b = self.__world.buildings[unit]
            if b:
                return b.team
        except Exception:
            pass

    def getBuildings(self):
        ai_id = self.getID()
        buildings = []
        for building in self.__world.buildings:
            if self.__getOwner(building) == ai_id:
                buildings.append(building)

        return buildings

    def getUnits(self):
        return self.__getUnits()

    def getDeadUnits(self):
        ai_id = self.getID()
        units = self.__world.ai_dead_units[ai_id] or []
        return units

    def getNewUnits(self):
        ai_id = self.getID()
        units = self.__world.ai_new_units[ai_id] or []
        return units

    def __getUnits(self, ai_id=None):
        ai_id = ai_id or self.getID()
        units = self.__world.ai_units[ai_id] or []
        return units

    # If unit is none, return all squares visible to the AI
    # else return only visible squares to the unit
    def getVisibleSquares(self, unit=None):
        ai_id = self.getID()
        if unit: self.checkOwner(unit)

        if self.__cached_turn < self.getCurrentTurn():
            self.__cached_visible_squares = {}
            self.__cached_turn = self.getCurrentTurn()

        vs_key = unit or ai_id

        if not vs_key in self.__cached_visible_squares:
            if not unit:
                squares = set()
                for unit in self.__getUnits(ai_id):
                    stats = self.__getStats(unit)
                    square = self.__world.map.getPosition(unit)
                    # TODO Properly calculate the sight of the unit.
                    moves = self.__world.map.getLegalMoves(square, stats.sight)
                    squares.update(moves)

                self.__cached_visible_squares[vs_key] = squares
                return squares
            else:
                self.checkOwner(unit, ai_id)
                self.checkAlive(unit)
                stats = self.__getStats(unit)
                square = self.__world.map.objectMap[unit]
                squares = self.__world.map.getLegalMoves(square, stats.sight)
                self.__cached_visible_squares[vs_key] = squares
        return self.__cached_visible_squares[vs_key]


    def getVisibleBuildings(self, unit=None):
        buildings = []
        if unit: self.checkOwner(unit)

        if unit:
            objs = self.__world.visiblebuildings[unit]
        else:
            ai_id = self.getID()
            objs = self.__world.visiblebuildings[ai_id]

        return list(objs)


    def getVisibleEnemies(self, unit=None):
        ai_id = self.getID()
        if unit: self.checkOwner(unit, ai_id)



        if unit:
            vis_objs = self.__world.visibleunits[unit]
            team = unit.team
        else:
            vis_objs = self.__world.visibleunits[ai_id]
            team = self.__world.teams[ai_id]

        return list(vis_objs)

    # Calculation Functions
    def calcBulletPath(self, unit, square):
        ai_id = self.getID()
        pos = self.getPosition(unit)
        if not pos:
            raise ai_exceptions.InvisibleUnitException("Can't calculate a path from %s to %s" % (unit, square))
        return self.__world.map.calcBulletPath(pos, square,
                self.__world.bulletRange)

    def calcDistance(self, unit, square):
        ai_id = self.getID()
        unit_square = self.__world.map.getPosition(unit)
        unit_ai_id = self.__getOwner(unit)


        if self.__isVisibleObject(unit, ai_id=ai_id):
            return calcDistance(unit_square, square)

    def calcUnitPath(self, unit, square):
        ai_id = self.getID()
        pos = self.__world.map.getPosition(unit)
        unit_ai_id = self.__getOwner(unit)
        if not self.__isVisibleObject(unit, ai_id=ai_id):
            return []
        return self.__world.map.calcUnitPath(pos, square)

    # Return all the units that would be hit by a bullet shot at target square.
    # (Assuming they stay still)
    def calcVictims(self, unit, square):
        ai_id = self.getID()
        self.checkOwner(unit, ai_id)
        self.checkAlive(unit)
        pos = self.__world.map.getPosition(unit)
        path = self.__world.map.calcBulletPath(pos, square, self.__world.bulletRange)
        victims = []

        for vunit in self.__world.visibleunits[ai_id]:
            vpos = self.__world.map.objectMap[vunit]
            if vpos in path:
                victims.append(vunit)
        return victims


    # AI Checking function - traverses the stakc frame until it finds 'self'
    # defined as an instance of an AI. The hope is to never let ai's get copies
    # of each other.
    def getID(self):
        # this function will print out the ai_id of the caller (or his parent, maybe)
        i = 2
        errored_once = False
        while True:
            try:
                i+=1
                try:
                    frame = sys._getframe(i)
                except ValueError:
                    i = 0
                    if errored_once:
                        return
                    errored_once = True
                    continue
                f_locals = frame.f_locals
                try:
                    if ai.AI in f_locals['self'].__class__.__bases__:
                        ai_id = f_locals['self'].ai_id
                        return ai_id
                except KeyError:
                    pass
            finally:
                try:
                    pass
                except:
                    pass

    # Unit Helper functions
    def checkOwner(self, unit, ai_id=None):
        if not ai_id: ai_id = self.getID()

        if self.__getOwner(unit) != ai_id:
            raise ai_exceptions.InvalidOwnerException("You don't own this unit")

    def checkAlive(self, unit):
        ai_id = self.getID()
        if not unit in self.__world.units:
            raise ai_exceptions.DeadUnitException("This unit is deceased")

    # Unit Functions
    def capture(self, unit, building):
        self.checkAlive(unit)
        self.checkOwner(unit)
        self.__world.createCaptureEvent(unit, building)
        return True

    def move(self, unit, square):
        self.checkAlive(unit)
        self.checkOwner(unit)
        self.__world.createMoveEvent(unit, square)
        return True

    def shoot(self, unit, square):
        self.checkAlive(unit)
        self.checkOwner(unit)
        self.__world.createShootEvent(unit, square, self.__world.bulletRange)
        return True

    def calcScore(self, team, ai_id):
        if self.__scores_cached_turn < self.__world.currentTurn:
            self.__scores_cached = self.__world.calcScores()
            self.__scores_cached_turn = self.__world.currentTurn

        if ai_id == self.getID():
            return self.__scores_cached[team]

# vim: set expandtab shiftwidth=4 softtabstop=4 textwidth=79:
