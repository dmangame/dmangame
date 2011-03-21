import ai
import random
import world
AIClass = "SharkAI"

class SharkAI(ai.AI):
    def __init__(self, *args, **kwargs):
        ai.AI.__init__(self, *args, **kwargs)
        
    def _init(self):
        stats = world.Stats(armor=1, attack=1, sight=1, energy=1, speed=5, team=self.teamName, ai_id=self.ai_id)
        self.unit1 = self.wt.createUnit(stats)
        self.unit2 = self.wt.createUnit(stats)
        self.unit3 = self.wt.createUnit(stats)
        self.unit4 = self.wt.createUnit(stats)
        self.unit1.name = 'jaws'
        self.unit2.name = 'whitey'
        self.unit3.name = 'bigtooth'
        self.unit4.name = 'hump'
        self.ms = self.wt.getMapSize() - 1
        self.corners = { 
                            self.unit1 : (0, 0), 
                            self.unit2 : (self.ms, 0),
                            self.unit3 : (0, self.ms),
                            self.unit4 : (self.ms, self.ms) 
        }
        self.torandom = { self.unit1 : False,
                          self.unit2 : False,
                          self.unit3 : False,
                          self.unit4 : False
        }

        self.squares = {}
    
    def prey(self, unit):
        victims = unit.inRange()
        if len(victims) == 0:
            return False
        unit.shoot(victims[0].getPosition())
        return True

        
    def patrol(self, unit):
        corner = self.corners[unit]
        if unit.isAlive():
            if unit.getEnergy() > 0:
                if unit.getPosition() == corner:
                    x = random.randint(0, self.wt.getMapSize()-1)
                    y = random.randint(0, self.wt.getMapSize()-1)
                    self.squares[unit] = (x,y)
                    self.torandom[unit] = True
                try:
                    if unit.getPosition() == self.squares[unit]:
                        self.torandom[unit] = False
                except KeyError:
                    pass
                
                if self.prey(unit):
                    pass
                else:
                    if self.torandom[unit]:
                        unit.move(self.squares[unit])
                    else:
                        unit.move(self.corners[unit])
                
    def _spin(self):
        print "Spinning my AI and my AI tells me that it is the %s iteration" % (self.wt.getCurrentTurn()) 
        print "I own these units: ", self.getMyUnits()
        # I am gonna tell my AI to randomly shoot in a direction or move to a random square.
        # Cool, right? 

        for unit in self.getMyUnits():
            self.patrol(unit)
        #print "and I can see these squares: %s" % self.getVisibleSquares()
        print "and I can see these units: %s" % self.getVisibleUnits()
