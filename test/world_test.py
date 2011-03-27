import sys
sys.path.append(".")

import settings
import ai_exceptions
import mapobject
import ai
import ai.testai
import random
import unittest
import world
import worldtalker



class SecurityWorld(world.World):
  def createUnit(self, stats, square):
    at = getattr(self, '_World__createUnit')
    return at(stats, square)

  def killUnit(self, unit):
    at = getattr(self, '_World__unitCleanup')
    return at(unit)

class SecurityAI(ai.AI):
  # Tests that an AI can not manipulate units from anown
  # AI's team

  def do_unit_property(self, unit, prop):
    return getattr(unit, prop)

  def do_unit_action(self, unit, action, *args):
    func = getattr(unit, action)
    return func(*args)

class TestWorldFunctions(unittest.TestCase):
  def setUp(self):
    self.w = SecurityWorld()
    self.wt = worldtalker.WorldTalker(self.w)
    self.ai = SecurityAI(self.wt)

    top_left = (0,0)
    bottom_right = (self.w.mapSize-1, self.w.mapSize-1)

    self.top_left = top_left
    self.bottom_right = bottom_right

    s = world.Stats(ai_id=self.ai.ai_id,
                    team=self.ai.team)
    s.ai = self.ai
    self.unit = self.w.createUnit(s, top_left)


    b = mapobject.Building(self.wt)
    self.w.buildings[b] = self.ai
    self.b = b

    b = mapobject.Building(self.wt)




  def test_melee(self):
    # Test the melee event
    pass

  def test_shoot(self):
    # Test the shoot event
    pass

  def test_move(self):
    # Test the move event
    self.w.map.placeObject(self.unit, self.bottom_right)
    self.w.currentTurn = settings.UNIT_SPAWN_MOD+1
    self.w.createMoveEvent(self.unit, self.top_left)
    self.assertEqual(self.w.map.getPosition(self.unit), self.bottom_right)
    while True:
      this_position = self.w.map.getPosition(self.unit)
      self.w.Turn()
      next_position = self.w.map.getPosition(self.unit)
      if next_position == self.top_left:
        break

      self.assertNotEqual(self.w.map.getPosition(self.unit), self.bottom_right)


  def test_capture_simple(self):
      self.w.map.placeObject(self.b, self.bottom_right)
      self.w.map.placeObject(self.unit, self.bottom_right)
      self.w.buildings[self.b] = None

      self.w.currentTurn = settings.UNIT_SPAWN_MOD+1
      self.w.createCaptureEvent(self.unit, self.b)
      self.assertNotEqual(self.w.buildings[self.b], self.ai)
      for i in xrange(settings.CAPTURE_LENGTH):
        self.w.Turn()

      self.assertEqual(self.w.buildings[self.b], self.ai)

  def test_capture_ended_by_death(self):
    self.w.map.placeObject(self.b, self.bottom_right)
    self.w.map.placeObject(self.unit, self.bottom_right)
    self.w.buildings[self.b] = None

    self.w.currentTurn = settings.UNIT_SPAWN_MOD+1
    self.w.createCaptureEvent(self.unit, self.b)
    self.assertNotEqual(self.w.buildings[self.b], self.ai)
    for i in xrange(settings.CAPTURE_LENGTH-1):
      self.w.Turn()

    self.w.killUnit(self.unit)
    self.w.Turn()

    self.assertNotEqual(self.w.buildings[self.b], self.ai)

  
if __name__ == "__main__":
  unittest.main()

