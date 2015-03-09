from __future__ import with_statement

import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'
from google.appengine.dist import use_library
use_library('django', '1.2')
from google.appengine.ext.webapp import template

from google.appengine.ext import blobstore
from google.appengine.ext import db
from google.appengine.ext import deferred
from google.appengine.api import files
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp import blobstore_handlers
from google.appengine.ext.webapp.util import run_wsgi_app


import urllib
import hashlib
import sys
import time
import datetime
import random
import traceback

import ai as ai_module
import code_signature
import world
from lib import jsplayer
from lib.trueskill import trueskill

from collections import defaultdict

import settings
import main as dmangame

import logging
log = logging.getLogger("APPENGINE")
log.setLevel(logging.INFO)

template.register_template_library('appengine.extensions')

TEMPLATE_DIR=os.path.join(os.path.dirname(__file__), 'templates')

class Tournament(db.Model):
    created_at    = db.DateTimeProperty(auto_now_add=True)
    participants  = db.IntegerProperty()

class GameRun(db.Model):
    created_at    = db.DateTimeProperty(auto_now_add=True)
    map_name      = db.StringProperty()
    run_time      = db.FloatProperty()
    replay        = blobstore.BlobReferenceProperty()
    updated_at    = db.DateTimeProperty(auto_now=True)
    turns         = db.IntegerProperty()
    version       = db.StringProperty()
    tournament    = db.ReferenceProperty(Tournament)

# Represents an AI playing in the app engine ladder matches.
# The ladder player is added via a post to app engine and can
# be removed via a post to app engine.

# In order for the player to be added to app engine, though,
# the AI must contain the line INCLUDE_IN_LADDER=True
class AILadderPlayer(db.Model):
  created_at = db.DateTimeProperty(auto_now_add=True)
  updated_at = db.DateTimeProperty(auto_now=True)
  class_name = db.StringProperty(required=True)
  file_name  = db.StringProperty(required=True)
  enabled    = db.BooleanProperty(default=False)
  last_match = db.DateTimeProperty()
  matches    = db.IntegerProperty(default=0)
  # Records how many times it makes an uh oh
  faults     = db.IntegerProperty(default=0)

  # mu / sigma terms for trueskill
  skill     = db.FloatProperty(default=25.0)
  uncertainty = db.FloatProperty(default=25/3.0)

class AIMapPlayer(AILadderPlayer):
  map = db.StringProperty(required=True)

# This is the AI representing a player in a game
class AIParticipant(db.Model):
    created_at = db.DateTimeProperty(auto_now_add=True)
    updated_at = db.DateTimeProperty(auto_now=True)
    class_name = db.StringProperty(required=True)
    file_name  = db.StringProperty(required=True)
    game_run   = db.ReferenceProperty(GameRun)
    player     = db.ReferenceProperty(AILadderPlayer, default=None)
    version    = db.StringProperty(required=True)
    win        = db.BooleanProperty(required=True)

    # Can keep score information here for queries, I guess.
    deaths     = db.IntegerProperty()
    kills      = db.IntegerProperty()
    units      = db.IntegerProperty()
    buildings  = db.IntegerProperty()


PAGESIZE=100

def aggregate_games(tournament=None):
  q = GameRun.all().order("-created_at")
  ais = set()
  total_games = 0
  ai_classes = {}
  if tournament:
    q.filter("tournament =", tournament)

  scores = defaultdict(float)
  games = defaultdict(lambda: defaultdict(int))
  win_ratios = defaultdict(lambda: defaultdict(int))
  wins = defaultdict(lambda: defaultdict(int))
  losses = defaultdict(lambda: defaultdict(int))
  draws = defaultdict(lambda: defaultdict(int))
  offset = 0

  all_ais = set()

  while True:
    runs = q.fetch(PAGESIZE+1, offset)
    offset += PAGESIZE

    for game in runs:
      ais = list(game.aiparticipant_set)
      total_games += 1
      game_won = False
      winner = None
      for ai in ais:
        if not ai.file_name in all_ais:
          all_ais.add(ai.file_name)
          ai_classes[ai.file_name] = ai.class_name

      for ai in ais:
        for other_ai in ais:
          if ai != other_ai:
            games[ai.file_name][other_ai.file_name] += 1
        if ai.win:
          winner = ai
          game_won = True

      if not game_won:
        for ai in ais:
          scores[ai.file_name] += 1.0 / float(len(ais))
          for other_ai in ais:
            draws[ai.file_name][other_ai.file_name] += 1
            draws[other_ai.file_name][ai.file_name] += 1

      else:
        for ai in ais:
          if not ai == winner:
            losses[ai.file_name][winner.file_name] += 1
            wins[winner.file_name][ai.file_name] += 1

    if len(runs) <= PAGESIZE:
      # No more results
      break


  ai_scores = []
  for ai in all_ais:
    for other_ai in all_ais:
      if games[ai][other_ai] > 0:
        win_ratios[ai][other_ai] = float(wins[ai][other_ai]) / games[ai][other_ai] * 100
    ai_data = { "score"  : scores[ai],
                "wins"   : wins[ai],
                "losses" : losses[ai],
                "draws"  : draws[ai],
                "games"  : games[ai],
                "ratios" : win_ratios[ai],
                "file_name" : ai,
                "class_name" : ai_classes[ai]}

    ai_scores.append(ai_data)
  return ai_scores, len(all_ais), total_games

class AIStatsPage(webapp.RequestHandler):
    def get(self):
      file_name = self.request.get("file_name")
      tournament_key = self.request.get("tournament")
      tournament = None
      if tournament_key:
        tournament = Tournament.get(tournament_key)

      ai_scores, num_ais, total_games = aggregate_games(tournament=tournament)

      template_values = { "ai_scores" : ai_scores, "total_games" : total_games, "count_ai" : num_ais }

      path = os.path.join(TEMPLATE_DIR, "stats.html")
      self.response.headers['Content-Type'] = 'text/html'
      self.response.out.write(template.render(path, template_values))

class DisqusPage(webapp.RequestHandler):
  def get(self, resource):
    resource = str(urllib.unquote(resource))
    self.response.headers['Content-Type'] = 'text/html'
    template_values = { "blob_key" : resource }

    path = os.path.join(TEMPLATE_DIR, "disqus.html")
    self.response.headers['Content-Type'] = 'text/html'
    self.response.out.write(template.render(path, template_values))

class LadderPage(webapp.RequestHandler):
  def get(self):

    ladders = {}

    map_players = AIMapPlayer.all().order("-skill").fetch(PAGESIZE)
    for ladder_player in map_players:
      player_map = ladder_player.map
      if not player_map in ladders:
        ladders[player_map] = []
      ladders[player_map].append(ladder_player)

    template_values = {"ladders" : sorted(ladders.items()),
                       "overall" : AILadderPlayer.all().order("-skill").fetch(PAGESIZE) }

    path = os.path.join(TEMPLATE_DIR, "ladder.html")

    self.response.headers['Content-Type'] = 'text/html'
    self.response.out.write(template.render(path, template_values))

class ReplayPage(webapp.RequestHandler):
    def get(self, resource):
        resource = str(urllib.unquote(resource))
        blob_info = blobstore.BlobInfo.get(resource)
        blob_reader = blob_info.open()
        blob_data = blob_reader.read()
        self.response.headers['Content-Type'] = 'text/html'
        self.response.out.write(blob_data)

class AdminPage(webapp.RequestHandler):
    def get(self):
      self.redirect(users.create_login_url(self.request.uri))


class MainPage(webapp.RequestHandler):
    def get(self):
        before = self.request.get("before")

        query = GameRun.all().order("-created_at")
        if before:
          query = query.filter("created_at < ", datetime.datetime.fromtimestamp(float(before)))

        games = query.fetch(PAGESIZE+1)
        log.info(map(lambda x: x.key().id(), games))


        file_set = set()
        map_set = set()
        for game in games:
          ais = game.aiparticipant_set
          for ai in ais:
            file_set.add(ai.file_name)
          map_set.add(game.map_name)

          try:
            t = game.tournament
          except:
            game.tournament = None


        has_next_page = False
        if len(games) == PAGESIZE + 1:
          has_next_page = games[-1].created_at
          games = games[:PAGESIZE]

        game_maps = sorted(list(map_set))
        game_ais = sorted(list(file_set))
        ladder_players = AILadderPlayer.all().order("-skill").fetch(PAGESIZE)

        template_values = { "game_runs" : games,
                            "next_page" : has_next_page,
                            "maps"      : game_maps,
                            "ai_files"  : game_ais,
                            "ladder_players" : ladder_players,
                            "can_delete" : users.is_current_user_admin()}

        path = os.path.join(TEMPLATE_DIR, "game_runs.html")
        self.response.headers['Content-Type'] = 'text/html'
        self.response.out.write(template.render(path, template_values))


def delete_game(game_id):
    gr = GameRun.get(game_id)
    log.info(gr)
    if gr:
      for ai in gr.aiparticipant_set:
        ai.delete()
      blobstore.delete([gr.replay.key])
      gr.delete()



class DeleteHandler(webapp.RequestHandler):
    def post(self):
        log.info("Delete Handler into")
        user = users.get_current_user()
        if not user:
            self.redirect(users.create_login_url(self.request.uri))
            return

        log.info(user)
        if users.is_current_user_admin():
            game = self.request.get("game_run")
            delete_game(game)

class DeleteOldHandler(webapp.RequestHandler):
    def post(self):
        query = GameRun.all().order("created_at")
        games = query.fetch(PAGESIZE+1)

        for game in games:
            now = datetime.datetime.now()
            log.info(now)
            delta = now - game.created_at
            if (delta > datetime.timedelta(days=365)):
                delete_game(game.key())


HOW_TO_PARTICIPATE = """
Almost there! %s is loadable by the server, but it is not setup to participate in ladder matches just yet.

In order to register %s in ladder matches:

* add "PLAY_IN_LADDER=True" to your AI Class as a class variable
* commit your AI
* push your repository to github
* re-run this command
"""

FIRST_REGISTER_MSG = "%s passed basic sanity check. Successfully added %s as ladder player"
REREGISTER_MSG = """
Congratulations, %s is registered as a ladder player.

skill: %.2f, uncertainty: %.2f"""

UNREGISTERED_AI = """
%s is no longer a competitor in ladder matches on this server.

To add %s as a competitor in ladder matches:

* add "PLAY_IN_LADDER=True" to the AI Class as a class variable
* commit your AI
* push your repository to github
* re-run this command
"""

# Adds an AI from github to the ladder handler. It first fetches the AI to do a
# basic sanity check
class RegisterAIHandler(webapp.RequestHandler):
  def post(self):
    # Just need to get the github file name and run the sanity check for the
    # module
    argv_str = urllib.unquote(self.request.get("argv"))
    options,args = dmangame.parseOptions(argv_str.split())
    response_str = ""

    for ai_str in args:
      response_str += "\n\n***Updating %s\n" % ai_str

      # Find the AI Ladder Player for this ai string or create
      # one if it doesn't exist.
      ladder_player = AILadderPlayer.get_by_key_name(ai_str)
      try:
        ai_modules = dmangame.loadAIModules([ai_str])
        ai_module = ai_modules.pop()
      except Exception, e:
        response_str += 'There was an issue loading the AI at %s.\n\n %s.' % (ai_str, traceback.format_exc())
        continue

      play_in_ladder = False
      try:
        if ai_module.PLAY_IN_LADDER:
          play_in_ladder = bool(ai_module.PLAY_IN_LADDER)
      except AttributeError:
        pass

      if ladder_player:
        if play_in_ladder:
          ladder_player.enabled = True
          ladder_player.put()
          response_str += REREGISTER_MSG % (ai_str, ladder_player.skill, ladder_player.uncertainty)
        else:
          ladder_player.enabled = False
          ladder_player.put()

          response_str += UNREGISTERED_AI % (ai_str, ai_str)
      else:
        if play_in_ladder:

          ladder_player = AILadderPlayer(class_name=ai_module.__name__,
                                         file_name=ai_str,
                                         enabled=True,
                                         key_name=ai_str)
          ladder_player.put()

          response_str += FIRST_REGISTER_MSG % (ai_str, ai_str)

        else:
          response_str += HOW_TO_PARTICIPATE % (ai_str, ai_str)

    self.response.headers['Content-Type'] = 'text/plain'
    self.response.out.write(response_str)

class RunLadderHandler(webapp.RequestHandler):
    def get(self):
        # Needs to iterate through the AILadderPlayer instances and schedule
        # some matches
        t = Tournament()
        t.put()

        ai_players = AILadderPlayer.all().filter("enabled =", True).fetch(PAGESIZE)
        ai_files = map(lambda a: a.file_name, ai_players)
        num_games = 10
        num_players = random.choice([2,3,4,5])
        argv_str = "-t %s --players %s" % (num_games, num_players) # Hardcoded 10 games

        deferred.defer(dmangame.appengine_run_tournament, ai_files, argv_str, str(t.key()))
        self.response.headers['Content-Type'] = 'text/html'
        self.response.out.write('Scheduling %s ladder matches with %s players per game' % (num_games, num_players))

class TournamentHandler(webapp.RequestHandler):
    def post(self):
        argv_str = urllib.unquote(self.request.get("argv"))
        self.response.headers['Content-Type'] = 'text/plain'
        self.response.out.write('Running tournament with %s' % argv_str)

        t = Tournament()
        t.put()

        ai_players = AILadderPlayer.all().filter("enabled =", True).fetch(PAGESIZE)
        ai_files = map(lambda a: a.file_name, ai_players)
        deferred.defer(dmangame.appengine_run_tournament, ai_files, argv_str, str(t.key()))

class RunHandler(webapp.RequestHandler):
    def post(self):
        # Need to iterate through all the parameters of the
        # request, parse their values and use it for
        # parseOptions, apparently.
        argv_str = urllib.unquote(self.request.get("argv"))

        self.response.headers['Content-Type'] = 'text/plain'
        fn = files.blobstore.create(mime_type='text/html')
        self.response.out.write('Running game with %s' % argv_str)
        deferred.defer(dmangame.appengine_run_game, argv_str, fn)

application = webapp.WSGIApplication(
                                     [('/', MainPage),
                                      ('/admin', AdminPage),
                                      ('/stats', AIStatsPage),
                                      ('/delete', DeleteHandler),
                                      ('/delete_old', DeleteOldHandler),
                                      ('/run_game', RunHandler),
                                      ('/ladder/register', RegisterAIHandler),
                                      ('/ladder/run', RunLadderHandler),
                                      ('/ladder', LadderPage),
                                      ('/disqus/([^/]+)?', DisqusPage),
                                      ('/replays/([^/]+)?', ReplayPage),
                                      ('/run_tournament', TournamentHandler)])

class MatchParticipant:
  pass

def adjust_rankings(ai_players, ai_files, game_scores):
  contestants = []
  # ai_players and ai_files are relatively ordered.
  for ai_player in ai_players:
    m = MatchParticipant()
    m.skill = (ai_player.skill, ai_player.uncertainty)
    m.rank = game_scores[ai_player.file_name]
    m.player = ai_player
    contestants.append(m)

  trueskill.AdjustPlayers(contestants)

  log.info("Calculating new trueskill ratings")
  for c in contestants:
    skill, uncertainty = c.skill
    log.info("rank: %s", c.rank)
    log.info("old: %s:%s", c.player.skill, c.player.uncertainty)
    c.player.skill = skill
    c.player.uncertainty = uncertainty
    c.player.matches += 1
    c.player.last_match = datetime.datetime.now()
    log.info("new: %s:%s", skill, uncertainty)
    c.player.put()

def get_map_players(ai_files, class_mapping):
  map_query   = AIMapPlayer.all()
  map_query   = map_query.filter("file_name IN", list(ai_files))
  map_query   = map_query.filter("map =", settings.MAP_NAME)
  map_players = map_query.fetch(len(ai_files))
  player_to_file = {}
  log.info("FOUND PLAYERS: %s", map_players)
  for m_player in map_players:
    player_to_file[m_player.file_name] = m_player

  for ai_file in ai_files:
    if not ai_file in player_to_file:
      # build the map player here.
      class_name = class_mapping[ai_file]
      m_player = AIMapPlayer(class_name=class_name,
                             file_name=ai_file,
                             enabled=True,
                             map=settings.MAP_NAME)
      map_players.append(m_player)

  log.info("MAP PLAYERS: %s", map_players)
  return map_players

# Examine the world and mark AIs that are timing out.
# If the AI is caught using a bigger than 10 second CPU Chunk and the
# deadline is exceeded, the AI will be penalized.
# If the AI is the only one who is executing, it will be penalized
# If the AI has used 90% CPU usage and the game hits the deadline, it is
# penalized
# If this happens 10 times, the AI is disabled.
def mark_timed_out_ai(world):
  ai_files = set()
  file_to_class_map = {}

  for ai in world.dumpScores():
    ai_instance = world.team_map[ai["team"]]
    ai_class = ai_instance.__class__
    ai_module = sys.modules[ai_class.__module__]
    ai_str = ai_module.__ai_str__
    ai_files.add(ai_str)
    file_to_class_map[ai_str] = ai_class.__name__


  total_time = defaultdict(int)

  for turn in world.execution_times:
    for ai in world.execution_times[turn]:
      total_time[ai] += world.execution_times[turn][ai]

  ai = world.executing
  TEN_SECONDS=10
  if not total_time[ai] or total_time[ai] / float(total) > 0.80 or \
    time.time() - world.execution_start_time > TEN_SECONDS:
    ai_instance = world.team_map[ai.team]
    ai_class = ai_instance.__class__
    ai_module = sys.modules[ai_class.__module__]
    ai_str = ai_module.__ai_str__
    log.info("deadlined %s, (prev time used: %ss, current chunk: %.2fs", ai_str, total_time[ai], time.time() - world.execution_start_time)
    ai_player = AILadderPlayer.get_by_key_name([ai_str])[0]

    if ai_player:
      ai_player.faults += 1
      log.info("%s has been responsible for %s faults", ai_str, ai_player.faults)

      if ai_player.faults >= 10:
        log.info("disabling player")
        ai_player.enabled = False

      ai_player.put()

def skip_disabled_ai(ai_files):
  allowed_files = []
  ai_players = AILadderPlayer.get_by_key_name(ai_files)
  for ai_p in ai_players:
    if ai_p.enabled:
      allowed_files.append(ai_p.file_name)
  return allowed_files

def record_ladder_match(world):
  # Now to generate tournament compatible scores
  # Collect the
  game_scores = {}
  alive = []
  dead = []
  ranks = {}
  ai_files = set()
  file_to_class_map = {}

  for ai in world.dumpScores():
    ai_instance = world.team_map[ai["team"]]
    ai_class = ai_instance.__class__
    ai_module = sys.modules[ai_class.__module__]
    ai_str = ai_module.__ai_str__
    ai_files.add(ai_str)
    file_to_class_map[ai_str] = ai_class.__name__

    # [okay]: TODO: actually use a better ranking system than tying for last.
    # Score should be:
    # If alive:
    #   score: dead units + kills
    # If dead:
    #   score: dead units + kills

    game_scores[ai_str] = ai["deaths"] + ai["kills"]
    if ai["units"] > 0:
      alive.append(ai_str)
    else:
      dead.append(ai_str)

  dead.sort(key=lambda u: game_scores[u], reverse=True)
  alive.sort(key=lambda u: game_scores[u], reverse=True)

  rank = 0
  score = None
  for ai_str in alive:
    ai_score = game_scores[ai_str]
    if ai_score is not score:
      rank += 1

    ranks[ai_str] = rank
    score = ai_score
    log.info("Alive: AI: %s, Score: %s, Rank: %s" % (ai_str, score, rank))

  rank += 1
  for ai_str in dead:
    ai_score = game_scores[ai_str]
    if ai_score is not score:
      rank += 1

    ranks[ai_str] = rank
    score = ai_score
    log.info("Dead: AI: %s, Score: %s, Rank: %s" % (ai_str, score, rank))

  ai_players = AILadderPlayer.get_by_key_name(ai_files)
  map_players = get_map_players(ai_files, file_to_class_map)

  adjust_rankings(ai_players, ai_files, ranks)
  adjust_rankings(map_players, ai_files, ranks)

def record_game_to_db(world, replay_blob_key, run_time, tournament_key=None):
  t = None
  if tournament_key:
    t = db.Key(tournament_key)

  gr = GameRun(replay=replay_blob_key,
               turns=world.currentTurn-1,
               run_time=run_time,
               map_name=settings.MAP_NAME,
               version=code_signature.digestCode(),
               tournament=t)
  gr.put()

  for ai_datum in world.dumpScores():
    team = ai_datum['team']
    ai = world.team_map[team]
    mod = sys.modules[ai.__class__.__module__]
    md = hashlib.md5()
    md.update(mod.__file_content__)
    version = md.hexdigest()

    win=False
    if ai_datum['units'] > 0:
      win = True

    aip = AIParticipant(class_name=ai.__class__.__name__,
                        file_name=mod.__file__,
                        version=version,
                        win=win,
                        kills=ai_datum['kills'],
                        deaths=ai_datum['deaths'],
                        units=ai_datum['units'],
                        buildings=ai_datum['buildings'],
                        game_run=gr)

    aip.put()

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    code_signature.freezeModules()
    main()

