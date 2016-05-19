import settings
try:
  import json
except ImportError:
  from django.utils import simplejson as json
import logging
import copy
import re
from collections import defaultdict

log = logging.getLogger("JSPLAYER")

JSLOOKUP = {
  "buildings"    : "a",
  "bulletpath"   : "b",
  "bullets"      : "c",
  "capturing"    : "d",
  "collisions"   : "e",
  "count"        : "f",
  "currentturn"  : "g",
  "deaths"       : "h",
  "idle"         : "i",
  "kills"        : "j",
  "moving"       : "k",
  "shooting"     : "l",
  "survivor"     : "m",
  "team"         : "n",
  "unitpath"     : "o",
  "units"        : "p",
  "stats"        : "q",
  "sight"        : "r",
  "speed"        : "s",
  "position"     : "t",
  "id"           : "u",
  "region"       : "v",
  "highlights"   : "w",
  "line"         : "y",
}

HTML_SKELETON = """
<html>
<head>
</head>
<body>

<style>

#map {
  border: 2px solid black;
}

#ai_scores {
  margin-left: 5px;
}

#map_interactive {
  position: fixed;
  opacity: 0.25;
  margin-left: 5px;
  margin-top: 5px;
  font-size: 150%;
}

#turn_counter {
  width: 50px;
  text-align: center;
  background: none;
  border: 0px;
  margin: 1px;
  font-size: 100%;
}

#turn_counter:hover {
  background-color: #ededed;
  border: 1px dashed #ddd;
  margin: 0px 1px;
}

.ai_color_cell {
  width: 25px;
  height: 25px;
  float: left;
  margin-top: 10px;
  margin-bottom: 10px;
  margin-right: 10px;
}

.ai_header {
  padding: 10px 0px;
  font-weight: bold;
  float: left;
}

.ai_info_cell {
  padding: 5px;
  margin: auto;
}

.clearfix {
  clear: both;
}

#map {

}

#rewind {
  cursor: pointer;
  display: inline-block;
  margin: 0 5px;
  margin-left: 5px;
}
#play_direction {
  cursor: pointer;
  display: inline-block;
  margin: 0 5px;
}

#play_direction:hover {
  text-decoration: underline;
}

</style>
<div>
"""

PLAYER_CONTROLS="""
  <div>
    <canvas id="map" style="width: auto; float: left;">
    </canvas>

    <div id="map_interactive">

      <span id="rewind"> &lt;&lt; </span>
      <input type="text" id="turn_counter"></input> / <span id="total_turns"></span>
      <span id="play_direction"> &gt; </span>

      <select id="playback_speed">
        <option value="%(double_speed)s">2x</option>
        <option value="%(normal_speed)s" selected="True">1x</option>
        <option value="%(half_speed)s">1/2 x</option>
        <option value="%(quarter_speed)s">1/4 x</option>
      </select>
    </div>

  </div>

  <div id="ai_scores" style="width: auto; float: left;"> </div>

</div>
<script>
TOTAL_TURNS = 0;
"""

HTML_SKELETON_END= """
</script>

</body>
</html>
"""

JS_PLAYER = """
var playSpeedEl = document.getElementById("playback_speed"),
    mapEl = document.getElementById("map"),
    turnEl = document.getElementById("turn_counter"),
    mapControlEl = document.getElementById("map_interactive"),
    totalEl = document.getElementById("total_turns"),
    hudEl = document.getElementById("ai_scores");

playSpeedEl.onchange = function(val, a) {
  var option = this.options[this.selectedIndex],
      val    = option.value;
  setWorldSpeed(val);
};


turnEl.onmouseout = function() {
  current_turn = parseInt(this.value);
};
turnEl.onchange = turnEl.onmouseout;

mapControlEl.onmouseout = function() {
  mapControlEl.style.opacity = 0.25;
  STOPPED=false;
}

mapControlEl.onmouseover = function() {
  mapControlEl.style.opacity = 1;
  STOPPED=true;
}

var playDirectionEl = document.getElementById("play_direction");
var rewindEl = document.getElementById("rewind");

REWIND=false;
rewindEl.onmouseover = function() {
    REWIND = true;
}

rewindEl.onmouseout = function() {
    REWIND = false;
}

rewindEl.onclick = function() {
  current_turn = 0;
  STOPPED=false;
  startWorld();
}

STOPPED=false;
playDirectionEl.onclick = function() {
  if (!STOPPED) {
    STOPPED=true;
  } else {
    if (current_turn >= TOTAL_TURNS) {
      current_turn = 0;
    }
    STOPPED=false;
    startWorld();
  }
}

window.onresize = function() {
  width=window.innerWidth;
  height=window.innerHeight;
  side = Math.min(width, height) - 40;
  mapEl.width = side;
  mapEl.height = side;
}

window.onresize();


var context = mapEl.getContext('2d');

var unit_actions = ['moving', 'shooting', 'idle', 'capturing'];
var ai_counts =['units', 'buildings', 'kills', 'deaths' ];


function draw_turn_count() {
  var turnEl = document.getElementById("turn_counter");
  turnEl.value = current_turn+1;
}

function draw_ai_scores(ai_data, colors, names) {
  ai_data_html = "";
  for (t in ai_data) {
    var html_arr = new Array();
    var team_data = ai_data[t],
        ai_lookup = AI_LOOKUP_SUPPL[t];

    var team = team_data[ai_lookup.team],
        color = colors[team];

    html_arr.push("<div id='ai_" + team + "'>");
    var bg_color = "rgb("+
                      parseInt(color[0]*255)+","+
                      parseInt(color[1]*255)+","+
                      parseInt(color[2]*255)+")";

    html_arr.push("<div class='ai_color_cell' style='background-color:"+bg_color+";'></div>");
    html_arr.push("<div class='ai_header'>"+names[team]+"</div>");

    html_arr.push("<div class='clearfix'>");
    html_arr.push("<div>");
    for (a in unit_actions) {
      action = unit_actions[a];
      html_arr.push("<span class='ai_info_cell'>");
      html_arr.push(action + ":" + team_data[ai_lookup[action]]);
      html_arr.push("</span>");
    }
    html_arr.push("</div>");

    html_arr.push("<div>");
    for (c in ai_counts) {
      count = ai_counts[c];
      html_arr.push("<span class='ai_info_cell'>");
      html_arr.push(count + ":" + team_data[ai_lookup[count]]);
      html_arr.push("</span>");
    }
    html_arr.push("</div>");

    html_arr.push("</div>");

    ai_data_html += html_arr.join('').replace(/undefined/g, "0");
  }

  hudEl.innerHTML = ai_data_html;
}

function draw_world(world_data, turn_data) {
  var deltax = side/world_data.mapsize,
      deltay = side/world_data.mapsize,
      midx   = deltax/2,
      midy   = deltay/2;

  context.fillStyle = "#fff";
  context.fillRect(0, 0, side, side);

  for (u in turn_data[TD_LOOKUP.units]) {
    context.lineWidth = 0;
    unit_data = turn_data[TD_LOOKUP.units][u]

    var unit_static_data = world_data[JSLOOKUP.units][unit_data[TD_LOOKUP_SUPPL.units.id]],
        pos = unit_data[TD_LOOKUP_SUPPL.units.position],
        x = pos[0],
        y = pos[1];


    var color = world_data.colors[unit_static_data[JSLOOKUP.team]],
        color_str = "rgb("+
                      parseInt(color[0]*255)+","+
                      parseInt(color[1]*255)+","+
                      parseInt(color[2]*255)+")",
        alpha_color_str = "rgba("+
                      parseInt(color[0]*255)+","+
                      parseInt(color[1]*255)+","+
                      parseInt(color[2]*255)+", 0.35)",
        path_color_str = "rgba("+
                      parseInt(color[0]*255)+","+
                      parseInt(color[1]*255)+","+
                      parseInt(color[2]*255)+", 0.5)";

    context.fillStyle = color_str;
    context.fillRect(deltax*x, deltay*y, deltax, deltay);

    // Draw movement
    if (unit_data[TD_LOOKUP_SUPPL.units.unitpath]) {

      start = unit_data[TD_LOOKUP_SUPPL.units.unitpath][0];
      end = unit_data[TD_LOOKUP_SUPPL.units.unitpath][1];
      if (start && end) {
        context.beginPath();
        context.strokeStyle = path_color_str;
        context.moveTo(start[0]*deltax+midx, start[1]*deltay+midy);
        context.lineTo(end[0]*deltax+midx, end[1]*deltay+midy);
        context.closePath();
        context.lineWidth = deltax;
        context.stroke();
      }
    } // end movement


    // Bullet paths
    if (unit_data[TD_LOOKUP_SUPPL.units.bulletpath]) {
        for (p in unit_data[TD_LOOKUP_SUPPL.units.bulletpath]) {
          var path = unit_data[TD_LOOKUP_SUPPL.units.bulletpath][p];
          var start = path[0],
              end   = path[1];

          if (start && end) {

            context.beginPath();
            context.strokeStyle = path_color_str;
            context.moveTo(start[0]*deltax+midx, start[1]*deltay+midy);
            context.lineTo(end[0]*deltax+midx, end[1]*deltay+midy);
            context.closePath();
            context.lineWidth = midx;
            context.stroke();
          }
        }
    } // End bullet path


    // Circle of sight
    context.lineWidth = 0;
    context.beginPath();
    context.fillStyle = alpha_color_str;
    context.arc(deltax*x, deltay*y, unit_static_data[JSLOOKUP.stats][JSLOOKUP.sight]*deltax, 0, Math.PI * 2, false);
    context.closePath();
    context.fill();
  } // end unit


  // Draw buildings
  for (b in turn_data[TD_LOOKUP.buildings]) {
    var building_data = turn_data[TD_LOOKUP.buildings][b],
        building_static_data = world_data[JSLOOKUP.buildings][building_data[TD_LOOKUP_SUPPL.buildings.id]],
        pos = building_static_data[JSLOOKUP.position],
        x = pos[0],
        y = pos[1];

      var color = world_data.colors[building_data[TD_LOOKUP_SUPPL.buildings.team]];
      if (color) {
          var color_str = "rgb("+
                parseInt(color[0]*255)+","+
                parseInt(color[1]*255)+","+
                parseInt(color[2]*255)+")";
      } else {
          var color_str = "rgb(0,0,0)";
      }

    context.fillStyle = "#000";
    context.fillRect(deltax*x-(midx), deltay*y-(midy), 2*deltax, 2*deltay);

    context.fillStyle = color_str;
    context.fillRect(deltax*x, deltay*y, deltax, deltay);

  } // End building drawing

  // Draw collisions
  for (c in turn_data[TD_LOOKUP.collisions]) {
    var collision_data = turn_data[TD_LOOKUP.collisions][c];

    var pos = collision_data[TD_LOOKUP_SUPPL.collisions.position];
    var x = pos[0],
        y = pos[1];
        count = collision_data[TD_LOOKUP_SUPPL.collisions.count];
        survivor = collision_data[TD_LOOKUP_SUPPL.collisions.survivor];
        var color = [0, 0, 0];
        if (survivor != null) {
          color = world_data.colors[survivor];
        }

        color_str = "rgb("+color[0]*255+","+color[1]*255+","+color[2]*255+")";
        context.fillStyle = color_str;
        context.fillRect(deltax*x-(count/2*deltax), deltay*y-(count/2*deltay), count*deltax, count*deltay);
  }; // End collision drawing

  // Draw highlights
  for (h in turn_data[TD_LOOKUP.highlights]) {
    var highlight_data = turn_data[TD_LOOKUP.highlights][h];
    var start = highlight_data[TD_LOOKUP_SUPPL.highlights.start],
        end = highlight_data[TD_LOOKUP_SUPPL.highlights.end],
        team = highlight_data[TD_LOOKUP_SUPPL.highlights.team],
        color = world_data.colors[team],
        alpha_color = (color[0], color[1], color[2], 0.25),
        shape = highlight_data[TD_LOOKUP_SUPPL.highlights.shape];
        color_str = "rgba("+
                      parseInt(color[0]*255)+","+
                      parseInt(color[1]*255)+","+
                      parseInt(color[2]*255)+", 0.1)",

    context.fillStyle = color_str;
    context.strokeStyle = color_str;
    if (shape == "region") {
      context.fillRect(deltax*start[0], deltay*start[1], deltax*end[0], deltax*end[1]);
    }
    if (shape == "line") {
      context.lineWidth = deltax / 2;
      context.beginPath();
      context.moveTo(deltax*start[0], deltay*start[1]);
      context.lineTo(deltax*end[0], deltay*end[1]);
      context.closePath();
      context.stroke();
    }

  };

}

DIRECTION=1;
TIMER_ID=null;
current_turn = 0;
totalEl.innerHTML = TOTAL_TURNS;


TIMER = ###INTERVAL###;

var getTurn = function(turn) {
  var cur_turn = 0;
  var turns = null;
  for (i in TURN_SET) {
    turns = TURN_SET[i];
    if (cur_turn + turns.LENGTH > turn) {
      break;
    }

    cur_turn += turns.LENGTH;
  }

  if (turns) {
    TD_LOOKUP = turns.TD_LOOKUP;
    TD_LOOKUP_SUPPL = turns.TD_LOOKUP_SUPPL;
    AI_LOOKUP = turns.AI_LOOKUP;
    AI_LOOKUP_SUPPL = turns.AI_LOOKUP_SUPPL
    return [turns.WORLD_TURNS[turn - cur_turn], turns.AI_TURNS[turn - cur_turn]];
  }
}


var spinWorld = function() {
  if (!REWIND && STOPPED) {
    playDirectionEl.innerHTML = '=';
    return;
  }

  var direction = 1;
  if (REWIND) {
    direction = -1;
    playDirectionEl.innerHTML = '&lt';
  } else {
    playDirectionEl.innerHTML = '&gt';
    direction = 1;
  }

  if (current_turn < 0) {
    current_turn = 0;
  } else if (current_turn >= TOTAL_TURNS) {
    current_turn = TOTAL_TURNS - 1;
  }

  var turn = getTurn(current_turn),
      turn_data = turn[0],
      ai_data = turn[1];

  if (turn_data) {
    draw_world(WORLD_DATA, turn_data);
    draw_ai_scores(ai_data, WORLD_DATA.colors, WORLD_DATA.names);
    draw_turn_count();
  } else {
    if (direction == -1) {
      return;
    }
  }
  current_turn += direction;

}
var startWorld = function() {
  if (TIMER_ID) {
    clearTimeout(TIMER_ID);
    TIMER_ID = null;
  }
  var world_spinner_id = setInterval(spinWorld , TIMER);

  TIMER_ID =  world_spinner_id;
}

var setWorldSpeed = function(interval) {
  TIMER = interval;
  startWorld();
}

var setWorldPosition = function(pos) {
  current_turn = pos;
}

startWorld();

"""

def strip_whitespace(st):
  return re.sub('\s', '', st)

def translate_array(arr, translation_key, drop_zeroes=False):
  for a in arr:
    if isinstance(a, (list, tuple)):
      translate_array(a, translation_key, drop_zeroes)
    if isinstance(a, (dict)):
      translate_dict(a, translation_key, drop_zeroes)

# Need a recursive strategy to replace dictionaries with
# dictionaries that have their keys translated.
def translate_dict(d, translation_key, drop_zeroes=False):
  for k in d.keys():
    v = d[k]

    if v == 0 and drop_zeroes:
      del d[k]
      continue

    if k in translation_key:
      d[translation_key[k]] = v
      del d[k]
    if isinstance(v, (list, tuple)):
      translate_array(v, translation_key, drop_zeroes)
    if isinstance(v, (dict)):
      translate_dict(v, translation_key, drop_zeroes)

def key_merge(lookup, other_lookup):
  sub_keys = set(lookup.keys() + other_lookup.keys())
  sorted_keys = sorted(list(sub_keys))
  for k in xrange(len(sorted_keys)):
    lookup[sorted_keys[k]] = k


# To turn a dict into a table, we have to determine table
# properties - this recurses through arrays and dicts,
# figuring out the table columns.
def determine_keys(arr_data):
  keys = set()
  types_seen = set()
  max_count = 0
  for d in arr_data:
    types_seen.add(type(d))
    t = type(d)
    if t not in (dict, list, tuple):
      return None, None
    if len(types_seen) >= 2:
      return None, None

    if type(d) == dict:
      keys.update(set(d.keys()))
    else:
      max_count = max(len(d), max_count)

  key_lookups = defaultdict(dict)
  if not keys:
    sorted_keys = range(0, max_count)
  else:
    sorted_keys = list(keys)
    sorted_keys.sort()

  for d in arr_data:
    for k in sorted_keys:
      try:
        val = d[k]
      except Exception, e:
        val = None

      if isinstance(val, (dict)):
        val = [val]

      if isinstance(val, (list, tuple)):
        sub_key_lookup, sub_key_lookups = determine_keys(val)

        # Have to do key merges:
        if sub_key_lookup:
          key_merge(sub_key_lookup, key_lookups[k])
          key_lookups[k].update(sub_key_lookup)

        if sub_key_lookups:
          for kk in sub_key_lookups:
            key_merge(sub_key_lookups[kk], key_lookups[kk])
          key_lookups.update(sub_key_lookups)

  this_lookup = {}
  for i in xrange(len(sorted_keys)):
    this_lookup[sorted_keys[i]] = i

  return this_lookup, key_lookups


# Horizontal pack the world turns and ai_data from an array of dicts into a table format. This is done using keys returned from determine_keys.

def horizontal_pack(arr_data, this_lookup, sub_key_lookup):
  # Collect the keys, first:
  new_arr_data = []


  for d in arr_data:
    if not isinstance(d, (list, tuple, dict)):
      row = d

    else:
      row = [None]*len(this_lookup)
      for k in this_lookup:
        val = None

        try:
          val = d[k]
        except Exception, e:
          pass

        boxed = False
        if isinstance(val, (dict)):
          val = [val]
          boxed = True

        if isinstance(val, (list, tuple)):
          val = horizontal_pack(val, sub_key_lookup[k], sub_key_lookup)

        if boxed:
          val = val.pop()

        row[this_lookup[k]] = val

    new_arr_data.append(row)

  return new_arr_data


# It needs to translate the world data into smaller format
# words using minification or something.

# Need to group the world turns into a smaller size, so that
# the JSONification doesn't take forever.

def begin_save_to_js_file(world_turns):
  log.info("Creating %s", settings.JS_REPLAY_FILENAME)

  f = settings.JS_REPLAY_FILE
  if not f:
    f = open(settings.JS_REPLAY_FILENAME, "w")

  speeds = {
   "half_speed"     : 2 * 1000 / settings.FPS,
   "quarter_speed"  : 4 * 1000 / settings.FPS,
   "normal_speed"   : 1 * 1000 / settings.FPS,
   "double_speed"   : 0.5 * 1000 / settings.FPS,
  }

  f.write(HTML_SKELETON)
  f.write(PLAYER_CONTROLS % speeds)
  f.write("TURN_SET = [];\n");

  if not settings.JS_REPLAY_FILE:
    f.close()



def end_save_to_js_file(world_data):
  f = settings.JS_REPLAY_FILE
  if not f:
    f = open(settings.JS_REPLAY_FILENAME, "a")

  f.write(JS_PLAYER.replace("###INTERVAL###",
                            str(1000 / settings.FPS)))

  world_data = copy.deepcopy(world_data)
  translate_dict(world_data, JSLOOKUP)
  f.write("JSLOOKUP = %s;\n" % strip_whitespace((json.dumps(JSLOOKUP))))
  f.write("WORLD_DATA = %s;\n" % (strip_whitespace(json.dumps(world_data))))

  f.write(HTML_SKELETON_END)

  if not settings.JS_REPLAY_FILE:
    f.close()

def save_world_turns_to_js_file(world_turns):

  f = settings.JS_REPLAY_FILE
  if not f:
    f = open(settings.JS_REPLAY_FILENAME, "a")

  world_turns, ai_turns = zip(*world_turns)
  world_lookup, world_key_lookups = determine_keys(world_turns)

  f.write("TOTAL_TURNS += %s;\n" % (len(world_turns)))
  f.write("TURN_SET.push(function() {\n");
  h_arr = horizontal_pack(world_turns, world_lookup, world_key_lookups)
  f.write("var LENGTH=%s;\n"%(len(world_turns)))
  f.write("var TD_LOOKUP=%s;\n"%(strip_whitespace(json.dumps(world_lookup))));
  f.write("var TD_LOOKUP_SUPPL=%s;\n"%(strip_whitespace(json.dumps(world_key_lookups))));

  # Use the array extension method in JS so we can write less lines at a time.
  f.write("var WORLD_TURNS = [];\n");

  # Scrub excess timer info from AIs.
  for ai_turn in ai_turns:
    for ai in  ai_turn:
      del ai['time']

  ai_lookup, ai_key_lookups = determine_keys(ai_turns)
  h_arr = horizontal_pack(ai_turns, ai_lookup, ai_key_lookups)
  f.write("var AI_LOOKUP = %s;\n" % (strip_whitespace(json.dumps(ai_lookup))))
  f.write("var AI_LOOKUP_SUPPL = %s;\n" % (strip_whitespace(json.dumps(ai_key_lookups))))
  f.write("var AI_TURNS = [];\n");

  log.info("Saving %s turns to %s", len(world_turns), settings.JS_REPLAY_FILENAME)

  LINES=50
  h_arr = horizontal_pack(world_turns, world_lookup, world_key_lookups)
  for i in xrange(len(h_arr) / LINES+1):
    lines = h_arr[i*LINES:(i+1)*LINES]
    if lines:
      f.write("WORLD_TURNS.push.apply(WORLD_TURNS, %s);\n" % strip_whitespace(json.dumps(lines)))

  h_arr = horizontal_pack(ai_turns, ai_lookup, ai_key_lookups)
  for i in xrange(len(h_arr) / LINES+1):
    lines = h_arr[i*LINES:(i+1)*LINES]
    if lines:
      f.write("AI_TURNS.push.apply(AI_TURNS, %s);\n" % strip_whitespace(json.dumps(lines)))

  f.write("""
  return {
    AI_LOOKUP : AI_LOOKUP,
    AI_LOOKUP_SUPPL : AI_LOOKUP_SUPPL,
    AI_TURNS : AI_TURNS,
    TD_LOOKUP : TD_LOOKUP,
    TD_LOOKUP_SUPPL : TD_LOOKUP_SUPPL,
    WORLD_TURNS : WORLD_TURNS,
    LENGTH : LENGTH };\n""");
  f.write("\n}());\n");
  if not settings.JS_REPLAY_FILE:
    f.close()

def save_to_js_file(world_data, world_turns):
  begin_save_to_js_file(world_turns)
  save_world_turns_to_js_file(world_turns)
  end_save_to_js_file(world_data)


START_WORLD_HTML=False
def save_world_turns(world_turns):
  if not settings.JS_REPLAY_FILE and not settings.JS_REPLAY_FILENAME:
    return

  global START_WORLD_HTML
  if not START_WORLD_HTML:
    START_WORLD_HTML=True
    begin_save_to_js_file(world_turns)

  # Save the world information to an output file.
  save_world_turns_to_js_file(world_turns)

def end_world(world_data):
  global START_WORLD_HTML
  START_WORLD_HTML=False
  end_save_to_js_file(world_data)

