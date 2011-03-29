# A map class, responsible for map functions, like
# finding the square a unit is on or what occupies a square
import ai
import mapobject
import math
import random
import logging
import settings
from unit import Unit

log = logging.getLogger("MAP")


def draw_map(cairo_context, width, height, world):

  surface = cairo_context.get_target()

  deltax = float(width)/world.mapSize
  deltay = float(height)/world.mapSize
  cairo_context.set_source_rgb(1, 1, 1)
  cairo_context.rectangle(0, 0, width, height)
  cairo_context.fill()
  cairo_context.set_source_rgb(0,0,0)
  cairo_context.set_line_width(1.0)

  #self.draw_grid(cairo_context)

#       Draw the squares a unit sees ( using circle) in a really light unit color.
#
  # try getting the color from our color dictionary.

  AI = world.AI

  for unit in world.units:
      stats = world.units[unit]
      team = stats.team
      color = ai.AI_COLORS[team]

  for unit in world.melees:
      team = unit.team
      color = ai.AI_COLORS[team]
      x, y = world.melees[unit]
      cairo_context.set_source_rgb(*color)
      cairo_context.rectangle(deltax*x-(deltax), deltay*y-(deltay), 4*deltax, 4*deltay)
      cairo_context.fill()

  for building in world.buildings:
      try:
        x, y = world.map.getPosition(building)
        cairo_context.set_source_rgb(0,0,0)
        cairo_context.rectangle(deltax*x-(deltax/2), deltay*y-(deltay/2), 2*deltax, 2*deltay)
        cairo_context.fill()
      except TypeError:
        pass

  for unit in world.units:
      stats = world.units[unit]
      x, y = world.map.getPosition(unit)
      color = ai.AI_COLORS[stats.team]
      color = (color[0], color[1], color[2], .15)
      cairo_context.set_source_rgba(*color)
      cairo_context.arc(deltax*x, deltay*y, (stats.sight)*deltax, 0, 360.0)
      cairo_context.fill()

  # Draw the unit paths
  for unit in world.unitpaths:
      path = world.unitpaths[unit]
      team = world.units[unit].team
      color = map(lambda x: x/2.0, ai.AI_COLORS[team])
      cairo_context.set_source_rgb(*color)
      for x,y in path:
          cairo_context.rectangle(deltax*x, deltay*y, deltax, deltay)
          cairo_context.fill()

  # Draw the bullet paths
  cairo_context.set_source_rgb(.75, .75, .75)
  for unit in world.bulletpaths:
      for path in world.bulletpaths[unit]:
          for x,y in path:
              cairo_context.rectangle(deltax*x, deltay*y, deltax, deltay)
              cairo_context.fill()

  # Draw the mapobjects in different colors (based on whether it is a bullet or unit)
  for unit in world.map.getAllObjects():
      x,y = world.map.getPosition(unit)
      if unit.__class__ == Unit:
          team = world.units[unit].team
          color = ai.AI_COLORS[team]
          cairo_context.set_source_rgb(*color)
      elif unit.__class__ == mapobject.Bullet:
          cairo_context.set_source_rgb(0, 0, 0)
      elif unit.__class__ == mapobject.Building:
          team = unit.team
          if team in ai.AI_COLORS:
              color = ai.AI_COLORS[team]
              cairo_context.set_source_rgb(*color)
          else:
              cairo_context.set_source_rgb(0.2,0.2,0.2)
      else:
          cairo_context.set_source_rgb(0,0,0)
      cairo_context.rectangle(deltax*x, deltay*y,
                                   deltax, deltay)
      cairo_context.fill()

  if settings.SAVE_IMAGES:
    surface.write_to_png("_output_%02i.png"%world.currentTurn)

class Map:
    def __init__(self, N):
        self.size = N
        self.objectMap = {}
        self.squareMap = {}
        self.__bullet_paths = {}
        self.__unit_paths = {}
        self.__legal_moves = {}

    # Returns a random valid square on the map
    def getRandomSquare(self):
        return (random.randint(0, self.size), random.randint(0, self.size))

    # Place a map object onto the map
    def placeObject(self, mapobject, square):
        if self.isValidSquare(square):
            self.removeObject(mapobject)
            self.objectMap[mapobject] = square
            try:
                self.squareMap[square].append(mapobject)
            except KeyError:
                self.squareMap[square] = [mapobject]

    # Remove the object from the map
    def removeObject(self, mapobject):
        if mapobject in self.objectMap:
            self.squareMap[self.objectMap[mapobject]].remove(mapobject)
            del self.objectMap[mapobject]

    # Returns the square mapobject is on
    def getPosition(self, mapobject):
        try:
            return self.objectMap[mapobject]
        except KeyError, e:
            pass
#            log.debug("Get Position errored with: %s", e)


    # Returns the mapobject on square
    def getOccupants(self, square):
        if self.isValidSquare(square):
            return self.squareMap[square]
        # Raise an exception

    # Returns all the object on the map
    def getAllObjects(self):
        return self.objectMap.keys()

    # Returns if the square falls within map boundaries
    def isValidSquare(self, square):
        x,y = square
        return x < self.size and x >= 0 and y < self.size and y >= 0

    # Get all squares within radius n of square
    def getLegalMoves(self, square, n):
        lm_key = str((square, n, ))
        try:
          return self.__legal_moves[lm_key]
        except:
          pass

        log.debug("Calculating legal moves for %s",(str(lm_key)))
        x,y = square
        nd = set()
        nd.add((x,y))


        # All ways of getting moves N distance away:
        for m in xrange(0, n+1):
          # m is distance of move we are looking for
          for i in xrange(0, m):
            j = m - i
            # i in x, j in y
            nd.add((x+i, y+j))
            nd.add((x+i, y-j))
            nd.add((x-i, y+j))
            nd.add((x-i, y-j))

            # j in x, i in y
            nd.add((x+j, y+i))
            nd.add((x+j, y-i))
            nd.add((x-j, y+i))
            nd.add((x-j, y-i))


        self.__legal_moves[lm_key] = set(filter(self.isValidSquare, nd))
        return self.__legal_moves[lm_key]

    # Get the distance between x,y and m,n
    def calcDistance(self, start, end):
        x,y = start
        m,n = end
        return math.sqrt((m-x)**2 + (n-y)**2)

    # Get the path a bullet takes from x,y to m,n
    # R is the range on the bullets...why is this here?
    def calcBulletPath(self, start, end, R):
        x, y = start
        m, n = end
        R += 1
        bp_key = ",".join(map(str, (x,y,m,n,R)))
        if not bp_key in self.__bullet_paths:
            path = []
            if x-m is 0:
                    path = [(x, i+1) for i in xrange(min(y, n), min(y, n) + R)]
            elif y-n is 0:
                    path = [(j+1, y) for j in xrange(min(x, m), min(x, m) + R)]
            else:
                    ox = x
                    oy = y
                    slope = abs(float(n-y)/float(m-x))
                    if slope < 1:
                            xmovement = 1
                            ymovement = slope
                    else:
                            xmovement = 1/slope
                            ymovement = 1

                    if x > m:
                            xmovement = -xmovement
                    if y > n:
                            ymovement = -ymovement

                    x += 0.5
                    y += 0.5
                    while self.isValidSquare((x,y)):
                            x += xmovement
                            y += ymovement
                            if math.sqrt((ox-x)**2+(oy-y)**2) > R:
                              break

                            path.append((int(x), int(y)))


            self.__bullet_paths[bp_key] = path
        return self.__bullet_paths[bp_key]

    # Get the path a unit takes when travelling from (x,y) to (m,n)
    def calcUnitPath(self, start, end):
        x,y = start
        m,n = end
        up_key = ",".join(map(str, (x,y,m,n)))
        if not up_key in self.__unit_paths:
            log.debug("Calculating path from %s to %s", (x, y), (m, n))
            if x == m:
                if y == n:
                    return [(m,n)]
                else:
                    slope = 1.0
            else:
                slope = float(n-y)/float(m-x)

            path = []
            i = 0.0
            j = 0.0
            xdir = 1
            ydir = 1
            if abs(slope) < 1:
                    xmovement = 1
                    ymovement = slope
            else:
                xmovement = 1/slope
                ymovement = 1

            if (x > m):
                xmovement = -xmovement
                xdir = -1
            if (y > n):
                ymovement = -ymovement
                ydir = -1


            # [TODO] Generate this the right way
            while x != m or y != n:
                if x - m != 0:
                    for b in xrange(abs(int(xmovement+i))):
                        x += xdir
                        path.append((x,y))
                        if x == m:
                            break
                    i = (xmovement+i)-int(xmovement+i)

                if y - n != 0:
                    for a in xrange(abs(int(ymovement+j))):
                        y += ydir
                        path.append((x,y))
                        if y == n:
                            break
                    j = (ymovement+j)-int(ymovement+j)

            self.__unit_paths[up_key] = path
        return self.__unit_paths[up_key]


if __name__ == "__main__":
    m = Map(200)
    m.calcUnitPath((11, 13),(0, 193))
    m.calcBulletPath((0,0,), (5,5), 4)
    m.getLegalMoves((50, 50), 5)
    #x = "Just a unit"
    #m.placeObject(x, (0,0))
    #m.getPosition(x)
    #m.getOccupant((0,0))
    #m.getAllObjects()
    #m.removeObject(x)
    #m.getAllObjects()
    #m.getPosition(x)
    path = m.calcBulletPath((6, 16), (6, 70), int(m.size/8))
    #m.getlegalmoves((5,5), 2)
