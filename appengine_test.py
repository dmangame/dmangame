import urllib2
import urllib
import sys
import settings

import yaml




# Should make some sort of marshalling to make it feel like
# google's app engine appears the same as local.

# So, gotta parse options and then send them over the same way
# for deparsing with the main loadOptions function

def main():
  yaml_data = open("app.yaml").read()
  app_data = yaml.load(yaml_data)

  if settings.APPENGINE_LOCAL:
    url_to = "http://localhost:8080/run"
  else:
    url_to = "http://%s.appspot.com/run" % (app_data["application"])

  data = " ".join(sys.argv[1:])
  data_str = urllib.urlencode({"argv" : data})

  print "Posting to: ", url_to
  print "Posting with:"
  print data_str
  r = urllib2.urlopen(url_to, data_str)
  print r.read()

if __name__ == "__main__":
  main()
