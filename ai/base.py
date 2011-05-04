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
    """
    A basic AI implementation, required by all AIs as an ancestor class
    """

    def __init__(self, worldtalker):
        self.wt = worldtalker
        self.mapsize = self.wt.getMapSize() - 1

        self.__ai_id = str(ID_GENERATOR.next())
        self.__team = str(TEAM_GENERATOR.next())
        self.teamName = "Default AI"


    @property
    def team(self):
        """
        the team of this AI instance
        """
        return self.__team

    @property
    def ai_id(self):
        """
        the AI's private ID, it's used by the worldtalker for identification
        purposes.
        """
        return self.__ai_id

    @property
    def new_units(self):
        """
        all units that were spawned this turn for this AI instance
        """
        return self.wt.getNewUnits()

    @property
    def dead_units(self):
        """
        all units that died the past turn for this AI instance.
        """
        return self.wt.getDeadUnits()

    @property
    def new_buildings(self):
        """
        all buildings that were captured the past turn by this AI instance.
        """
        return self.wt.getNewBuildings()

    @property
    def lost_buildings(self):
        """
        all buildings that were lost this past turn by this AI instance.
        """
        return self.wt.getLostBuildings()


    @property
    def my_units(self):
        """
        living units that belong to this AI instance
        """
        return self.wt.getUnits()

    @property
    def my_buildings(self):
        """
        all buildings that belong to this AI instance
        """

        return self.wt.getBuildings()

    @property
    def visible_buildings(self):
        """
        all visible buildings
        """
        return self.wt.getVisibleBuildings()

    @property
    def visible_squares(self):
        """
        all visible squares to the AI (the set of all squares visible to the AI's units)
        """
        return self.wt.getVisibleSquares()

    @property
    def visible_enemies(self):
        """
        all visible enemy units to the AI
        """
        return self.wt.getVisibleEnemies()

    @property
    def score(self):
        """
        the AI's current score
        """
        return self.wt.calcScore(self.team, self.ai_id)

    @property
    def current_turn(self):
        """
        the world's current iteration
        """
        return self.wt.getCurrentTurn()

    def highlightLine(self, start, end):
        """Adds a highlight line to the map from start to end"""
        self.wt.highlightLine(self, start, end)

    def highlightRegion(self, start, end=None):
        """Adds a highlight region to the map from start to end"""
        self.wt.highlightRegion(self, start, end)

    def clearHighlights(self):
        """Clear all highlighted areas by the AI on the map"""
        self.wt.clearHighlights(self)

    # Overrode definitions
    def init(self):
        """
        Needs to be implemented by AI

        This function is called at the beginning of the game by the world.

        The AI should initialize itself and can inspect world information in
        this function.

        """

    def turn(self):
        """
        Needs to be implemented by AI.

        This function is called once per turn by the world during game execution.

        The AI can inspect the world and queue events via a unit's API during
        this function.


        """

class AI(BareAI):
    def init(self, *args, **kwargs):
        self._init()

    def turn(self):
        """
        calls into the _spin, _init, _new_unit and _unit_died methods of
        the implemented AI.

        """
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
        """Needs to be implemented by AI"""

    def _spin(self):
        """ Needs to be implemented by AI"""

    def _unit_spawned(self, unit):
        """ Needs to be implemented by AI"""

    def _unit_died(self, unit):
        """ Needs to be implemented by AI"""

# Objects to generate docstrings for
__all__ = [ "AI" ]
# vim: set expandtab shiftwidth=4 softtabstop=4 textwidth=79:
