DMANGAME
--------

##Download##

You can find the latest version of the source code on [github][]

[github]:http://github.com/okayzed/dmangame

##Playing##

Run:

    # Run with graphics (you probably want this)
    python main.py -g ai/captureai.py ai/killncapture.py
    # Run without graphics
    python main.py ai/capture.ai ai/killncapture.py
    # Help
    python main.py --help


##Purpose##

To write an AI that competes against other AIs in a relatively simple world.
The overall objective is to crush your enemies, see them driven before you, and
to hear the lamentation of their pixels.


##Game Play##

Each game has a number of AI contestants who are responsible for managing their
Units. The game starts with no Units on the map and one building per AI.

At a fixed interval, each building will spawn a unit to the team that currently
owns the building. The end objective is to capture all enemy buildings and kill
all enemy units. Every unit is capable of shooting towards a square, moving
towards a square or capturing a building (If they are on the same square as a
building).

###Unit Attributes:###
  At the moment, all units have fixed attributes, but each building is capable
  of spawning units with different attributes.

####SPEED####
How far the unit can move in one round

####ENERGY####
How much energy the unit has, when this runs to 0, the unit
is killed and removed from the map.

####ATTACK####
How much damage a unit does

####SIGHT####
How far a unit can see on the map.

####ARMOR####
Modifies much damage a unit absorbs when being hit by a bullet

It is possible to have a map with multiple buildings spawning multiple units
with different attributes, but it is not implemented yet.

##Unit API##

### Actions ###
Each unit can perform one action per turn. If multiple actions are enqueued
inadvertently, an exception will be raised.

####unit.shoot((x,y))####
  this will shoot a bullet towards (x,y), even if X,Y is not in range. The
  bullet will travel as far as it can go. Any units who are in the path of the
  bullet at the end of the round will take damage.

####unit.move((x,y))####
  this will move the unit towards (x,y) by their speed amount

####unit.capture(building)####
  this initiates a capture of the building if the unit is occuping the same
  square as the building.  For a capture to happen successfully, the Unit must
  stay in the building for a length of time after initiating the capture.

See the pydocs for mapobject.py for more information on what
a Unit can do.

## AI API ##

See ai.py for the available AI functions, and look in ai/ for
example AIs.


See Also:
---------
I've been a fan of AI based games for a while, such as the [Google AI
Challenge][g_src] and the [Queue ICPC Challenge][i_src]. They are fun and challenging
(could you tell from their titles?)
[g_src]: http://ai-contect.com
[i_src]: http://queue.acm.org/icpc/

