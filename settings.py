# IMPORTANT: all SETTINGS that eventually end up in this file
# through code must also be defined here from the beginning,
# because this is a 'reset' file, as well.


### ENGINE SETTINGS (SHOULDNT BE USABLE BY AI)
MAP_NAME="maps/micro.py"
SINGLE_THREAD=False
IGNORE_EXCEPTIONS=False
PROFILE=False
PROFILE_AI=False
NCURSES=False

# Set of AI classes to show map debugging information for.
SHOW_HIGHLIGHTS=set()

JS_REPLAY_FILENAME=None
JS_REPLAY_FILE=None
END_GAME_TURNS=100
FPS=10

GAME_LENGTH=10000

# If you want to host your own app engine dev environment, you can run:
# python /path/to/google_appengine/dev_appserver.py aigame/
# and then set the below to True, which will cause appengine
# calls to go to localhost:8080
APPENGINE_LOCAL = False
TOURNAMENT = False

LOADED_AI_MODULES=set()

# In GUI mode this variable controls how large the buffer of stored turned to
# save is - these are precalculated frames that are then later displayed.
# In CLI mode, this variable controls how often the game state is saved to
# file in order to conserve RAM.
# WARNING: the buffer size needs to be the minimum amount of
# turns needed to see a unit fire a bullet. 
BUFFER_SIZE=250


# Import local settings
try:
    from local_settings import *
except: pass
