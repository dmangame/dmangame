import sys
sys.path.append(".")

import ai_exceptions
import mapobject
import ai
import ai.testai
import random
import unittest
import world
import worldtalker


class SecurityAI(ai.AI):
  # Tests that an AI can not manipulate units from another
  # AI's team

  def do_unit(self, unit, action, *args):
    args = map(str, args)
    command = "unit.%s(%s)" % (action, ",".join(args))
    print command
    exec command

class TestSecurityFunctions(unittest.TestCase):
  def setUp(self):
    self.w  = world.World(10)
    self.wt = worldtalker.WorldTalker(self.w)
    self.own_ai = SecurityAI(self.wt)
    self.other_ai = SecurityAI(self.wt)

    s = world.Stats(ai_id=self.own_ai.ai_id)
    s.ai = self.own_ai
    self.own_unit = mapobject.Unit(self.wt, s)
    self.w.units[self.own_unit] = s
    self.w.alive[self.own_unit] = True

  def test_move(self):
    exc_class = None
    # Verify own AI can move unit
    self.own_ai.do_unit(self.own_unit, "move", (5,5))

    # Verify other AI can not
    try:
      self.other_ai.do_unit(self.own_unit, "move", (5,5))
    except Exception, e:
      exc_class = e.__class__

    self.assertEqual(exc_class,
                     ai_exceptions.InvalidOwnerException)

if __name__ == "__main__":
  unittest.main()
