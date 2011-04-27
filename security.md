---
title: security
layout: default
---

## Security

There are two parts to the security in this game. First, an AI is only allowed
to control its own units. Meaning, a unit can only be given orders by the AI
that owns it. The other half of the security is releasing information to each
AI only as the AI becomes aware of it. Specifically, an AI should only be able
to examine objects that are currently visible to its units. Using
introspection and frame crawling, the code does a basic verification on each
AI.

However, the game is implemented in python and all the AIs run in the same
process, so it is possible for an AI to work around the security measures in
the game to gain access to more information than it should have or control
another AIs unit.

I've briefly looked at a few ideas, but it comes down to this: a process in
memory can not adequately protect itself from its own code. For there to be
any semblance of security, the world and each AI would have to run in its own
process. That would add complexity and performance overhead that I am not
interested in dealing with at the moment.

