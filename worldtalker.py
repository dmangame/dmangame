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

# TODO: add permissions checking for all commands that are issued on a unit.
# Including visible_enemies, visible_units, etc
class WorldTalker:
    def __init__(self, world):
        self.__world = world
        self.__world.wt = self
        self.__visible_cache = {}
        self.__visible_cached_turn = 0
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
            return self.__world.buildings[unit].ai_id

    def __getTeam(self, unit):
        if unit.__class__ == Unit:
            return self.__getStats(unit).team
        elif unit.__class__ == mapobject.Building:
            return self.__world.buildings[unit].team

    def __getPosition(self, mapobject):
        return self.__world.map.getPosition(mapobject)

    def isAlive(self, unit):
        if unit in self.__world.units:
            pos = self.__world.map.getPosition(unit)

        if unit in self.__world.corpses:
            pos = self.__world.corpses[unit]

        if pos and self.isVisible(pos):
            return unit in self.__world.units


    def isCapturing(self, unit):
        pos = unit.position
        if self.isVisible(pos):
            return self.__world.unitstatus[unit] == world.CAPTURING

    def isMoving(self, unit):
        pos = unit.position
        if self.isVisible(pos):
            return self.__world.unitstatus[unit] == world.MOVING

    def isShooting(self, unit):
        pos = unit.position
        if self.isVisible(pos):
            return self.__world.unitstatus[unit] == world.SHOOTING

    # Calculates if a position is visible to this AI or a specific unit
    def isVisible(self, position, unit=None):
        if not position:
            return

#        ai_id = self.getID()
#        v_key = "%s_%s_%s" % (ai_id, position, unit)
#        ct = self.__world.currentTurn
#        if self.__visible_cached_turn < ct:
#            self.__visible_cache.clear()
#            self.__visible_cached_turn = ct
#        try:
#            return self.__visible_cache[v_key]
#        except:
#            pass


        if unit:
            units = [unit]
        else:
            units = self.getUnits()

        for unit in units:
            unit_square = self.__world.map.getPosition(unit)
            if not unit_square:
                continue

            dist = self.__world.map.calcDistance(position, unit_square)
            stats = self.__getStats(unit)
            if dist <= stats.sight:
#                self.__visible_cache[v_key] = True
                return True
#        self.__visible_cache[v_key] = False
        return False

    def isUnderAttack(self, unit):
        pos = unit.position
        if self.isVisible(pos):
            return unit in self.__world.under_attack

    def inRange(self, unit):
        # relies on both sight and bullet range.
        # Find all visible units to this unit.
        origin = self.__getPosition(unit)
        units = []
        ai_id = self.__getOwner(unit)
        for vunit in self.__world.units:
            if self.__getOwner(vunit) == ai_id:
                continue
            square = self.__getPosition(vunit)
            if self.isVisible(square) and self.__world.map.calcDistance(origin,
                    square) <= self.__world.bulletRange:
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
        position = self.__getPosition(unit)
        if unit.__class__ == mapobject.Building:
            return position

        if unit in self.getUnits() or self.isVisible(position):
            return position

    def getStats(self, unit):
        ai_id = self.getID()
        stats = copy.copy(self.__world.units[unit])
        stats.ai_id = None
        return stats

    def getSight(self, unit):
        self.checkOwner(unit)
        return self.__getStats(unit).sight

    def getTeam(self, unit):
        return self.__getTeam(unit)

    def getBuildings(self):
        ai_id = self.getID()
        buildings = []
        for building in self.__world.buildings:
            if self.__getOwner(building) == ai_id:
                buildings.append(building)

        return buildings

    def getUnits(self, ai_id=None):
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
                for unit in self.getUnits(ai_id):
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
                square = self.__getPosition(unit)
                squares = self.__world.map.getLegalMoves(square, stats.sight)
                self.__cached_visible_squares[vs_key] = squares
        return self.__cached_visible_squares[vs_key]


    def getVisibleBuildings(self, unit=None):
        buildings = []
        if unit: self.checkOwner(unit)

        for b in self.__world.buildings:
            pos = self.__world.map.getPosition(b)
            if self.isVisible(pos, unit):
                buildings.append(b)

        return buildings

    def getVisibleEnemies(self, unit=None):
        ai_id = self.getID()
        if unit: self.checkOwner(unit, ai_id)
        units = []
        for vunit in self.__world.units:
            if self.__getOwner(vunit) == ai_id:
                continue

            square = self.__world.map.getPosition(vunit)
            if not square:
                raise Exception("WHAT SQUARE WAS THIS FOR: %s" % (vunit))

            if self.isVisible(square, unit):
                units.append(vunit)
        return units

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


        if unit in self.getUnits(ai_id) or self.isVisible(unit_square, unit):
            return self.__world.map.calcDistance(unit_square, square)

    def calcUnitPath(self, unit, square):
        ai_id = self.getID()
        if not unit in self.getUnits(ai_id) and \
            not unit in self.getVisibleEnemies():
            return []
        return self.__world.map.calcUnitPath(self.__world.map.getPosition(unit), square)

    # Return all the units that would be hit by a bullet shot at target square.
    # (Assuming they stay still)
    def calcVictims(self, unit, square):
        ai_id = self.getID()
        self.checkOwner(unit, ai_id)
        self.checkAlive(unit)
        path = self.__world.map.calcBulletPath(self.__world.map.getPosition(unit), square, self.__world.bulletRange)
        victims = []
        for unit in self.__world.units:
            if self.__world.map.getPosition(unit) in path:
                victims.append(unit)
        return victims


    # AI Checking function - traverses the stakc frame until it finds 'self'
    # defined as an instance of an AI. The hope is to never let ai's get copies
    # of each other.
    def getID(self):
        # this function will print out the ai_id of the caller (or his parent, maybe)
        i = 2
        while True:
            try:
                i+=1
                try:
                    frame = sys._getframe(i)
                except ValueError:
                    i = 0
                    continue
                f_locals = frame.f_locals
                try:
                    if ai.AI in f_locals['self'].__class__.__bases__:
                        ai_id = f_locals['self'].ai_id
                        del frame
                        return ai_id
                except KeyError:
                    pass
            finally:
                try:
                    del frame
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
        if ai_id == self.getID():
            return self.__world.calcScore(team)

# vim: set expandtab shiftwidth=4 softtabstop=4 textwidth=79:
