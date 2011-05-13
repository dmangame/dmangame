# IMPORTANT: all SETTINGS that eventually end up in this file
# through code must also be defined here from the beginning,
# because this is a 'reset' file, as well.

# MAP MODIFIERS
MAP_SIZE=100
MAP_NAME="default"
ADDITIONAL_BUILDINGS=0
ADDITIONAL_BUILDINGS_PER_AI=0

# BUILDING MODIFIERS
CAPTURE_LENGTH=3
UNIT_SPAWN_MOD=CAPTURE_LENGTH*10

# STAT MODIFIERS
ARMOR_MODIFIER       = 1
ATTACK_MODIFIER      = 0.5
ENERGY_MODIFIER      = 10
SIGHT_MODIFIER       = 1
SPEED_MODIFIER       = 1
BULLET_RANGE_MODIFIER = 8
BULLET_SPEED_MODIFIER = 10

SAVE_IMAGES=False
SINGLE_THREAD=False
IGNORE_EXCEPTIONS=False
PROFILE=False
NCURSES=False

# Set of AI classes to show map debugging information for.
SHOW_HIGHLIGHTS=set()

BUILDING_SPAWN_DISTANCE=5
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
