import mapobject

def unit_id_generator():
  i = 0
  while True:
    yield i
    i += 1

class Unit(mapobject.MapObject):
    """
    Represents a Unit on the map. A Unit can move, shoot or capture for events, at the moment
    """
    # What can a unit do?
    # It can shoot, move and capture a square. Can two units occupy the same
    # square? I forget.

    ID_GENERATOR = unit_id_generator()

    def __init__(self, worldtalker, stats):
        self.__wt = worldtalker
        self.__stats = stats
        self.killer = set()
        self.__unit_id = Unit.ID_GENERATOR.next()

    @property
    def unit_id(self):
      return self.__unit_id

    # Some functions the unit has access to.  The way it will
    # use all these functions is by asking the worldtalker to
    # do all teh dirty business.

    # Properties

    @property
    def position(self):
        " the position of this Unit on the map"
        return self.__wt.getPosition(self)

    @property
    def is_alive(self):
        " if this unit is alive or not in the world"
        return self.__wt.isAlive(self)

    @property
    def is_capturing(self):
        " if this unit is currently capturing a building "
        return self.__wt.isCapturing(self)


    @property
    def is_moving(self):
        " if this unit is currently moving."
        return self.__wt.isMoving(self)

    @property
    def is_shooting(self):
        " if this unit is shooting"
        return self.__wt.isShooting(self)

    @property
    def is_under_attack(self):
        " if this unit is under attack"
        return self.__wt.isUnderAttack(self)

    @property
    def armor(self):
        "The armor of the unit, represents the damage this unit absorbs when it gets shot by a bullet."
        return self.__wt.getArmor(self)

    @property
    def attack(self):
        "The attack of the unit, represents the damage this unit does with its bullets."
        return self.__wt.getAttack(self)

    @property
    def energy(self):
        "The energy of the unit, represents the health of the unit"
        return self.__wt.getStats(self).energy

    @property
    def sight(self):
        "The sight of the unit, use: sight as R of unit"
        return self.__wt.getSight(self)

    @property
    def speed(self):
        "The speed of the unit - the number of units distance the unit can travel in one turn."
        return self.__wt.getSpeed(self)

    @property
    def team(self):
        " The owner of the unit (an ai_id) "
        return self.__wt.getTeam(self)

    @property
    def visible_squares(self):
        "all squares that are in the range of sight of this unit"
        return self.__wt.getVisibleSquares(self)

    @property
    def visible_buildings(self):
        "all buildings that are in the range of sight of this unit"
        return self.__wt.getVisibleBuildings(self)

    @property
    def visible_enemies(self):
        "all enemy units that are in the range of sight of this unit"
        # all (enemy?) units in shooting range
        return self.__wt.getVisibleEnemies(self)

    @property
    def in_range_enemies(self):
        """
        all enemy units that are within bullet distance of this unit.

        it may return enemies not visible to this unit if they are visible to
        another unit on the same team.
        """
        return self.__wt.inRange(self)

    def calcBulletPath(self, target_square):
        """
        Calculates the path a bullet takes to get from the
        unit's position to target_square
        """
        return self.__wt.calcBulletPath(self, target_square)

    def calcDistance(self, target_square):
        "Calculate distance from this unit to target square"
        return self.__wt.calcDistance(self, target_square)

    def calcUnitPath(self, target_square):
        "Calculate the path this unit would take to get to target square"
        return self.__wt.calcUnitPath(self, target_square)

    def calcVictims(self, target_square):
        """
        If the unit shot at target square, which units would be hit?

        Returns all visible units that would be hit by a bullet shot toward the
        destination (including own units and enemy units) if they were to not
        move until the bullet arrived.

        """
        return self.__wt.calcVictims(self, target_square)

    # Main actions
    def capture(self, b):
        """
        initiates a capture of building if the unit is occuping the same
        square as the building.  For a capture to happen successfully, the Unit
        must stay in the building for CAPTURE_LENGTH time after initiating the
        capture.
        """
        return self.__wt.capture(self, b)

    def move(self, (x,y)):
        """
        move the unit towards (x,y) by their speed amount in this round.

        if the unit doesn't receive a new order, it will continue moving to
        that square on subsequent turns until it arrives.

        it is also safe to continually call unit.move(dest) until the unit
        arrives there.
        """

        return self.__wt.move(self, (int(x), int(y)))

    def shoot(self, (x, y)):
        """
          shoot a bullet towards (x,y), even if (x,y) is not
          in range. The bullet will travel as far as it can
          go. Any units who are in the path of the bullet at
          the end of the round will take damage.
        """
        return self.__wt.shoot(self, (x, y))

