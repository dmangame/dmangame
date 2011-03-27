DMANGAME
--------

##Download##

You can find the latest version of the source code on [github][]

[github]:http://github.com/okayzed/dmangame

##Playing##

Run:

    # Run with graphics (you probably want this)
    python main.py ai/captureai.py ai/killncapture.py

    # Run without graphics
    python main.py ai/capture.ai ai/killncapture.py -c

    # Run on a specific map
    python main.py ai/capture.ai ai/killncapture.py -m maps/micro.py

    # Run with any number of AIs
    python main.py ai/capture.ai ai/killncapture.py ai/sharkai.py ai/basepatroller.py

    # Help
    python main.py --help


##Purpose##

To write an AI that competes against other AIs in a relatively simple world.
The overall objective is to crush your enemies, see them driven before you, and
to hear the lamentation of their pixels.

##Game Play##

You write an AI that is responsible for controlling a team of
units. Your AI should subclass ai.AI and can implement three functions:

    def _init(self):
    def _new_unit(self, unit):
    def _spin(self):

_init() is called when the AI is first created. Every turn of
the game world, _spin() is called. During this time, the AI
should interact with its units and issue commands. Whenever a
unit is spawned by a building, its AI is notified via the
_new_unit(unit) call.

You can interact with your units via the properties defined
in ai.AI (ai/base.py). For example, you can have all your
units move to the top left of the world with:

    for unit in self.units:
        unit.move((0,0))

or list which squares you can see, your visible enemies or which buildings are currently in view.

    print self.visible_enemies
    print self.visible_squares
    print self.visible_buildings



The game starts out with one building per AI. Each AI is then initialized with
a call to _init(), and the game world starts running. On the first turn of the
game, each building spawns a unit. Every UNIT_SPAWN_MOD (as defined in the map)
turns, the buildings spawn a unit of whichever AI happens to be controlling
them.

The end objective is to capture all enemy buildings and kill all enemy units.
Every unit is capable of shooting towards a square, moving towards a square or
capturing a building (If they are on the same square as a building).

### A simple example AI###

    import ai
    AIClass="SimpleAI"
    class SimpleAI(ai.AI):
        def _init(self):
          print self.currentTurn

        def _spin(self):
          print self.my_units
          print self.visible_enemies

        def _new_unit(self, unit):
          print "Received a new unit: %s" % unit


This AI just prints world information as it turns. You'll notice that it dies
very quickly, since it just stands there.

To run it, try:

    python main.py ai/simpleai.py ai/captureai.py

### Building a more defensive AI: ###


    import ai
    import random
    AIClass="TowerAI"
    class TowerAI(ai.AI):
      def _init(self):
        self.moved_once = set()

      def _spin(self):
        for unit in self.my_units:
          if unit.visible_enemies:
            unit.shoot(unit.visible_enemies[0].position)
          else:
            if not unit in self.moved_once:
              unit.move((random.randint(0, self.mapsize),
                         random.randint(0, self.mapsize)))
              self.moved_once.add(unit)

This AI is slightly smarter - for each unit, it picks a spot on the map and
moves the unit there. If it arrives there without issue, it will stop moving
and attack anything that comes near it.

If the unit notices an enemy unit on the way there, it'll start attacking. The
attack stops the unit's movement, and the unit will sit at that location. (and
not continue to its final destination).

    python main.py ai/towerai.py ai/captureai.py

## Game Mechanics ##

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

##Unit API##

The most up to date API information is in unit.py

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
  this initiates a capture of the building if the unit is occupying the same
  square as the building.  For a capture to happen successfully, the Unit must
  stay in the building for a length of time after initiating the capture.


## AI API ##

See ai/base.py for the available AI functions, and look in ai/ for more example AIs.


See Also:
---------
I've been a fan of AI based games for a while, such as the [Google AI
Challenge][g_src] and the [Queue ICPC Challenge][i_src]. They are fun and challenging
(could you tell from their titles?)
[g_src]: http://ai-contest.com
[i_src]: http://queue.acm.org/icpc/

