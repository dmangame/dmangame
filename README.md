DMANGAME
--------

##Download##

You can find the latest version of the source code on [github][]

[github]:http://github.com/okayzed/dmangame

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

### Properties ###

####unit.position####
The units current position on the map

####unit.is_alive####
If the unit is still alive on the map

####unit.is_capturing####
If the unit is in the middle of a capture event.

####unit.energy####
The unit's remaining health

####unit.team####
The string representing what team the unit is on

####unit.visible_squares####
All squares within SIGHT distance from unit

####unit.visible_buildings####
All buildings within SIGHT distance from unit

####unit.visible_enemies####
All enemies within SIGHT distance from the unit

### Helpers ###

####unit.isVisible(unit2)####
Can unit see unit2?

####unit.getBulletPath((x,y))####
Give the path a bullet would take to get to x,y

####unit.getDistance((x,y))####
The distance to (x,y) for unit

####unit.getVictims((x,y))####
If the unit shot towards (x,y), who would be hit? Friendly fire is enabled, so
be careful.

## AI API ##

### User Implemented ###

####_init####
####_spin####
####\_new\_unit####

### Properties ###

####ai.visible_buildings####
####ai.visible_enemies####
####ai.visible_squares####
####ai.my_units####
####ai.my_buildings####
####ai.current_turn####
####ai.score####

See ai/ for example implemented AIs.


See Also:
---------
I've been a fan of AI based games for a while, such as the [Google AI
Challenge][g_src] and the [Queue ICPC Challenge][i_src]. They are fun and challenging
(could you tell from their titles?)
[g_src]: http://ai-contect.com
[i_src]: http://queue.acm.org/icpc/

