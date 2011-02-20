
import trueskill


class Player(object):
    pass



def run(games, ratings, use_default_rating=False):
    """Update ratings based on games, and return new ratings

    GAMES is a list of dict objects, containing the following keys:

    players: a list of player identifiers
    rank:  a list of places in the game

    RATINGS is a dictionary of player identifiers matched with their
    (mu, sigma) rating.  RATINGS is modified in this function.

    If USE_DEFAULT_RATING is False, an error is thrown if a player
    in games is not in RATINGS.  Otherwise, the default mu and sigma
    are used.
    """

    for game in games:
        players = []
        for k in xrange(len(game['players'])):
            p = Player()
            p.id = game['players'][k]
            p.rank = game['rank'][k]

            if ratings.has_key(p.id):
                p.skill = ratings[p.id]
            elif use_default_rating:
                p.skill = (trueskill.INITIAL_MU, trueskill.INITIAL_SIGMA)
            else:
                raise Exception("Rating missing for: %s" % p.id)
            players.append(p)
        trueskill.AdjustPlayers(players)
        for p in players:
            ratings[p.id] = p.skill

if __name__ == "__main__":
    # examples
    def example_1():
        games = [ { 'game_id': 0,
                    'map': 'random4',
                    'players': ['a', 'b', 'c', 'd'],
                    'rank': [2,1,3,0],
                    'score': [103, 153, 91, 167] } ]

        ratings = {}
        run(games, ratings, True)
        for k in ratings.keys():
            print k, ratings[k]


    example_1()



    def example_2():
        games = [ { 'players': ['a', 'b', 'c', 'd'],
                    'rank': [2,1,3,0]},
                  { 'players': ['a', 'b', 'c', 'd'],
                    'rank': [2,1,3,0]},
                  { 'players': ['a', 'b', 'c', 'd'],
                    'rank': [2,1,3,0]},]
                  

        ratings = {'a': (25, 8), 'b': (23, 5), 'c': (28,5),
                    'd': (24, 6)}
        run(games, ratings, False)
        print ratings
#    example_2()

    
