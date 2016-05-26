---
title: More AIs
layout: default
---

## sharing AIs

The [dmanai][1] repository contains sample AIs for dmangame.
If you'd like your AI to be available for others to play
against, fork the dmanai repository on github. The AI in your
fork are then available for others to play against.

### playing with AIs from dmanai

#### Using a github hosted AI

{% highlight bash %}
# To use a github hosted AI, the format of the AI argument
# should be
# github_user:path_to_ai.py
# This AI format is usable on app engine, as well, allowing
# for tournaments between remote AIs.

cd dmangame/
python main.py dmangame:okay/rushai.py \
dmangame:bob/expand-then-search.py
{% endhighlight %}

You can play against any forked AI this way, but the AI must
be in the master branch of the repository.

#### Cloning an AI repository locally

{% highlight bash %}
cd dmangame/
git clone git://github.com/dmangame/dmanai.git
python main.py dmanai/okay/rushai.py \
           dmanai/bob/expand-then-search.py \
           dmanai/okay/goose.py

{% endhighlight %}

### submitting your own AI to dmanai

If you want to run your AI on the dmangame app engine
instance, or just want your AI to be available for others:

 * 1) fork ([github help for fork][2]) the [dmanai repository][1].
 * 2) add your AI into a subdirectory of the main repository with a unique username. for example: dmanai/okay/rushai.py
 * 3) \[optional\] register it to play in app engine ladder games: `python main.py -r github_username:path_to_ai.py`

At this point, anyone can browse the [dmanai member graph][3] and look at what
others are developing.

[1]: http://github.com/dmangame/dmanai
[2]: http://help.github.com/fork-a-repo/
[3]: https://github.com/dmangame/dmanai/network/members
