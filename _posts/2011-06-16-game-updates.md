---
layout: post
title: github, your issue system is pretty good.
author: okay
---

There has been some good discussion on github, which prompted a bunch of
updates. if you have any feature requests, ideas or whatever - open an issue
on github - it'll get looked at. i promise.

#### game mechanics

the capture mechanics have been adjusted, recently - now buildings spawn units
UNIT_CAPTURE_LENGTH turns after the building has changed owners.

#### developer updates

two updates have been added to help AI developers make assumptions and speed up
their code. , game settings are now passed to each AI and are available in the
'settings' object.

    print settings
    print settings.map
    print settings.map.size

`--profile` now saves per AI profiling information, so if you think your AI
is going slow - now you know.

    # Saves a profile to "%s.prof" % killncapture.AI_CLASS which would be
    # ./KillNCapture.prof
    python main.py ai/killncapture.py --profile

finally, the default for github hosted AI is to run in safemode using
safelite, so if you are writing an AI, try not to import sys or os. I know it
may issue warnings about modules being loaded via require_dependency - that is
being looked into.

#### user submissions

[behindcurtain3][3] has submitted the [warzone][4] map - it's a fast paced
close combat map with lots of damage and unit spawning.


[3]: http://github.com/behindcurtain3/dmanai
[4]: https://github.com/dmangame/dmangame/blob/master/maps/warzone.py
