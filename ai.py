#! /usr/bin/env python
import random
import world

class AI:
    def __init__(self, worldtalker):
        self.wt = worldtalker
        self.ai_id = random.randint(-100000000, 100000000)
        self.teamName = "Default AI"


    def pathsIntersect(self, path1, path2):
        for x,y in path1:
            for m, n in path2:
                if x == m and y == n:
                    return True
        return False

    def getMyUnits(self):
        return self.wt.getUnits()

    def getVisibleSquares(self):
        return self.wt.getVisibleSquares()

    def getVisibleUnits(self):
        return self.wt.getVisibleUnits()

    # Overrode definitions
    def _init(self):
        """Needs to be implemented"""

    def _spin(self):
        """ Needs to be implemented """
# vim: set expandtab shiftwidth=4 softtabstop=4 textwidth=79:
