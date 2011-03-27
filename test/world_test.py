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
  # Tests that an AI can not manipulate units from another
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
    self.own_ai = SecurityAI(self.wt)
    self.other_ai = SecurityAI(self.wt)

    top_left = (0,0)
    bottom_right = (self.w.mapSize-1, self.w.mapSize-1)

    self.top_left = top_left
    self.bottom_right = bottom_right

    s = world.Stats(ai_id=self.own_ai.ai_id,
                    team=self.own_ai.team)
    s.ai = self.own_ai
    self.own_unit = self.w.createUnit(s, top_left)

    s = world.Stats(ai_id=self.other_ai.ai_id, team=self.other_ai.team)
    s.ai = self.other_ai
    self.other_unit = self.w.createUnit(s, bottom_right)

    b = mapobject.Building(self.wt)
    self.w.buildings[b] = self.own_ai
    self.own_b = b

    b = mapobject.Building(self.wt)
    self.w.buildings[b] = self.other_ai

    self.other_b = b

  def test_simple_capture(self):
      self.w.map.placeObject(self.other_b, self.bottom_right)
      self.w.map.placeObject(self.other_unit, self.bottom_right)
      self.w.buildings[self.other_b] = None

      self.w.currentTurn = settings.UNIT_SPAWN_MOD+1
      self.w.createCaptureEvent(self.other_unit, self.other_b)
      self.assertNotEqual(self.w.buildings[self.other_b], self.other_ai)
      for i in xrange(settings.CAPTURE_LENGTH):
        self.w.Turn()

      self.assertEqual(self.w.buildings[self.other_b], self.other_ai)

  def test_capture_ended_by_death(self):
    self.w.map.placeObject(self.other_b, self.bottom_right)
    self.w.map.placeObject(self.other_unit, self.bottom_right)
    self.w.buildings[self.other_b] = None

    self.w.currentTurn = settings.UNIT_SPAWN_MOD+1
    self.w.createCaptureEvent(self.other_unit, self.other_b)
    self.assertNotEqual(self.w.buildings[self.other_b], self.other_ai)
    for i in xrange(settings.CAPTURE_LENGTH-1):
      self.w.Turn()

    self.w.killUnit(self.other_unit)
    self.w.Turn()

    self.assertNotEqual(self.w.buildings[self.other_b], self.other_ai)

if __name__ == "__main__":
  unittest.main()

