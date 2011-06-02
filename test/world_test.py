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

from collections import defaultdict



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

    self.w.teams = defaultdict(lambda: "<<UNDEFINED>>")
    self.w.team_map = defaultdict(lambda: "<<UNDEFINED>>")
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




  # Test that melee kills a unit on the same square
  def test_melee(self):
    other_ai = SecurityAI(self.wt)
    s = world.Stats(ai_id=other_ai.ai_id,
                    team=other_ai.team)
    s.ai = other_ai
    other_unit = self.w.createUnit(s, self.top_left)
    self.assertEqual(other_unit in self.w.units, True)
    self.w.map.placeObject(self.unit, self.top_left)
    self.w.currentTurn = settings.UNIT_SPAWN_MOD+1
    self.w.createShootEvent(self.unit, self.top_left, 1)
    self.w.Turn()
    self.assertEqual(other_unit in self.w.units, False)

  # Test that melee doesn't kill allies on the same square
  def test_melee_no_friendly_fire(self):
    s = world.Stats(ai_id=self.ai.ai_id,
                    team=self.ai.team)
    friendly_unit = self.w.createUnit(s, self.top_left)
    self.assertEqual(friendly_unit in self.w.units, True)
    self.w.map.placeObject(self.unit, self.top_left)
    self.w.currentTurn = settings.UNIT_SPAWN_MOD+1
    self.w.createShootEvent(self.unit, self.top_left, 1)
    self.w.Turn()
    self.assertEqual(friendly_unit in self.w.units, True)

  def test_melee_kill_all_enemies(self):
    enemies = []
    self.w.map.placeObject(self.unit, self.top_left)

    for x in xrange(5):
      other_ai = SecurityAI(self.wt)
      s = world.Stats(ai_id=other_ai.ai_id,
                      team=other_ai.team)
      s.ai = other_ai
      other_unit = self.w.createUnit(s, self.top_left)
      enemies.append(other_unit)

    for other_unit in enemies:
      self.assertEqual(other_unit in self.w.units, True)

    self.w.currentTurn = settings.UNIT_SPAWN_MOD+1
    self.w.createShootEvent(self.unit, self.top_left, 1)
    self.w.Turn()
    for other_unit in enemies:
      self.assertEqual(other_unit in self.w.units, False)



  def test_shoot_deals_damage(self):
    self.w.map.placeObject(self.unit, self.top_left)
    other_ai = SecurityAI(self.wt)
    s = world.Stats(ai_id=other_ai.ai_id,
                    team=other_ai.team)
    s.ai = other_ai
    other_unit = self.w.createUnit(s, (5,5))
    self.ai.do_unit_action(self.unit, "shoot", (5,5))
    energy = self.w.units[other_unit].energy

    self.w.Turn()
    self.assertNotEqual(energy,
      self.w.units[other_unit].energy)

  def test_shoot_hits_enemy_just_in_range(self):
    self.w.map.placeObject(self.unit, self.top_left)
    other_ai = SecurityAI(self.wt)
    s = world.Stats(ai_id=other_ai.ai_id,
                    team=other_ai.team)
    s.ai = other_ai

    for i in xrange(self.w.bulletRange):
      dy = self.w.bulletRange - i
      dx = self.w.bulletRange - dy
      pos = dx, dy
      other_unit = self.w.createUnit(s, pos)
      self.ai.do_unit_action(self.unit, "shoot", pos)
      energy = self.w.units[other_unit].energy

      self.w.Turn()
      self.w.Turn()
      self.w.Turn()
      self.w.Turn()
      self.assertNotEqual(energy,
        self.w.units[other_unit].energy)

    for i in xrange(self.w.bulletRange):
      dx = self.w.bulletRange - i
      dy = self.w.bulletRange - dx
      pos = dx, dy
      other_unit = self.w.createUnit(s, pos)
      self.ai.do_unit_action(self.unit, "shoot", pos)
      energy = self.w.units[other_unit].energy

      self.w.Turn()
      self.w.Turn()
      self.w.Turn()
      self.w.Turn()
      self.assertNotEqual(energy,
        self.w.units[other_unit].energy)

  def test_shoot_does_not_hit_distant_enemy(self):
    self.w.map.placeObject(self.unit, self.top_left)
    other_ai = SecurityAI(self.wt)
    s = world.Stats(ai_id=other_ai.ai_id,
                    team=other_ai.team)
    s.ai = other_ai
    other_unit = self.w.createUnit(s, self.bottom_right)
    self.ai.do_unit_action(self.unit, "shoot", self.bottom_right)
    energy = self.w.units[other_unit].energy

    self.w.Turn()
    self.assertEqual(energy,
      self.w.units[other_unit].energy)

  def test_shoot_can_kill_enemy(self):
    self.w.map.placeObject(self.unit, self.top_left)
    other_ai = SecurityAI(self.wt)
    s = world.Stats(ai_id=other_ai.ai_id,
                    team=other_ai.team)
    s.ai = other_ai
    other_unit = self.w.createUnit(s, (5,5))

    while other_unit in self.w.units:
      energy = self.w.units[other_unit].energy
      self.ai.do_unit_action(self.unit, "shoot", (5,5))
      self.w.Turn()
      if not other_unit in self.w.units:
        break

      self.assertNotEqual(energy,
        self.w.units[other_unit].energy)



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

  def test_capture_twice(self):
    self.w.map.placeObject(self.b, self.bottom_right)
    self.w.map.placeObject(self.unit, self.bottom_right)
    self.w.buildings[self.b] = None

    self.w.createCaptureEvent(self.unit, self.b)
    self.w.Turn()
    self.w.currentTurn = settings.UNIT_SPAWN_MOD+1
    self.w.createCaptureEvent(self.unit, self.b)
    self.assertNotEqual(self.w.buildings[self.b], self.ai)

    for i in xrange(settings.CAPTURE_LENGTH-1):
      self.assertNotEqual(self.w.buildings[self.b], self.ai)
      self.w.Turn()

    self.assertEqual(self.w.buildings[self.b], self.ai)


if __name__ == "__main__":
  unittest.main()

