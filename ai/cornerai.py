import ai
import world
AIClass = "CornerAI"

class CornerAI(ai.AI):
    def __init__(self, *args, **kwargs):
        ai.AI.__init__(self, *args, **kwargs)
        
    def _init(self):
        stats = world.Stats(armor=1, attack=1, sight=1, energy=1, speed=5, team=self.teamName, ai_id=self.ai_id)
        self.unit1 = self.wt.createUnit(stats)
        self.unit2 = self.wt.createUnit(stats)
        self.unit3 = self.wt.createUnit(stats)
        self.unit4 = self.wt.createUnit(stats)
        self.unit1.name = 'anton'
        self.unit2.name = 'greg'
        self.unit3.name = 'stubs'
        self.unit4.name = 'Maximus'
        self.ms = self.wt.getMapSize() - 1
        self.unitsquares = { 
                            self.unit1 : (0, 0), 
                            self.unit2 : (self.ms, 0),
                            self.unit3 : (0, self.ms),
                            self.unit4 : (self.ms, self.ms) 
        }
        
        
    def moveToCorner(self, unit):
        corner = self.unitsquares[unit]
        if unit.isAlive():
            if unit.getEnergy() > 0:
                if unit.getPosition() != corner:
                    unit.move(corner, )
                else:
                    shoot = True
                    target = (self.ms/2, self.ms/2)
                    bulletpath = unit.getBulletPath(target, )[:self.wt.getBulletRange()]
                    for vunit in self.getMyUnits():
                        if unit == vunit:
                            continue 
                        unit_square = self.unitsquares[vunit]
                        vunitpath = vunit.getUnitPath(unit_square, )
                        if self.pathsIntersect(bulletpath, vunitpath):
                            shoot = False
                            break
                    if shoot:
                        unit.shoot((self.ms/2, self.ms/2), )

    def _spin(self):
        print "Spinning my AI and my AI tells me that it is the %s iteration" % (self.wt.getCurrentTurn()) 
        print "I own these units: ", self.getMyUnits()
        # I am gonna tell my AI to randomly shoot in a direction or move to a random square.
        # Cool, right? 

        self.moveToCorner(self.unit1)
        self.moveToCorner(self.unit2)        
        self.moveToCorner(self.unit3)
        self.moveToCorner(self.unit4)
        #for unit in self.getMyUnits():
            #func = random.choice([unit.move, unit.shoot])
            #while True:
            #    try:
            #        square = (random.randint(0, self.wt.getMapSize()), \
            #                    random.randint(0, self.wt.getMapSize()))
            #        func(square, )
            #        break
            #    except world.IllegalSquareException:
            #        pass        
            
        #print "and I can see these squares: %s" % self.getVisibleSquares()
        print "and I can see these units: %s" % self.getVisibleUnits()
