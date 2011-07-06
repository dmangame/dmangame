import ai
import random
import itertools
import time
from collections import defaultdict
AIClass = "TimeoutAI"

import logging
log = logging.getLogger(AIClass)

class TimeoutAI(ai.AI):
    PLAY_IN_LADDER=True
    def __init__(self, *args, **kwargs):
        ai.AI.__init__(self, *args, **kwargs)

    def _spin(self):
      while True:
        continue
