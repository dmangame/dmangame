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

import ai as ai_module
import code_signature
import world
from lib import jsplayer

import settings

register = webapp.template.create_template_register()
template.register_template_library('appengine')

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


import main as dmangame

import logging
log = logging.getLogger("APPENGINE")

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

class AdminPage(webapp.RequestHandler):
    def get(self):
      self.redirect(users.create_login_url(self.request.uri))

class MainPage(webapp.RequestHandler):
    def get(self):
        games = GameRun.all().order("-created_at").fetch(PAGESIZE)


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

class ReplayHandler(webapp.RequestHandler):
    def get(self, resource):
        resource = str(urllib.unquote(resource))
        blob_info = blobstore.BlobInfo.get(resource)
        blob_reader = blob_info.open()
        blob_data = blob_reader.read()
        self.response.headers['Content-Type'] = 'text/html'
        self.response.out.write(blob_data)

application = webapp.WSGIApplication(
                                     [('/', MainPage),
                                      ('/admin', AdminPage),
                                      ('/delete', DeleteHandler),
                                      ('/run_game', RunHandler),
                                      ('/replays/([^/]+)?', ReplayHandler),
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
    md.update(open(mod.__file__).read())
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
    main()

