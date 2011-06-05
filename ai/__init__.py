import base

BareAI = base.BareAI
AI = base.AI
AI_COLORS = {}

import random


def random_ai_color():
  r = random.randint(1, 5)
  g = random.randint(1, 5)
  b = random.randint(1, 5)
  return map(lambda x: x/5.0, [r,g,b])

PREDEFINED_COLORS = []

def hex2float(h):
  r = int(h[0:2], 16)
  g = int(h[2:4], 16)
  b = int(h[4:6], 16)
  return (r / 256.0, g / 256.0, b / 256.0)

def clear_ai_colors():
  global PREDEFINED_COLORS

  # These should be better defined
  PREDEFINED_COLORS = random.choice([[
                       hex2float("202020"),
                       hex2float("221b00"),
                       hex2float("2fda00"),
                       hex2float("e80c7a"),
                       hex2float("3d0dff"),

                       hex2float("f26716"),
                      ],
                      
                      [
                      hex2float("ffff00"),
                      hex2float("202020"),
                      hex2float("a60311"),
                      hex2float("1abc16"),
                      hex2float("023a8b"),
                      hex2float("f26716"),
                      ]])


  random.shuffle(PREDEFINED_COLORS)

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
