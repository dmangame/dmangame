#! /usr/bin/env python
import random
import world

class AI:
    def __init__(self, worldtalker):
        self.wt = worldtalker
        self.mapsize = self.wt.getMapSize() - 1
        self.ai_id = random.randint(-100000000, 100000000)
        self.teamName = "Default AI"


    def getMyUnits(self):
        return self.wt.getUnits()
    my_units = property(getMyUnits)

    def getVisibleSquares(self):
        return self.wt.getVisibleSquares()
    visible_squares = property(getVisibleSquares)

    def getVisibleUnits(self):
        return self.wt.getVisibleUnits()
    visible_units = property(getVisibleUnits)

    def calculateScore(self):
        return self.wt.calculateScore(self.ai_id)
    score = property(calculateScore)

    def currentTurn(self):
        return self.wt.getCurrentTurn()
    current_turn = property(currentTurn)

    # Overrode definitions
    def _init(self):
        """Needs to be implemented"""

    def _spin(self):
        """ Needs to be implemented """

    def _new_unit(self, unit):
        """ Needs to be implemented """

# vim: set expandtab shiftwidth=4 softtabstop=4 textwidth=79:
