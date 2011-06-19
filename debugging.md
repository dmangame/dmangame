---
title: Debugging
layout: default
---

## debugging

Writing an AI is easy enough, but debugging an incorrectly functioning AI can
be a pain.

### exceptions

When writing an AI, you probably want to find out whenever your AI throws an
exception. When running the game normally, each AI runs in its own thread of
execution. When an AI throws an exception, its in that thread, so the game
will continue to run after an AI throws an exception. The exception will be
printed to screen. You can log the game output with:


    python main.py ai/simpleai.py > game.log 2>&1


Alternatively, if the game is run with the --profile option, gameplay will stop
when an AI throws an exception. This is because profiling requires that the
execution stays single threaded in order to profile each AI more accurately.

### highlighting the map

There are three functions in ai.AI for printing debug information on the map.



{% highlight python %}
    def highlightLine(self, start, end)
    def highlightRegion(self, start, end=None)
    def clearHighlights(self)
{% endhighlight %}


The AI can paint a line, a square or a region onto the map using these. The
objects will stay persistent from turn to turn until the AI calls
clearHighlights(), so an AI can accumulate more and more information on the
map.

In order to see the highlights from a given AI, use the --hl option before the
AI's name when loading it:



    python main.py --hl ai/simpleai.py


This tells the game that you want to see what this AI is printing on the
screen. The debug information will be visible in the GUI and in the web
replay.

