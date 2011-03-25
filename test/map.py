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

    two_sq_moves = set([(49, 50), (51, 50), (49, 51), (51, 51), (51, 49), (50, 49), (49, 49), (50, 48), (50, 52), (50, 51), (50, 50), (52, 50), (48, 50)])


    self.assertEqual(self.map.getLegalMoves((50, 50), 2), 
                     two_sq_moves)

    three_sq_moves = set([(49, 51), (51, 51), (50, 49), (50, 53), (52, 49), (48, 51), (49, 50), (51, 50), (51, 52), (50, 50), (52, 50), (49, 49), (50, 47), (51, 49), (49, 52), (50, 51), (52, 51), (49, 48), (53, 50), (48, 49), (51, 48), (48, 50), (50, 48), (47, 50), (50, 52)])
    self.assertEqual(self.map.getLegalMoves((50, 50), 3), 
                     three_sq_moves)

if __name__ == "__main__":
  unittest.main()
