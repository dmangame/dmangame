import base

BareAI = base.BareAI
AI = base.AI
AI_COLORS = {}

import random

PREDEFINED_COLORS = [(0.0, 0.0, 1.0),
                     (0.0, 1.0, 0.0),
                     (1.0, 0.0, 0.0),
                     (0.0, 1.0, 1.0),
                     (1.0, 1.0, 0.0),
                     (1.0, 0.0, 1.0)]


def random_ai_color():
  r = random.randint(1, 5)
  g = random.randint(1, 5)
  b = random.randint(1, 5)
  return map(lambda x: x/6.0, [r,g,b])

def generate_ai_color(ai_player):
  global PREDEFINED_COLORS

  if not ai_player.team in AI_COLORS:
      try:
        if PREDEFINED_COLORS:
          color = PREDEFINED_COLORS[0]
          PREDEFINED_COLORS = PREDEFINED_COLORS[1:]
          AI_COLORS[ai_player.team] = color
          return

        color = ai_player.__class__.color
      except:
        color = random_ai_color()
        while color in AI_COLORS.values():
            color = random_ai_color()
      AI_COLORS[ai_player.team] = color
