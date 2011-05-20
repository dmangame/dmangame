---
title: More AIs
layout: default
---

## more ais

The [dmanai][1] repository contains AIs for dmangame. If you'd
like your AI to be available for others to play against, fork
the dmanai repository on github.

### playing with AIs from dmanai

#### Using a github hosted AI

{% highlight bash %}
# To use a github hosted AI, the format of the AI argument
# should be
# github_user:path_to_dep1.py,path_to_dep2.py,path_to_ai.py
# This AI format is usable on app engine, as well, allowing
# for tournaments between remote AIs.

cd dmangame/
python main.py okayzed:okay/okay.py,okay/rushai.py \
okayzed:bob/expand-then-search.py
{% endhighlight %}

#### Cloning git locally

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
