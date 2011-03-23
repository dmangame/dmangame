import ai
import world
AIClass = "CornerAI"

class TestAI(ai.AI):
    def __init__(self, *args, **kwargs):
        ai.AI.__init__(self, *args, **kwargs)
        
    def _init(self):
        print "Initializing"

    def _spin(self):
        print "Spinning my AI and my AI tells me that it is the %s iteration" % (self.wt.getCurrentTurn()) 
        print "I own these units: ", self.getMyUnits()
        print "and I can see these units: %s" % self.getVisibleUnits()
        print self.unit1.testFunc()
        print self.wt.getID()

    def _new_unit(self, unit):
        print "Yay, I received a new unit: %s" % (unit)
