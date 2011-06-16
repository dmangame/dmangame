---
title: AI Modules
layout: default
---

## the AI module

Each AI lives in a python module. AI modules execute in the python
environment, with a few modifications (See the notes below). After the modules
are passed to the engine from command line, the game engine loads the module.
It then looks to the module variable AIClass for the name of your AI.

Once the engine knows the class name, it loads the class from the ai module.
Once the AIs are collected, they are instantiated and passed to the world. The
world then takes care of calling each AI's functions every turn.

### notes

#### settings

There is a global, `settings`, that is exposed to each AI that contains
information about the game state. The data contained in it is calculated by
the world based on map size and other factors specified in the map settings file.

    # prints information about the world state and what settings are
    # available.
    print settings

#### dependencies

The AI module comes with a dependency loader that will automatically import
required modules from github or local filesystem depending on where the AI was
loaded from. This is used on app engine, so ladder matches are always pulling
the latest code from github.

    # will add another_module to the current namespace, it acts like
    # 'import another_module'
    require_dependency("another_module")

#### keywords

Because the game has to run on python 2.5 (using appengine), there are a few
keywords (for example next()) missing. To account for this, dmangame manually
injects python keywords into the AI scope. If a keyword is missing, feel free
to open an issue on github or fix it yourself and let me know.

#### restricted modules

By default, AIs loaded via the remote AI are run in restricted mode. This means
that only a subset of modules are allowed to be loaded and writes to the file
system are restricted. If you are writing an AI, don't load sys or os if you
want other people to run your AI.

This also restricts which builtins are callable - if you are calling a builtin
and it fails, it's probably because someone thought it was unsafe.  (for
example, compile())

#### ai.BareAI

If you don't care for \_unit\_died and \_unit\_spawned (or want to do your own
book keeping), you can subclass from ai.BareAI - in which case you need to
implement the following two functions:


{% highlight python %}
    def turn(self):
    def init(self):
{% endhighlight %}

