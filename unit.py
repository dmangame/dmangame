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
        self.__unit_id = next(Unit.ID_GENERATOR)

    def getUnitID(self):
      return self.__unit_id
    unit_id = property(getUnitID)

    # Some functions the unit has access to.  The way it will
    # use all these functions is by asking the worldtalker to
    # do all teh dirty business.

    # Properties
    def getPosition(self):
        " Returns the position of this Unit on the map"
        return self.__wt.getPosition(self)
    position = property(getPosition)

    def isAlive(self):
        " Returns if this unit is alive or not in the world"
        return self.__wt.isAlive(self)
    is_alive = property(isAlive)

    def isCapturing(self):
        " Returns if this unit is currently capturing a building "
        return self.__wt.isCapturing(self)
    is_capturing = property(isCapturing)


    def isMoving(self):
        " Returns if this unit is currently moving."
        return self.__wt.isMoving(self)
    is_moving = property(isMoving)

    def isShooting(self):
        " Returns if this unit is shooting"
        return self.__wt.isShooting(self)
    is_shooting = property(isShooting)

    def isUnderAttack(self):
        " Returns if this unit is under attack"
        return self.__wt.isUnderAttack(self)
    is_under_attack = property(isUnderAttack)

    def getArmor(self):
        "The armor of the unit, represents the damage this unit absorbs when it gets shot by a bullet."
        return self.__wt.getArmor(self)
    armor = property(getArmor)

    def getAttack(self):
        "The attack of the unit, represents the damage this unit does with its bullets."
        return self.__wt.getAttack(self)
    attack = property(getAttack)

    def getEnergy(self):
        "The energy of the unit, represents the health of the unit"
        return self.__wt.getStats(self).energy
    energy = property(getEnergy)

    def getSight(self):
        "The sight of the unit, use: sight as R of unit"
        return self.__wt.getSight(self)
    sight = property(getSight)

    def getSpeed(self):
        "The speed of the unit - the number of units distance the unit can travel in one turn."
        return self.__wt.getSpeed(self)
    speed = property(getSpeed)

    def getTeam(self):
        " The owner of the unit (an ai_id) "
        return self.__wt.getTeam(self)
    team = property(getTeam)

    def getVisibleSquares(self):
        "Return all squares that are in the range of sight of this unit"
        return self.__wt.getVisibleSquares(self)
    visible_squares = property(getVisibleSquares)

    def getVisibleBuildings(self):
        "Return all buildings that are in the range of sight of this unit"
        return self.__wt.getVisibleBuildings(self)
    visible_buildings = property(getVisibleBuildings)

    def getVisibleEnemies(self):
        "Return all enemy units that are in the range of sight of this unit"
        # Returns all (enemy?) units in shooting range
        return self.__wt.getVisibleEnemies(self)
    visible_enemies = property(getVisibleEnemies)

    def getInRangeEnemies(self):
        """
        Returns all hittable enemy units to the AI
        """
        return self.__wt.inRange(self)
    in_range_enemies = property(getInRangeEnemies)

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
        "If the unit shot at target square, who would be hit?"
        return self.__wt.calcVictims(self, target_square)

    # Main actions
    def capture(self, b):
        """
        this initiates a capture of the building if the unit
        is occuping the same square as the building.  For a
        capture to happen successfully, the Unit must stay in
        the building for CAPTURE_LENGTH time after initiating
        the capture.
        """
        return self.__wt.capture(self, b)

    def move(self, (x,y)):
        """
        this will move the unit towards (x,y) by their speed
        amount in this round. You can continually call
        unit.move(dest) until the unit arrives there.
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

