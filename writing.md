---
title: Writing an AI
layout: default
---

## writing an AI

You write an AI that is responsible for controlling a team of units. Your AI
should subclass ai.AI and can implement four functions:


{% highlight python %}

    def _init(self):
    def _unit_spawned(self, unit):
    def _unit_died(self, unit):
    def _spin(self):

{% endhighlight %}

\_init() is called when the AI is first created. Every turn of the game world,
\_spin() is called. During this time, the AI should interact with its units and
issue commands. Whenever a unit is spawned by a building, its AI is notified
via the \_unit\_spawned(unit) call. Whenever a unit dies, the AI is notified via
a \_unit\_died(unit) call.

You can interact with your units via the properties defined in ai.AI
(ai/base.py). For example, you can have all your units move to the top left of
the world with:



{% highlight python %}
    for unit in self.units:
      unit.move((0,0))
{% endhighlight %}


or list which squares you can see, your visible enemies or which buildings are
currently in view.



{% highlight python %}
    print self.visible_enemies
    print self.visible_squares
    print self.visible_buildings
{% endhighlight %}


The game starts out with one building per AI. Each AI is then initialized with
a call to \_init(), and the game world starts running. On the first turn of the
game, each building spawns a unit. Every UNIT\_SPAWN\_MOD (as defined in the
map) turns, the buildings spawn a unit of whichever AI happens to be
controlling them.

The end objective is to capture all enemy buildings and kill all enemy units.
Every unit is capable of shooting towards a square, moving towards a square or
capturing a building (If they are on the same square as a building).

### a simple example AI



{% highlight python %}

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


{% endhighlight %}

This AI just prints world information as it turns. You'll notice that it dies
very quickly, since it just stands there.

To run it, try:



    python main.py ai/simpleai.py ai/captureai.py


### building a more defensive AI:



{% highlight python %}
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

{% endhighlight %}

This AI is slightly smarter - for each unit, it picks a spot on the map and
moves the unit there. If it arrives there without issue, it will stop moving
and attack anything that comes near it.

If the unit notices an enemy unit on the way there, it'll start attacking. The
attack stops the unit's movement, and the unit will sit at that location. (and
not continue to its final destination).



    python main.py ai/towerai.py ai/captureai.py


