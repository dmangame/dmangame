---
title: strategy
layout: default
---

##class AI(BareAI)##


###Methods###

####init(self, \*args, kwargs)####

####turn(self)####
calls into the \_spin, \_init, \_unit_spawned and \_unit\_died methods of
the implemented AI.

* * *

Methods inherited from BareAI:

####clearHighlights(self)####
Clear all highlighted areas by the AI on the map

####highlightLine(self, start, end)####
Adds a highlight line to the map from start to end

####highlightRegion(self, start, end=None)####
Adds a highlight region to the map from start to end


###Properties###
Data descriptors inherited from BareAI:


####ai_id####
the AI's private ID, it's used by the worldtalker for identification
purposes.

####current_turn####
the world's current iteration

####dead_units####
all units that died the past turn for this AI instance.

####lost_buildings####
all buildings that were lost this past turn by this AI instance.

####my_buildings####
all buildings that belong to this AI instance

####my_units####
living units that belong to this AI instance

####new_buildings####
all buildings that were captured the past turn by this AI instance.

####new_units####
all units that were spawned this turn for this AI instance

####score####
the AI's current score

####team####
the team of this AI instance

####visible_buildings####
all visible buildings

####visible_enemies####
all visible enemy units to the AI

####visible_squares####
all visible squares to the AI (the set of all squares visible to the AI's units)
