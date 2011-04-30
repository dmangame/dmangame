import urllib2

def main():
#  url_to = "http://localhost:8080/run"
  url_to = "http://dmangame-app.appspot.com/run"
  data = "ai=ai/basepatroller.py"

  r = urllib2.urlopen(url_to, data)
  print r.read()



if __name__ == "__main__":
  main()
