---
title: More AIs
layout: default
---

## more ais

The [dmanai][1] repository contains AIs for dmangame.

### playing with AIs from dmanai


{% highlight bash %}

    cd dmangame/
    git clone git://github.com/okayzed/dmanai.git
    python main.py dmanai/okay/rushai.py \
               dmanai/bob/expand-then-search.py \
               dmanai/okay/goose.py

{% endhighlight %}


### submitting your own AI to dmanai

If you want to run your AI on the dmangame app engine
instance, or just want your AI to be available for others:

 * 1) fork ([github help for fork][2]) the [dmanai repository][1].
 * 2) add your AI into a subdirectory of the main repository with a unique username. for example: dmanai/okay/rushai.py
 * 3) submit a pull request ([github help for pull requests][3]) to the dmanai repository


[1]: http://github.com/okayzed/dmanai
[2]: http://help.github.com/fork-a-repo/
[3]: http://help.github.com/pull-requests/
