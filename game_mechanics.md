---
title: Game Mechanics
layout: default
---

note: upper case words are variables defined in settings.py or a map with the
-m option.

## world

The world is a 2-dimensional square that is MAP_SIZExMAP_SIZE. There are 3
main objects that exist in the game world: units, buildings and bullets.

## units

The only object that the AIs can command are units. Each unit has an AI that
it belongs to and it will only accept commands from that AI. These units have
3 abilities: moving, shooting and capturing. Additionally, every unit is able
to see its surroundings and report them back to its AI. The units have energy
and when that falls to zero, they die. The only way to acquire more units is
through buildings.

## buildings

Buildings are stationary objects that spawn a new Unit every UNIT_SPAWN_MOD
turns for the AI that owns the Building. A building can be captured by another
AI through its units. To capture a building, a unit must step inside it and
begin capturing. If the unit can stay there for CAPTURE_LENGTH turns without
shooting or moving, the base will change ownership to that unit's AI.

## moving

An AI may tell a unit to move to any square on the map. The unit will move
forward SPEED_MODIFIERxLOG(MAP_SIZE) squares along the shortest possible route
to the square until it arrives or another directive is issued.

If the square is invalid, an exception will be raised.

## collisions

If two or more AI teams have units that occupy the same square during a turn,
the units collide with each other. All teams then lose the amount of the
second greatest number of units on the square.

## attacking

When a unit attacks, they shoot towards a square that they want to hit. The
bullet travels at about MAP_SIZE/BULLET_SPEED_MODIFIER units a turn, while
their full range is MAP_SIZE/BULLET_RANGE_MODIFIER units. Any unit who falls
within the path of a bullet will take damage (including allies).

## damage

When a bullet goes through the same square that a unit is moving through on a
turn, the unit's energy is depleted by ATTACKxLOG(MAP_SIZE) - ARMOR amount. If
a unit's energy falls below 0, it is considered dead and is taken off the map.
Any moves that the unit made during the round are still carried out - so it
can finish a capture event or attack.

## end game

The game ends when only one AI owns all units and buildings or GAME_LENGTH
turns have passed. If the game ends when GAME_LENGTH turns have passed, it is
considered a draw.

