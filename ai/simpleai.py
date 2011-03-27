
import ai
AIClass="SimpleAI"
class SimpleAI(ai.AI):
    def _init(self):
      print self.currentTurn

    def _spin(self):
      print self.my_units
      print self.visible_enemies

    def _unit_spawned(self, unit):
      print "Received a new unit: %s" % unit
