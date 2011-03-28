import base

AI = base.AI
AI_COLORS = {}

import random
def random_ai_color():
  r = random.randint(1, 5)
  g = random.randint(1, 5)
  b = random.randint(1, 5)
  return map(lambda x: x/5.0, [r,g,b])

def generate_ai_color(ai_player):
  if not ai_player.team in AI_COLORS:
      try:
        color = ai_player.__class__.color
      except:
        color = random_ai_color()
        while color in AI_COLORS.values():
            color = random_ai_color()
      AI_COLORS[ai_player.team] = color
