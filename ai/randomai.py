import ai
import random
import world
AIClass = "RandomAI"

class RandomAI(ai.AI):
    def __init__(self, *args, **kwargs):
        ai.AI.__init__(self, *args, **kwargs)

    def _init(self):
        pass

    def _spin(self):
        # I am gonna tell my AI to randomly shoot in a direction or move to a random square.
        # Cool, right?
        for unit in self.my_units:
            func = random.choice([unit.move, unit.shoot])
            while True:
                try:
                    square = (random.randint(0, self.wt.getMapSize()), \
                                random.randint(0, self.wt.getMapSize()))
                    func(square)
                    break
                except world.IllegalSquareException:
                    pass
