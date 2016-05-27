---
title: introduction
layout: default
---

## about

dmangame is about writing an AI to play a simplified Realtime Strategy Game.
There is no 'playing' done by humans, the game is played by various AI. Each
AI controls a team of units that it is able to communicate with. The AI's
objective is to crush its enemies and hear the lamentation of their pixels.

Your objective is to code this AI.

## pics or stfu

Here's [an example game][1] (saved using the -o option).

The little moving dots inside transparent circles are units. The circle is the
unit's field of vision. The line behind the unit is its path from their
location on the previous turn. Sometimes they shoot bullets (the slightly
thinner line) towards other units.

The stationary black outlined dots are buildings. Notice how buildings spawn
units at the same time.

## gimme

You can find the latest version of the source code on [github][2].

    git clone git://github.com/dmangame/dmangame.git

## dependencies ##

### required: ###

python 2.x

### optional: ###

If using graphics, pygtk (which should include cairo).

If posting to app engine, pyyaml

## running it


{% highlight bash %}

# Play with realtime graphics
python main.py ai/captureai.py ai/killncapture.py

# Play without realtime graphics and save a web replay.
# Open output.html to view the game replay.
# NOTE: This file is a massive JSON crusty file.
# If you want to copy it somewhere, make sure to
# compress it (scp -C) or gzip it first.
python main.py ai/capture.ai ai/killncapture.py -c -o output.html

# Use NCURSES GUI (Game output gets saved to
# game.log and game.out)
python main.py ai/capture.ai ai/killncapture.py -cn

# Play on a specific map
python main.py ai/capture.ai ai/killncapture.py -m maps/micro.py

# Show AI debug highlighting for AIs.
# Note: Each AI must have --hl before it to enable highlighting.
# See the Debugging section for more information.
# In this instance, only simpleAI gets highlighting.
python main.py --hl ai/simpleai.py ai/basepatroller.py

# Help
python main.py --help

{% endhighlight %}

## game it end?

   [1]: http://dmangame.github.io/dmangame/circleblaster_vs_expand.html
   [2]: http://github.com/dmangame/dmangame
   [3]: http://dmangame-hrd.appspot.com

