DMANGAME
--------

##Download##

You can find the latest version of the source code on [github][]

[github]:http://github.com/okayzed/dmangame

## What is it? ##

Briefly, dmangame is about writing an AI to play a simplified Realtime Strategy
Game.  There is no 'playing' done by humans, the game is played by various AI.
Each AI controls a team of units that it is able to communicate with.  The AI's
objective is to crush its enemies and hear the lamentation of their pixels.

Your objective is to code this AI.

## What it looks like ##

Here's [an example game][replay] (saved using the -o option).

[replay]:http://okayzed.github.com/dmangame/circleblaster_vs_expand.html

The little moving dots inside transparent circles are units. The circle is the
unit's field of vision.  The line behind the unit is its path from their
location on the previous turn. Sometimes they shoot bullets (the slightly
thinner line) towards other units.

The stationary black outlined dots are buildings. Notice how buildings spawn
units at the same time.

## Dependencies ##

If using graphics, pygtk (which should include cairo).

If not, then just python.

## Playing ##

    # Play with graphics
    python main.py ai/captureai.py ai/killncapture.py

    # Play without graphics and a web replay. Open output.html to view the game replay.
    # NOTE: This file is a massive JSON crusty file. If you want to copy it
    # somewhere, make sure to compress it (scp -C) or gzip it first.
    python main.py ai/capture.ai ai/killncapture.py -c -o output.html

    # Use NCURSES GUI (Game output gets saved to game.log and game.out)
    python main.py ai/capture.ai ai/killncapture.py -cn

    # Play on a specific map
    python main.py ai/capture.ai ai/killncapture.py -m maps/micro.py

    # Show AI debug highlighting for AIs.
    # Note: Each AI must have --hl before it to enable highlighting. See the
    # Debugging section for more information.
    # In this instance, only simpleAI gets highlighting.
    python main.py --hl ai/simpleai.py ai/basepatroller.py

    # Help
    python main.py --help

## Game Mechanics ##

Note: upper case words are variables defined in settings.py or a map with the -m option.

### World ###
The world is a 2dimensional square that is MAP\_SIZExMAP\_SIZE. There are 3 main
objects that exist in the game world: units, buildings and bullets.

### Units ###

The only object that the AIs can command are units. Each unit has an AI that it
belongs to and it will only accept commands from that AI. These units have 3
abilities: moving, shooting and capturing.  Additionally, every unit is able to
see its surroundings and report them back to its AI. The units have energy and
when that falls to zero, they die. The only way to acquire more units is through
buildings.

### Buildings ###

Buildings are stationary objects that spawn a new Unit every UNIT\_SPAWN\_MOD
turns for the AI that owns the Building. A building can be captured by another
AI through its units. To capture a building, a unit must step inside it and
begin capturing. If the unit can stay there for CAPTURE\_LENGTH turns without
shooting or moving, the base will change ownership to that unit's AI.

### Moving ###
An AI may tell a unit to move to any square on the map. The unit will move
forward SPEED\_MODIFIER*LOG(MAP\_SIZE) squares along the shortest possible route
to the square until it arrives or another directive is issued.

If the square is invalid, an exception will be raised.

### Collisions ###

If two or more AI teams have units that occupy the same square during a turn,
the units collide with each other. All teams then lose the amount of the second
greatest number of units on the square.


### Attacking ###
When a unit attacks, they shoot towards a square that they want to hit.  The
bullet travels at about MAP\_SIZE/BULLET\_SPEED\_MODIFIER units a turn, while their
full range is MAP\_SIZE/BULLET\_RANGE\_MODIFIER units. Any unit who falls within
the path of a bullet will take damage (including allies).

### Damage ###

When a bullet goes through the same square that a unit is moving through on a
turn, the unit's energy is depleted by ATTACK*LOG(MAP\_SIZE) - ARMOR amount. If a
unit's energy falls below 0, it is considered dead and is taken off the map.
Any moves that the unit made during the round are still carried out - so it can
finish a capture event or attack.

### End game ###

The game ends when only one AI owns all units and buildings or GAME\_LENGTH turns
have passed.  If the game ends when GAME\_LENGTH turns have passed, it is
considered a draw.

##Writing an AI##

You write an AI that is responsible for controlling a team of
units. Your AI should subclass ai.AI and can implement four
functions:

    def _init(self):
    def _unit_spawned(self, unit):
    def _unit_died(self, unit):
    def _spin(self):

\_init() is called when the AI is first created. Every turn of
the game world, \_spin() is called. During this time, the AI
should interact with its units and issue commands. Whenever a
unit is spawned by a building, its AI is notified via the
\_unit\_spawned(unit) call. Whenever a unit dies, the AI is notified via a \_unit\_died(unit) call.

NOTE: During unit\_spawned and unit\_died, the unit will not have proper
visibility and should not really interact with the game world - just with the
AI internal bookkeeping.

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
a call to \_init(), and the game world starts running. On the first turn of the
game, each building spawns a unit. Every UNIT\_SPAWN\_MOD (as defined in the map)
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

        def _unit_died(self, died):
          print "Lost a unit: %s" % unit

        def _unit_spawned(self, unit):
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

### More AIs ###

The [dmanai][d_src] repository contains AIs for dmangame.
[d_src]:http://github.com/okayzed/dmanai


#### Playing with AIs from dmanai ####

    cd dmangame/
    git clone git://github.com/okayzed/dmanai.git
    python main.py dmanai/okay/rushai.py dmanai/bob/expand-then-search.py dmanai/okay/gooseai.py



## API ##

See ai/base.py for the available AI functions, and look in ai/ for more example AIs.

The easiest way to see the documentation is to run `pydoc -p
8000` and browse to the [ai docs][] or [unit docs][].

[ai docs]:http://localhost:8000/ai.base.html
[unit docs]:http://localhost:8000/unit.html

If you don't care for \_unit\_died and \_unit\_spawned (or want
to do your own book keeping), you can subclass from ai.BareAI
- in which case you need to implement the following two
  functions:

    def turn(self)
    def init(self)

## Debugging ##

### Exceptions ###

When writing an AI, you probably want to find out whenever your AI throws an
exception. When running the game normally, each AI runs in its own thread of
execution. When an AI throws an exception, its in that thread, so the game will
continue to run after an AI throws an exception. The exception and its
traceback will be printed to screen. You can log the game output with:

    python main.py ai/simpleai.py > game.log 2>&1

Alternatively, if the game is run with the -p option (profiling), gameplay will
stop when an AI throws an exception. This is because profiling requires that
the execution stays single threaded in order to profile each AI more
accurately.

### Highlighting the map ###

There are three functions in ai.AI for printing debug information on the map.

    def highlightLine(self, start, end)
    def highlightRegion(self, start, end=None)
    def clearHighlights(self)

The AI can paint a line, a square or a region onto the map using these. The
objects will stay persistent from turn to turn until the AI calls
clearHighlights(), so an AI can accumulate more and more information on the
map.

In order to see the highlights from a given AI, use the --hl option before the AI's name when loading it:

    python main.py --hl ai/simpleai.py

This tells the game that you want to see what this AI is printing on the
screen. The debug information will be visible in the GUI and in the web replay.


## Security ##

There are two parts to the security in this game. First, an AI is only allowed
to control its own units. Meaning, a unit can only be given orders by the AI
that owns it. The other half of the security is releasing information to each
AI only as the AI becomes aware of it.  Specifically, an AI should only be able
to examine objects that are currently visible to its units. Using introspection
and frame crawling, the code does a basic verification on each AI.

However, the game is implemented in python and all the AIs run in the same
process, so it is possible for an AI to work around the security measures in
the game to gain access to more information than it should have or control
another AIs unit.

I've briefly looked at a few ideas, but it comes down to this: a process in
memory can not adequately protect itself from its own code. For there to be any
semblance of security, the world and each AI would have to run in its own
process. That would add complexity and performance overhead that I am not
interested in dealing with at the moment.

See Also:
---------
I've been a fan of AI based games for a while, such as the [Google AI
Challenge][g_src] and the [Queue ICPC Challenge][i_src]. They are fun and challenging
(could you tell from their titles?)
[g_src]: http://ai-contest.com
[i_src]: http://queue.acm.org/icpc/

