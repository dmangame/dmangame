from google.appengine.ext import blobstore
from google.appengine.ext import deferred
from google.appengine.api import files
from google.appengine.ext import webapp
from google.appengine.ext.webapp import blobstore_handlers
from google.appengine.ext.webapp.util import run_wsgi_app
import urllib

import main as dmangame

class MainPage(webapp.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/plain'
        self.response.out.write('Current stats for matches will go here')

class AiRun(webapp.RequestHandler):
    def post(self):
        ais = self.request.get_all("ai")
        self.response.headers['Content-Type'] = 'text/plain'
        fn = files.blobstore.create(mime_type='text/html')
        deferred.defer(dmangame.appengine_run_game, ais, fn)
        self.response.out.write('Running game with %s' % str(ais))

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
                                      ('/run', AiRun),
                                      ('/replays/([^/]+)?', ReplayHandler)],

                                     debug=True)
def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
