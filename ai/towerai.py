import ai
import random
AIClass="TowerAI"
class TowerAI(ai.AI):
  def _init(self):
    self.moved_once = set()

  def _spin(self):
    for unit in self.my_units:
      if unit.visible_enemies:
        unit.shoot(unit.visible_enemies[0].position)
      else:
        if not unit in self.moved_once:
          unit.move((random.randint(0, self.mapsize),
                     random.randint(0, self.mapsize)))
          self.moved_once.add(unit)

