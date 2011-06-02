import math
import random
import logging
import copy

logging.basicConfig(level=logging.INFO)

log = logging.getLogger("TOURNAMENT")

def combinations(iterable, r):
    # combinations('ABCD', 2) --> AB AC AD BC BD CD
    # combinations(range(4), 3) --> 012 013 023 123
    pool = tuple(iterable)
    n = len(pool)
    if r > n:
        return
    indices = range(r)
    yield tuple(pool[i] for i in indices)
    while True:
        for i in reversed(range(r)):
            if indices[i] != i + n - r:
                break
        else:
            return
        indices[i] += 1
        for j in range(i+1, r):
            indices[j] = indices[j-1] + 1
        yield tuple(pool[i] for i in indices)
# League Matchup
# Number of rounds, make sure everyone plays someone they
# haven't played before.
def league_games(contestants, max_games=50, num_players=2):
  games = []
  tries = 0
  if len(contestants) <= 1:
    return []

  games = list(combinations(contestants, num_players))

  if not games:
    raise Exception("Not enough players for the tournament")

  while len(games) < max_games:
    games += games

  return games[:max_games]

if __name__ == "__main__":
  print league_games(range(0, 10))
