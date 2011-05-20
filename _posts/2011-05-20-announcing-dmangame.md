---
layout: post
title: dmangame on reddit & remote AI
author: okay
---

it took a while and some encouragement, but after asking
around for good some good places to get players and feedback
for dmangame, i decided to post on reddit. twice, actually - once in [/r/programming][0] and again in [/r/Python][1].

the comments were positive and i'm hoping to see some cool AI
soon. two issues brought up, that i'd like to address are:


 * why does the AI know the dimension of the map to start with?

*it does make more sense for that information to be left out, since the AI is theoretically being dropped into the map.*

*currently, the map size is given to each AI due to the ease
of implementation, both for the game and for the player
writing an AI.*


 * how does multiplayer work? and what does it mean in the context of a game about writing AI

*to me, multiplayer in a game about writing code would be the
ability to run other user's code. as a result, there's now
the ability to play against github hosted AI. An AI can be
loaded via any github fork of dmanai. See the section on [more
AI][2] for information.*

[0]: http://www.reddit.com/r/programming/comments/hdtta/dmangame_a_game_about_writing_game_ai_in_python/
[1]: http://www.reddit.com/r/Python/comments/hdqw7/dmangame_a_game_about_writing_game_ai/
[2]: more_ais.html
