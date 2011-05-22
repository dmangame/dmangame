import ai
import random
from collections import defaultdict
import itertools
AIClass = "ImmortalAI"


# Immortal AI from quiverer (on reddit)
# http://www.reddit.com/r/programming/comments/hdtta/dmangame_a_game_about_writing_game_ai_in_python/c1vb5kp
class ImmortalAI(ai.AI):
    def _spin(self):
        for unit in self.my_units:
            unit.move((30,30))

