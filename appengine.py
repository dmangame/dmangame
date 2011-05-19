from __future__ import with_statement

from google.appengine.ext import blobstore
from google.appengine.ext import db
from google.appengine.ext import deferred
from google.appengine.api import files
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp import blobstore_handlers
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.webapp import template

import urllib
import hashlib
import os
import sys
import time
import datetime

import ai as ai_module
import code_signature
import world
from lib import jsplayer

from collections import defaultdict

import settings
import main as dmangame

import logging
log = logging.getLogger("APPENGINE")
log.setLevel(logging.INFO)

register = webapp.template.create_template_register()
template.register_template_library('appengine')

@register.filter
def hash(h,key):
    return h[key]

@register.filter
def datetime_to_seconds(value):
    dt = value
    seconds = time.mktime(dt.timetuple())
    return seconds

@register.filter
def truncate(value, arg):
    """
    Truncates a string after a given number of chars
    Argument: Number of chars to truncate after
    """
    try:
        length = int(arg)
    except ValueError: # invalid literal for int()
        return value # Fail silently.
    if not isinstance(value, basestring):
        value = str(value)
    if (len(value) > length):
        return value[:length]
    else:
        return value

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

class AIParticipant(db.Model):
    created_at = db.DateTimeProperty(auto_now_add=True)
    updated_at = db.DateTimeProperty(auto_now=True)
    class_name = db.StringProperty(required=True)
    file_name  = db.StringProperty(required=True)
    game_run   = db.ReferenceProperty(GameRun)
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

      log.info(ais)

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

      self.response.headers['Content-Type'] = 'text/html'
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


        has_next_page = False
        if len(games) == PAGESIZE + 1:
          has_next_page = games[-1].created_at
          games = games[:PAGESIZE]

        game_maps = sorted(list(map_set))
        game_ais = sorted(list(file_set))
        template_values = { "game_runs" : games,
                            "next_page" : has_next_page,
                            "maps"      : game_maps,
                            "ai_files"  : game_ais,
                            "can_delete" : users.is_current_user_admin()}

        path = os.path.join(TEMPLATE_DIR, "game_runs.html")
        self.response.headers['Content-Type'] = 'text/html'
        self.response.out.write(template.render(path, template_values))


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
          gr = GameRun.get(game)
          log.info(gr)
          if gr:
            for ai in gr.aiparticipant_set:
              ai.delete()
            blobstore.delete([gr.replay.key])
            gr.delete()

class TournamentHandler(webapp.RequestHandler):
    def post(self):
        argv_str = urllib.unquote(self.request.get("argv"))
        self.response.headers['Content-Type'] = 'text/plain'
        fn = files.blobstore.create(mime_type='text/html')
        self.response.out.write('Running tournament with %s' % argv_str)

        t = Tournament()
        t.put()
        deferred.defer(dmangame.appengine_run_tournament, argv_str, str(t.key()))

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
                                      ('/run_game', RunHandler),
                                      ('/disqus/([^/]+)?', DisqusPage),
                                      ('/replays/([^/]+)?', ReplayPage),
                                      ('/run_tournament', TournamentHandler)],
                                     debug=True)

# TODO: The game must be over for this to work.
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

