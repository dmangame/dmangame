import ai
import world
AIClass = "CornerAI"

import logging
log = logging.getLogger("TestAI")

class TestAI(ai.AI):
    def __init__(self, *args, **kwargs):
        ai.AI.__init__(self, *args, **kwargs)

    def _init(self):
        log.info( "Initializing")

    def _spin(self):
        log.info( "Spinning my AI and my AI tells me that it is the %s iteration" % (self.current_turn))
        log.info( "I own these units: ", self.getMyUnits())
        log.info( "and I can see these units: %s" % self.getVisibleUnits())
        log.info( self.unit1.testFunc())
        log.info( self.wt.getID())

    def _new_unit(self, unit):
        log.info( "Yay, I received a new unit: %s" % (unit))
