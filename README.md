DMANGAME
--------

## Website ##

check the [dmangame page][] for more information.

[dmangame page]:http://okayzed.github.com/dmangame

## Download ##

You can find the latest version of the source code on [github][]

[github]:http://github.com/okayzed/dmangame

## Dependencies ##

If using graphics, pygtk (which should include cairo).

If not, then just python.

## Playing ##

    # Play with graphics
    python main.py ai/captureai.py ai/killncapture.py

    # Play without graphics and a web replay. Open output.html to view the game replay.
    # NOTE: This file is a massive JSON crusty file. If you want to copy it
    # somewhere, make sure to compress it (scp -C) or gzip it first.
    python main.py ai/capture.ai ai/killncapture.py -c -o output.html

    # Use NCURSES GUI (Game output gets saved to game.log and game.out)
    python main.py ai/capture.ai ai/killncapture.py -cn

    # Play on a specific map
    python main.py ai/capture.ai ai/killncapture.py -m maps/micro.py

    # Show AI debug highlighting for AIs.
    # Note: Each AI must have --hl before it to enable highlighting. See the
    # Debugging section for more information.
    # In this instance, only simpleAI gets highlighting.
    python main.py --hl ai/simpleai.py ai/basepatroller.py

    # Help
    python main.py --help

    # Run game via appengine. The app engine server is specified in # app.yaml.
    # By default, it will hit dmangame-app.appspot.com, which
    # will have the version of the code in github + the latest dmanai/ available.
    # Note: You should need to set APPENGINE_LOCAL to False for this to work

    # The results should get posted to
    # http://dmangame-app.appspot.com
    python main.py dmanai/okay/rushai.py dmanai/bob/expand-then-search.py -m maps/macro.py --app-engine

See Also:
---------
I've been a fan of AI based games for a while, such as the [Google AI
Challenge][g_src] and the [Queue ICPC Challenge][i_src]. They are fun and challenging
(could you tell from their titles?)
[g_src]: http://ai-contest.com
[i_src]: http://queue.acm.org/icpc/

