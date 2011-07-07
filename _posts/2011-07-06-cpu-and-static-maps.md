---
layout: post
title: Post-June updates
author: okay
---

#### On github

A new AI has appeared in the ladder, welcome [OliAI2][0]. OliAI2 is built on a
squad based strategy, allowing for better coordination among subsets of units.
Cool stuff :-)

[0]: https://github.com/Aureus/dmanai/blob/master/aure/aureai.py

#### at pyclass

This coming monday, (july 11th), dmangame will once again be at pyclass. This
week, we'll go over a basic AI strategy. Or to put it another way: how does one
go from nothing to having an AI with some semblance of a strategy.

#### ranking system changes

If you've been following the ladder, you may have noticed that the rankings are
volatile. We've been speculating as to possible reasons: one reason for this is
that the maps have too much variance in the base positioning... it's possible
for an AI to get sandwiched or put in a bad place. In order to prevent this, we
are moving to more static maps, with the help of behindcurtain3.  While working
on this, behindcurtain3 raised the point that having a variable number of
players per map can lead to confusion about the strength of an AI.

Supplanting macro, micro and village will be static maps with a set number of
players. Hopefully the rankings on these maps will settle more, since the
number of players per map is fixed. In addition, the overall ranking will be an
average of the AIs ratings on each map, leading to more stable overall results.

#### Deadlining AIs

Also related to appengine, the appengine instance went over quota yesterday.
Since there isn't a good way of getting access to the quota programatically, it
becomes somewhat harder to run matches and host the server on the same
appengine instance, without running into resource usage issues.

Since it can't be prevented, I've put in place a system for marking when an AI
hits the deadline. If the execution expires on a game and an AI is responsible
for more than 90% of the runtime, it will be marked as faulting. If an AI
faults 10 times, it will get disabled temporarily and a notice will be sent to
the author.
