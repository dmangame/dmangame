# A map class, responsible for map functions, like
# finding the square a unit is on or what occupies a square.
# This is at the top so there are no circular dependencies
# between modules (not clean, will fix)
def calcDistance(start, end):
    x,y = start
    m,n = end
    return math.sqrt((m-x)**2 + (n-y)**2)

import ai
import mapobject
import math
import random
import logging
import settings
from unit import Unit
import operator

log = logging.getLogger("MAP")



def draw_map(cairo_context, width, height, world_data, turn_data):

  surface = cairo_context.get_target()

  deltax = float(width)/world_data["mapsize"]
  deltay = float(height)/world_data["mapsize"]

  cairo_context.set_source_rgb(1, 1, 1)
  cairo_context.rectangle(0, 0, width, height)
  cairo_context.fill()
  cairo_context.set_source_rgb(0,0,0)
  cairo_context.set_line_width(1.0)

  #self.draw_grid(cairo_context)

#       Draw the squares a unit sees ( using circle) in a really light unit color.
#
  # try getting the color from our color dictionary.

  for unit in turn_data["units"]:
      unit_data = world_data["units"][unit["unit_id"]]
      team = unit_data["team"]
      color = world_data["colors"][str(team)]

      x, y = unit["position"]
      alpha_color = (color[0], color[1], color[2], .15)
      cairo_context.set_source_rgba(*alpha_color)
      cairo_context.arc(deltax*x, deltay*y, (unit_data["stats"]["sight"])*deltax, 0, 360.0)
      cairo_context.fill()

      if "unitpath" in unit:
        path_color = map(operator.div, color, [2,2,2])
        cairo_context.set_source_rgb(*path_color)
        for x,y in unit["unitpath"]:
            cairo_context.rectangle(deltax*x, deltay*y, deltax, deltay)
            cairo_context.fill()

      if "bulletpath" in unit:
        # Draw the bullet paths
        cairo_context.set_source_rgb(.75, .75, .75)
        for path in unit["bulletpath"]:
            for x,y in path:
                cairo_context.rectangle(deltax*x, deltay*y, deltax, deltay)
                cairo_context.fill()

      # Draw the unit itself
      cairo_context.set_source_rgb(*color)
      cairo_context.rectangle(deltax*x, deltay*y,
                                   deltax, deltay)
      cairo_context.fill()




  for building in turn_data["buildings"]:
      try:
        building_data = world_data["buildings"][building["building_id"]]

        team = turn_data["buildings"][building]["team"]
        color = world_data["colors"][team] 
        x, y = building_data["position"]
        cairo_context.set_source_rgb(0,0,0)
        cairo_context.rectangle(deltax*x-(deltax/2), deltay*y-(deltay/2), 2*deltax, 2*deltay)
        cairo_context.fill()
        cairo_context.set_source_rgb(*color)
        cairo_context.rectangle(deltax*x, deltay*y, deltax, deltay)
        cairo_context.fill()
      except TypeError:
        pass

  cairo_context.set_source_rgb(0,0,0)
  for bullet in turn_data["bullets"]:
    x,y = bullet["position"]
    cairo_context.rectangle(deltax*x, deltay*y,
                               deltax, deltay)
    cairo_context.fill()

  for collision in turn_data["collisions"]:
      x, y = collision["position"]
      count = collision["count"] * 2
      survivor = collision["survivor"]
      if survivor:
        color = world_data["colors"][survivor]
      else:
        color = (0.25, 0.25, 0.25)


      cairo_context.set_source_rgb(*color)
      cairo_context.rectangle(deltax*x-(count/2*deltax), deltay*y-(count/2*deltay), count*deltax, count*deltay)
      cairo_context.fill()


  if settings.SAVE_IMAGES:
    surface.write_to_png("_output_%02i.png"%world_data["currentturn"])

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
            square = self.objectMap[mapobject]
            occupant_list = self.squareMap[square]
            occupant_list.remove(mapobject)
            if not occupant_list:
              del self.squareMap[square]

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

        if x == m and y == n:
          yield (m,n)

        else:

          if x == m:
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
                      yield (x,y)
                      if x == m:
                          break
                  i = (xmovement+i)-int(xmovement+i)

              if y - n != 0:
                  for a in xrange(abs(int(ymovement+j))):
                      y += ydir
                      yield (x,y)
                      if y == n:
                          break
                  j = (ymovement+j)-int(ymovement+j)


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
