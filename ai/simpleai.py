
import ai
AIClass="SimpleAI"
import logging
log = logging.getLogger(AIClass)

class SimpleAI(ai.AI):
    def _init(self):
      log.info("Initializing: Current Turn: %s", self.current_turn)

    def _spin(self):
      log.info("My visible units:%s", self.my_units)
      log.info("My visible enemies:%s", self.visible_enemies)

    def _unit_died(self, unit):
      log.info("%s died", unit)

    def _unit_spawned(self, unit):
      log.info("Received a new unit: %s", unit)
