import ai
import random
import world
AIClass = "RandomAI"

class RandomAI(ai.AI):
    def __init__(self, *args, **kwargs):
        ai.AI.__init__(self, *args, **kwargs)
        
    def _init(self):
        stats = world.Stats(armor=1, attack=1, sight=1, energy=1, speed=5, team=self.teamName, ai_id=self.ai_id)
        self.unit1 = self.wt.createUnit(stats)
        self.unit2 = self.wt.createUnit(stats)
        self.unit3 = self.wt.createUnit(stats)
        self.unit4 = self.wt.createUnit(stats)

    def _spin(self):
        print "Spinning my AI and my AI tells me that it is the %s iteration" % (self.wt.getCurrentTurn()) 
        print "I own these units: ", self.getMyUnits()
        # I am gonna tell my AI to randomly shoot in a direction or move to a random square.
        # Cool, right? 
        for unit in self.getMyUnits():
            func = random.choice([unit.move, unit.shoot])
            while True:
                try:
                    square = (random.randint(0, self.wt.getMapSize()), \
                                random.randint(0, self.wt.getMapSize()))
                    func(square)
                    break
                except world.IllegalSquareException:
                    pass        
            
        #print "and I can see these squares: %s" % self.getVisibleSquares()
        print "and I can see these units: %s" % self.getVisibleUnits()
