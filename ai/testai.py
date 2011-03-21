import ai
import world
AIClass = "CornerAI"

class TestAI(ai.AI):
    def __init__(self, *args, **kwargs):
        ai.AI.__init__(self, *args, **kwargs)
        
    def _init(self):
        stats = world.Stats(armor=1, attack=1, sight=1, energy=1, speed=5, team=self.teamName, ai_id=self.ai_id)
        self.unit1 = self.wt.createUnit(stats)
        self.unit1.name = "Joebe"

    def _spin(self):
        print "Spinning my AI and my AI tells me that it is the %s iteration" % (self.wt.getCurrentTurn()) 
        print "I own these units: ", self.getMyUnits()
        print "and I can see these units: %s" % self.getVisibleUnits()
        print self.unit1.testFunc()
        print self.wt.getID()