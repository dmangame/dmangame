#! /usr/bin/env python
import random
import traceback
import logging
log = logging.getLogger("AI")

import settings
import string

used_ids = set()
def id_generator():
    len = 2
    while True:
        i = ''.join(random.choice(string.letters) for i in xrange(len))
        if i not in used_ids:
            used_ids.add(i)
            yield i

ID_GENERATOR=id_generator()
TEAM_GENERATOR=id_generator()

class BareAI(object):
    def __init__(self, worldtalker):
        self.wt = worldtalker
        self.mapsize = self.wt.getMapSize() - 1

        self.__ai_id = str(next(ID_GENERATOR))
        self.__team = str(next(TEAM_GENERATOR))
        self.teamName = "Default AI"


    @property
    def team(self):
        """
        The team of this AI instance
        """
        return self.__team

    @property
    def ai_id(self):
        return self.__ai_id

    @property
    def new_units(self):
        """
        Returns all units that were spawned this turn for this AI instance
        """
        return self.wt.getNewUnits()

    @property
    def dead_units(self):
        """
        Returns all units that died the past turn for this AI instance.
        """
        return self.wt.getDeadUnits()

    @property
    def new_buildings(self):
        """
        Returns all buildings that were captured the past turn by this AI instance.
        """
        return self.wt.getNewBuildings()

    @property
    def lost_buildings(self):
        """
        Returns all buildings that were lost this past turn by this AI instance.
        """
        return self.wt.getLostBuildings()


    def getMyUnits(self):
        """
        Returns living units that belong to this AI instance
        """
        return self.wt.getUnits()
    my_units = property(getMyUnits)

    def getMyBuildings(self):
        """
        Returns all buildings that belong to this AI instance
        """

        return self.wt.getBuildings()
    my_buildings = property(getMyBuildings)

    def getVisibleBuildings(self):
        """
        Returns all visible buildings
        """
        return self.wt.getVisibleBuildings()
    visible_buildings = property(getVisibleBuildings)

    def getVisibleSquares(self):
        """
        Returns all visible squares to the AI (the set of all squares visible to the AI's units)
        """
        return self.wt.getVisibleSquares()
    visible_squares = property(getVisibleSquares)

    def getVisibleEnemies(self):
        """
        Returns all visible enemy units to the AI
        """
        return self.wt.getVisibleEnemies()
    visible_enemies = property(getVisibleEnemies)

    def calcScore(self):
        """
        Returns the AI's current score - number of units killed + number of
        units still alive
        """
        return self.wt.calcScore(self.team, self.ai_id)
    score = property(calcScore)

    def currentTurn(self):
        """
        Returns the world's current iteration
        """
        return self.wt.getCurrentTurn()
    current_turn = property(currentTurn)

    def highlightLine(self, start, end):
        self.wt.highlightLine(self, start, end)

    def highlightRegion(self, start, end=None):
        self.wt.highlightRegion(self, start, end)

    def clearHighlights(self):
        self.wt.clearHighlights(self)

    # Overrode definitions
    def init(self):
        """Needs to be implemented"""

    def turn(self):
        """Needs to be implemented"""

class AI(BareAI):
    def init(self, *args, **kwargs):
        self._init()

    def turn(self):
        for unit in self.new_units:
            try:
                self._unit_spawned(unit)
            except Exception, e:
              if settings.IGNORE_EXCEPTIONS:
                log.info("Spawn exception")
                log.info(e)
              else:
                traceback.print_exc()
                raise e

        for unit in self.dead_units:
            try:
                self._unit_died(unit)
            except Exception, e:
              if settings.IGNORE_EXCEPTIONS:
                log.info("Death exception")
                log.info(e)
              else:
                traceback.print_exc()
                raise e

        self._spin()

    # Overrode definitions
    def _init(self):
        """Needs to be implemented"""

    def _spin(self):
        """ Needs to be implemented """

    def _unit_spawned(self, unit):
        """ Needs to be implemented """

    def _unit_died(self, unit):
        """ Needs to be implemented """

# vim: set expandtab shiftwidth=4 softtabstop=4 textwidth=79:
