# Map test functionality. Tests accuracy of paths and moves
# generated, etc.
import sys
sys.path.insert(0, ".")

import map as wm
import unittest


class TestSecurityFunctions(unittest.TestCase):
  def setUp(self):
    self.map = wm.Map(100)

  def test_get_legal_moves(self):
    one_sq_moves = set([(49, 50), (51, 50), (50, 51), (50, 49), (50, 50)])

    self.assertEqual(self.map.getLegalMoves((50, 50), 1), 
                     one_sq_moves)

    print one_sq_moves

if __name__ == "__main__":
  unittest.main()
