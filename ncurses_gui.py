import curses.wrapper
import time
import sys
import logging

# Check that both stdout and stderr are redirected if using NCURSES

def redirect_outputs():
  f = open('game.out', 'w')
  print("Redirecting game output to game.out")

  # Redirect stdout
  if sys.stdout.isatty(): sys.stdout = f
  # Redirect stderr
  if sys.stderr.isatty(): sys.stderr = f



SECOND_BUFFER_LENGTH=10
class NcursesGui:
  def __init__(self):
    curses.wrapper(self.__init_ncurses)
    self.__second = None
    self.__last_seconds = []
    self.__turns_run = 0

  def __init_ncurses(self, stdscr):
    self.stdscr = stdscr

  def init(self, w):
    self.w = w
    l = len(w.AI)

    total_height,total_width = self.stdscr.getmaxyx()
    min_height = 5
    min_width = 20

    self.turn_win = curses.newwin(1, total_width, 0, 0)

    self.score_wins = {}

    max_columns = total_width / min_width
    max_rows = total_height / min_height

    w_d = l
    h_d = l
    if max_columns > l:
      h_d = 1
    elif max_rows > l:
      w_d = 1
    else:
      w_d = max_rows
      h_d = max_columns

    width = total_width / w_d
    height = total_height / h_d

    cur_x = 0
    cur_y = 2
    for x in xrange(l):
      print cur_y, cur_x
      ai = w.AI[x]
      score_win = curses.newwin(height, width, cur_y, cur_x)
      self.score_wins[ai.team] = score_win

      cur_x += width

      if cur_x >= total_width:
        cur_x = 0
        cur_y += height


  def update(self, t, s):
    self.draw(t,s)
    map(lambda s: s.noutrefresh(), self.score_wins.values())
    self.turn_win.noutrefresh()
    curses.doupdate()

  # We could try to actually draw the map in ncurses or
  # approximate it as well as possible. Right?
  # For now, just draw the turn counter and update ai scores
  def draw(self, turns, scores):
    self.draw_turns(turns)
    self.draw_scores(scores)

  def draw_turns(self, turns):
    # need to histogram the number of turns calculated in the
    # last second.
    cur_second = int(time.time())
    if self.__second != cur_second:
      self.__last_seconds.append(self.__turns_run)
      self.__turns_run = 0
      self.__second = cur_second
      if len(self.__last_seconds) > SECOND_BUFFER_LENGTH:
        self.__last_seconds.pop(0)

    avg_secs = sum(self.__last_seconds) / len(self.__last_seconds)

    self.__turns_run += 1
    turn = str(turns["currentturn"])
    try:
      self.turn_win.erase()
      self.turn_win.addstr("%s (%s/sec)" % (turn, avg_secs))
    except:
      pass

  def draw_scores(self, scores):
    for ai_team in scores:
      team = ai_team["team"]
      win = self.score_wins[team]

      ai_class = self.w.team_map[team].__class__.__name__
      s_str = "%s %s\n"%(team, ai_class)
      for k in ['idle', 'moving', 'shooting', 'capturing']:
        s_str += "%s:%s " % (k[0], ai_team[k])

      for k in ['units', 'kills', 'deaths', 'buildings' ]:
        s_str += "\n  %s:%s" % (k, ai_team[k])

      try:
        win.erase()
        win.addstr(s_str)
      except:
        pass

  def end(self):
    curses.endwin()

