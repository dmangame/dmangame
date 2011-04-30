import urllib2
import main as dmangame


# Should make some sort of marshalling to make it feel like
# google's app engine appears the same as local.

# So, gotta parse options and then send them over the same way
# for deparsing with the main loadOptions function

def main():
  options, args = dmangame.parseOptions()
#  url_to = "http://dmangame-app.appspot.com/run"
  url_to = "http://localhost:8080/run"
  data = '&'.join(map(lambda x: "ai=%s"%x, args))

  r = urllib2.urlopen(url_to, data)
  print r.read()



if __name__ == "__main__":
  main()
