import sys
sys.path.append(".")

import settings
import maps.default as map_settings
import ai_exceptions
import mapobject
import ai
import ai.testai
import random
import unittest
import world
import worldtalker
import copy
from collections import defaultdict


class SecurityWorld(world.World):
  def createUnit(self, stats, square):
    at = getattr(self, '_World__createUnit')
    return at(stats, square)

  def calcVisibility(self):
    at = getattr(self, '_World__calcVisibility')
    return at()

  def Stats(self, *args, **kwargs):
    s = copy.copy(self.unit_stats)
    for k in kwargs:
      setattr(s, k, kwargs[k])
    return s

class SecurityAI(ai.AI):
  # Tests that an AI can not manipulate units from another
  # AI's team

  def do_unit_property(self, unit, prop):
    return getattr(unit, prop)

  def do_unit_action(self, unit, action, *args):
    func = getattr(unit, action)
    return func(*args)

class TestSecurityFunctions(unittest.TestCase):
  def setUp(self):
    self.w  = SecurityWorld()
    self.wt = worldtalker.WorldTalker(self.w)
    self.own_ai = SecurityAI(self.wt)
    self.other_ai = SecurityAI(self.wt)

    top_left = (0,0)
    bottom_right = (self.w.mapSize-1, self.w.mapSize-1)

    self.top_left = top_left
    self.bottom_right = bottom_right

    s = self.w.Stats(ai_id=self.own_ai.ai_id,
                    team=self.own_ai.team)
    s.ai = self.own_ai
    self.own_unit = self.w.createUnit(s, top_left)

    s = self.w.Stats(ai_id=self.other_ai.ai_id, team=self.other_ai.team)
    s.ai = self.other_ai
    self.other_unit = self.w.createUnit(s, bottom_right)

    b = mapobject.Building(self.wt)
    self.w.buildings[b] = self.own_ai
    self.w.map.placeObject(b, top_left)
    self.own_b = b

    b = mapobject.Building(self.wt)
    self.w.buildings[b] = self.other_ai
    self.w.map.placeObject(b, bottom_right)

    self.other_b = b




  def do_test_property(self, prop, true_comp=None,
                                   false_comp=None):
    exc_class = None
    # Verify own AI can move unit
    ret = self.own_ai.do_unit_property(self.own_unit, prop)
    nret = None
#    print "t", prop, ret
    if true_comp is not None:
      self.assertTrue(true_comp(ret))
    else:
      self.assertTrue(ret)

    # Verify other AI can not
    try:
      nret = self.other_ai.do_unit_property(self.own_unit, prop)
    except ai_exceptions.InvisibleUnitException, e:
      exc_class = e.__class__

      self.assertEqual(exc_class,
                       ai_exceptions.InvisibleUnitException)
    except ai_exceptions.InvalidOwnerException, e:
      exc_class = e.__class__

      self.assertEqual(exc_class,
                       ai_exceptions.InvalidOwnerException)

#    print "f", prop, nret
    if not exc_class:

      if false_comp is not None:
        self.assertTrue(false_comp(nret))
      else:
        self.assertFalse(nret)


  def do_test_action(self, action, true_comp=None, false_comp=None, args=[]):
    exc_class = None
    # Verify own AI can move unit
    ret = self.own_ai.do_unit_action(self.own_unit, action, *args)
    nret = None
    if true_comp is not None:
      self.assertTrue(true_comp(ret))
    else:
      self.assertTrue(ret)

    # Verify other AI can not
    try:
      nret = self.other_ai.do_unit_action(self.own_unit, action, *args)
    except ai_exceptions.InvisibleUnitException, e:
      exc_class = e.__class__

      self.assertEqual(exc_class,
                       ai_exceptions.InvisibleUnitException)
    except ai_exceptions.InvalidOwnerException, e:
      exc_class = e.__class__

      self.assertEqual(exc_class,
                       ai_exceptions.InvalidOwnerException)

    if not exc_class:
      # If it didn't throw an error, verify it returned an empty set
#      print "f", action, nret
      if false_comp is not None:
        self.assertTrue(false_comp(nret))
      else:
        self.assertFalse(nret)

  # mapobject.Unit Security tests
  # Function tests
  def test_move(self):
    self.do_test_action("move", args=[(5,5)])

  def test_shoot(self):
    self.do_test_action("shoot", args=[(5,5)])

  def test_capture(self):
      self.do_test_action("capture", args=[self.own_b])

  def test_bullet_path(self):
      self.do_test_action("calcBulletPath", args=[(10,10)])

  def test_unit_path(self):
      self.do_test_action("calcUnitPath", args=[(10,10)])

  def test_distance(self):
      self.w.map.placeObject(self.other_unit, self.bottom_right)
      self.w.map.placeObject(self.own_unit, self.top_left)
      self.do_test_action("calcDistance", args=[(10,10)], false_comp=lambda x: x != False)

  def test_victims(self):
      self.w.map.placeObject(self.own_unit, (7,7))
      self.w.map.placeObject(self.other_unit, (10,10))
      self.w.calcVisibility()
      self.do_test_action("calcVictims", args=[(10,10)])

  # Property Tests
  def test_position(self):
      self.do_test_property("position")

  def test_is_alive(self):
      self.do_test_property("is_alive")

  def test_is_capturing(self):
      self.w.map.placeObject(self.other_b, self.top_left)
      self.w.map.placeObject(self.other_unit, self.bottom_right)

      self.own_ai.do_unit_action(self.own_unit, "capture", self.own_b)
      self.w.spawn_counters = defaultdict(lambda: 100)
      self.w.Turn()
      self.do_test_property("is_capturing")

  def test_visible_buildings(self):
      def true_comp(x):
        return len(x) > 0

      def false_comp(x):
        return len(x) == 0

      self.w.calcVisibility()
      self.do_test_property("visible_buildings", true_comp, false_comp)

  def test_visible_enemies(self):
      self.w.map.placeObject(self.own_unit, self.top_left)
      self.w.map.placeObject(self.other_unit, self.top_left)
      self.w.calcVisibility()
      def true_comp(x):
        return len(x) > 0

      def false_comp(x):
        return len(x) == 0
      self.do_test_property("visible_enemies", true_comp, false_comp)

  def test_visible_squares(self):
      def true_comp(x):
        return len(x) > 0

      def false_comp(x):
        return len(x) != 0

      self.do_test_property("visible_squares", true_comp, false_comp)


if __name__ == "__main__":
  unittest.main()
