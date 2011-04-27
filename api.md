---
title: API
layout: default
---

## API

See ai/base.py for the available AI functions, and look in ai/ for more
example AIs.

The easiest way to see the documentation is to run `pydoc -p 8000` and browse
to the [ai docs][1] or [unit docs][2].

If you don't care for _unit_died and _unit_spawned (or want to do your own
book keeping), you can subclass from ai.BareAI - in which case you need to
implement the following two functions:


{% highlight python %}
    def turn(self):
    def init(self):
{% endhighlight %}

   [1]: http://localhost:8000/ai.base.html
   [2]: http://localhost:8000/unit.html

