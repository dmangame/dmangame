---
title: strategy
layout: default
---



##class Unit(mapobject.MapObject)##


Represents a Unit on the map. A Unit can move, shoot or capture for events, at the moment




###Methods###

####\_\_init\_\_(self, worldtalker, stats)####

####calcBulletPath(self, target_square)####
Calculates the path a bullet takes to get from the unit's position to target_square

####calcDistance(self, target_square)####
Calculate distance from this unit to target square

####calcUnitPath(self, target_square)####
Calculate the path this unit would take to get to target square

####calcVictims(self, target_square)####
If the unit shot at target square, which units would be hit?

Returns all visible units that would be hit by a bullet shot toward the destination (including own units and enemy units) if they were to not move until the bullet arrived.

####capture(self, b)####
initiates a capture of building if the unit is occuping the
same square as the building.  

For a capture to happen successfully, the Unit must stay in the building for CAPTURE_LENGTH time after initiating the capture.

####move(self, (x, y))####
move the unit towards (x,y) by their speed amount in this round.

if the unit doesn't receive a new order, it will continue
moving to that square on subsequent turns until it arrives.
it is also safe to continually call unit.move(dest) until the
unit arrives there.

####shoot(self, (x, y))####
shoot a bullet towards (x,y), even if (x,y) is not in range.

The bullet will travel as far as it can go. Any units who are
in the path of the bullet at the end of the round will take
damage.


###Properties###

####armor####
The armor of the unit, represents the damage this unit absorbs when it gets shot by a bullet.

####attack####
The attack of the unit, represents the damage this unit does with its bullets.

####energy####
The energy of the unit, represents the health of the unit

####in_range_enemies####
all enemy units that are within bullet distance of this unit.

it may return enemies not visible to this unit if they are visible to

another unit on the same team.

####is_alive####
if this unit is alive or not in the world

####is_capturing####
if this unit is currently capturing a building

####is_moving####
if this unit is currently moving.

####is_shooting####
if this unit is shooting

####is_under_attack####
if this unit is under attack

####position####
the position of this Unit on the map

####sight####
The sight of the unit, use: sight as R of unit

####speed####
The speed of the unit - the number of units distance the unit can travel in one turn.

####team####
The owner of the unit (an ai_id)

####unit_id####
The unique unit identifier used internally by the game

####visible_buildings####
all buildings that are in the range of sight of this unit

####visible_enemies####
all enemy units that are in the range of sight of this unit

####visible_squares####
all squares that are in the range of sight of this unit

