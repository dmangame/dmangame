#! /usr/bin/env python
import random
import world

class AI:
    def __init__(self, worldtalker):
        self.wt = worldtalker
        self.mapsize = self.wt.getMapSize() - 1
        self.__ai_id = random.randint(-100000000, 100000000)
        self.__team = random.randint(-100000000, 100000000)
        self.teamName = "Default AI"


    @property
    def team(self):
        return self.__team

    @property
    def ai_id(self):
        return self.__ai_id


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
