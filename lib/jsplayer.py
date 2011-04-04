import settings
import json

HTML_SKELETON = """
<html>
<head>
  <script src="js/raphael-min.js"></script>
</head>
<body>

<script>
"""

HTML_SKELETON_END= """
</script>
</body>
</html>
"""

JS_PLAYER = """
width=window.innerWidth;
height=window.innerHeight;
side = Math.min(width, height);
var paper = Raphael(0, 0, side, side);

function draw_world(world_data) {
  var deltax = side/world_data.mapsize,
      deltay = side/world_data.mapsize;
  paper.clear();

  for (u in world_data["units"]) {
    var unit_data = world_data["units"][u],
        pos = unit_data["position"],
        x = pos[0],
        y = pos[1];

    var color = world_data.colors[unit_data.team],
        color_str = "rgb("+color[0]*255+","+color[1]*255+","+color[2]*255+")";

    var this_unit = paper.rect(deltax*x, deltay*y, deltax, deltay);
    this_unit.attr({"fill" : color_str, "stroke" : "none" })

    var this_unit_sight = paper.circle(deltax*x, deltay*y, unit_data.stats.sight*deltax);
    this_unit_sight.attr({"fill" : color_str, "opacity" : 0.15, "stroke" : "none" });

    if (unit_data.unitpath) {

      for (sq in unit_data.unitpath)
      {
        var pos = unit_data.unitpath[sq];
        var x = pos[0],
            y = pos[1];
        var trail = paper.rect(x*deltax, y*deltay, deltax, deltay);
        trail.attr({"fill" : color_str, "stroke" : "none", "opacity" : 0.50 })
      }
    }


    if (unit_data.bulletpath) {
        for (p in unit_data.bulletpath) {
          var path = unit_data.bulletpath[p];
          for (sq in path) {
            var pos = path[sq];
            var x = pos[0],
                y = pos[1];
            var path_color_str = "rgb(128, 128, 128)";
            var trail = paper.rect(x*deltax, y*deltay, deltax, deltay);
            trail.attr({"fill" : path_color_str, "stroke" : "none", "opacity" : 0.5 })
          }
        }
    }
  }

  for (b in world_data.bullets) {
    var bullet_data = world_data.bullets[b],
        pos = bullet_data.position,
        x = pos[0],
        y = pos[1];


    var this_bullet = paper.rect(x*deltax, y*deltay, deltax, deltay);
    this_bullet.attr({"fill" : "black", "stroke" : "none" });

  }

  for (b in world_data.buildings) {
    var building_data = world_data.buildings[b],
        pos = building_data.position,
        x = pos[0],
        y = pos[1];

    var color = world_data.colors[building_data.team],
        color_str = "rgb("+color[0]*255+","+color[1]*255+","+color[2]*255+")";

    var this_building = paper.rect(deltax*x-(deltax/2), deltay*y-(deltay/2), 2*deltax, 2*deltay);
        this_building.attr({"fill" : color_str, "stroke" : "none" })

  }

  for (c in world_data.collisions) {
    var collision_data = world_data.collisions[c],
        pos = collision_data.position,
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
        paper.rect(deltax*x-(count/2*deltax), deltay*y-(count/2*deltay), count*deltax, count*deltay);
  };
}

current_turn = 0;
var world_spinner_id = setInterval(function() {
  var world_data = WORLD_TURNS[current_turn];
  if (world_data) {
    draw_world(world_data);
  } else {
    clearTimeout(world_spinner_id);
  }
  current_turn += 1;
}, 100);

"""

def save_to_js_file(world_turns):
  f = open(settings.JS_REPLAY_FILE, "w")
  f.write(HTML_SKELETON)
  f.write("WORLD_TURNS = %s;" %(json.dumps(world_turns)))

  f.write(JS_PLAYER)
  f.write(HTML_SKELETON_END)
  f.close()

