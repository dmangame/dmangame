import settings
import json
import logging
log = logging.getLogger("JSPLAYER")

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

</style>
<canvas id="map" style="width: auto; float: left;"> </canvas>
<div id="ai_scores" style="width: auto; float: left;"> </div>
<script>
"""

HTML_SKELETON_END= """
</script>

</body>
</html>
"""

JS_PLAYER = """
var mapEl = document.getElementById("map");
window.onresize = function() {
  width=window.innerWidth;
  height=window.innerHeight;
  side = Math.min(width, height) - 20;
  mapEl.width = side;
  mapEl.height = side;
}

window.onresize();


var context = mapEl.getContext('2d');

var hudEl = document.getElementById("ai_scores");

var unit_actions = ['moving', 'shooting', 'idle', 'capturing'];
var ai_counts =['units', 'bldgs', 'kills', 'deaths' ];

function draw_ai_scores(ai_data, colors) {
  ai_data_html = "<div class='turn_counter'>" + (current_turn+1) + "/" + total_turns + "</div>";
  for (t in ai_data) {
    var html_str = "<div id='ai_" + t + "'>";
    var team = ai_data[t],
        color = colors[t];

    var bg_color = "rgb("+color[0]*255+","+color[1]*255+","+color[2]*255+");";
    html_str += "<div class='ai_color_cell' style='background-color:"+bg_color+";'></div>";
    html_str += "<div class='ai_header'>"+team["name"]+"</div>";

    html_str += "<div class='clearfix'>";
    html_str += "<div>";
    for (a in unit_actions) {
      action = unit_actions[a];
      html_str += "<span class='ai_info_cell'>";
      html_str += action + ":" + team[action];
      html_str += "</span>";
    }
    html_str += "</div>";

    html_str += "<div>";
    for (c in ai_counts) {
      count = ai_counts[c];
      html_str += "<span class='ai_info_cell'>";
      html_str += count + ":" + team[count];
      html_str += "</span>";
    }
    html_str += "</div>";

    html_str += "</div>";

    ai_data_html += html_str;
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

  for (u in turn_data["units"]) {
    context.strokeStyle = "none";
    context.lineWidth = 0;
    var unit_data = turn_data["units"][u],
        unit_static_data = world_data["units"][unit_data.id],
        pos = unit_data["pos"],
        x = pos[0],
        y = pos[1];

    var color = world_data.colors[unit_static_data["team"]],
        color_str = "rgb("+color[0]*255+","+color[1]*255+","+color[2]*255+")",
        alpha_color_str = "rgba("+color[0]*255+","+color[1]*255+","+color[2]*255+", 0.15)";
        path_color_str = "rgba("+color[0]*128+","+color[1]*128+","+color[2]*128+", 0.5)";
        ;

    context.fillStyle = color_str;
    context.fillRect(deltax*x, deltay*y, deltax, deltay);

    if (unit_data.unitpath) {

      start = unit_data.unitpath[0];
      end = unit_data.unitpath[1];
      if (start && end) {
        context.beginPath();
        context.strokeStyle = path_color_str;
        context.moveTo(start[0]*deltax+midx, start[1]*deltay+midy);
        context.lineTo(end[0]*deltax+midx, end[1]*deltay+midy);
        context.closePath();
        context.lineWidth = deltax;
        context.stroke();
      }
    }


    if (unit_data.bulletpath) {
        for (p in unit_data.bulletpath) {
          var path = unit_data.bulletpath[p];
          var start = path[0],
              end   = path[1];

          context.beginPath();
          context.strokeStyle = path_color_str;
          context.moveTo(start[0]*deltax+midx, start[1]*deltay+midy);
          context.lineTo(end[0]*deltax+midx, end[1]*deltay+midy);
          context.closePath();
          context.lineWidth = midx;
          context.stroke();
        }
    }
    context.strokeStyle = "none";
    context.lineWidth = 0;

    context.beginPath();
    context.fillStyle = alpha_color_str;
    context.arc(deltax*x, deltay*y, unit_static_data.stats.sight*deltax, 0, Math.PI * 2, false);
    context.closePath();
    context.fill();

  }

  for (b in world_data.bullets) {
    var bullet_data = world_data.bullets[b],
        pos = bullet_data.pos,
        x = pos[0],
        y = pos[1];


    context.fillStyle = "#000";
    context.fillRect(x*deltax, y*deltay, deltax, deltay);

  }

  for (b in turn_data.buildings) {
    var building_data = turn_data.buildings[b],
        building_static_data = world_data.buildings[building_data.id],
        pos = building_static_data.pos,
        x = pos[0],
        y = pos[1];

      var color = world_data.colors[building_data.team];
      if (color) {
          var color_str = "rgb("+color[0]*255+","+color[1]*255+","+color[2]*255+")";
      } else {
          var color_str = "rgb(0,0,0)";
      }

    context.fillStyle = "#000";
    context.fillRect(deltax*x-(midx), deltay*y-(midy), 2*deltax, 2*deltay);

    context.fillStyle = color_str;
    context.fillRect(deltax*x, deltay*y, deltax, deltay);

  }

  for (c in world_data.collisions) {
    var collision_data = world_data.collisions[c],
        pos = collision_data.pos,
        x = pos[0],
        y = pos[1];
        count = collision_data.count;
        survivor = collision_data.survivor;
        if (survivor) {
          var color = world_data.colors[survivor];
        } else {
          var color = (0.25, 0.25, 0.25);
        }

        color_str = "rgb("+color[0]*255+","+color[1]*255+","+color[2]*255+")";
        context.fillStyle = color_str;
        context.fillRect(deltax*x-(count/2*deltax), deltay*y-(count/2*deltay), count*deltax, count*deltay);
  };
}

current_turn = 0;
total_turns = WORLD_TURNS.length;

var world_spinner_id = setInterval(function() {
  var data = WORLD_TURNS[current_turn];
  if (data) {
    turn_data = data[0],
    ai_data    = data[1];
    draw_world(WORLD_DATA, turn_data);
    draw_ai_scores(ai_data, WORLD_DATA.colors);
  } else {
    clearTimeout(world_spinner_id);
  }
  current_turn += 1;
}, %s);

""" % (1000 / settings.FPS)

def save_to_js_file(world_data, world_turns):
  log.info("Saving %s turns to %s", len(world_turns), settings.JS_REPLAY_FILE)
  f = open(settings.JS_REPLAY_FILE, "w")
  f.write(HTML_SKELETON)
  f.write("WORLD_TURNS = %s;" %(json.dumps(world_turns)))
  f.write("WORLD_DATA = %s;" %(json.dumps(world_data)))

  f.write(JS_PLAYER)
  f.write(HTML_SKELETON_END)
  f.close()

