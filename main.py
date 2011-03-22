#! /usr/bin/env python

import ai
import os
import world
import worldtalker

LIFESPAN = 10
if __name__ == "__main__":
    try:
        for file in os.listdir("ai"):
            print file
    except WindowsError, e:
        print "Couldn't find AI directory"


    w = world.World(LIFESPAN)
    wt = worldtalker.WorldTalker(w)
    AI = []
    AI.append(ai.AI(wt))

    stats = world.Stats()
    unit1 = wt.createUnit(stats)
    unit1.name = "goomba"
    w.map.placeObject(unit1, (1, 2))

    unit2 = wt.createUnit(stats)
    unit2.name = "koopa"
    w.map.placeObject(unit2, (5, 5))


    # Create AI
    for turn in xrange(w.getLifeSpan()):
        for ai in AI:
            print ""
            ai._spin()
#            try:
#                ai.spin()
#            except Exception, e:
#                print "AI raised exception %s, skipping this turn for it" % (e)

        w.Turn()
    print "Finished simulating the world, press Enter to exit"
    raw_input()
