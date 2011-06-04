class Point(object):
  def __init__(self, x=None,y=None):
    self.x = x
    self.y = y

  def __repr__(self):
    return "%s,%s" % (self.x, self.y)

def linesIntersect((a,b), (c,d)):
  return lineline(Point(*a), Point(*b), Point(*c), Point(*d))

# http://www.bryceboe.com/2006/10/23/line-segment-intersection-algorithm/
def lineline(A,B,C,D):
    """ Line-line intersection algorithm,
            returns point of intersection or None
    """
    # ccw from http://www.bryceboe.com/2006/10/23/line-segment-intersection-algorithm/
    def ccw(A,B,C):
        return (C.y-A.y)*(B.x-A.x) > (B.y-A.y)*(C.x-A.x)
    if ccw(A,C,D) != ccw(B,C,D) and ccw(A,B,C) != ccw(A,B,D):
        # formula from http://local.wasp.uwa.edu.au/~pbourke/geometry/lineline2d/
        ua =    float(((D.x-C.x)*(A.y-C.y))-((D.y-C.y)*(A.x-C.x)))/ \
                float(((D.y-C.y)*(B.x-A.x))-((D.x-C.x)*(B.y-A.y)))
        return Point(   A.x+(ua*(B.x-A.x)), \
                        A.y+(ua*(B.y-A.y)))
    return None


def calculateIntersectPoint(a,b,c,d):
  return lineline(Point(*a), Point(*b), Point(*c), Point(*d))


if __name__ == '__main__':
  p1 = (1,5)
  p2 = (4,7)

  p3 = (4,5)
  p4 = (3,7)

  p5 = (4,1)
  p6 = (3,3)

  p7 = (3,1)
  p8 = (3,10)

  p9 =  (0,6)
  p10 = (5,6)

  p11 = (472.0, 116.0)
  p12 = (542.0, 116.0)


  assert None != calculateIntersectPoint(p1, p2, p3, p4), "line 1 line 2 should intersect"
  assert None != calculateIntersectPoint(p3, p4, p1, p2), "line 2 line 1 should intersect"
  assert None == calculateIntersectPoint(p1, p2, p5, p6), "line 1 line 3 shouldn't intersect"
  assert None == calculateIntersectPoint(p3, p4, p5, p6), "line 2 line 3 shouldn't intersect"
  assert None != calculateIntersectPoint(p1, p2, p7, p8), "line 1 line 4 should intersect"
  assert None != calculateIntersectPoint(p7, p8, p1, p2), "line 4 line 1 should intersect"
  assert None != calculateIntersectPoint(p1, p2, p9, p10), "line 1 line 5 should intersect"
  assert None != calculateIntersectPoint(p9, p10, p1, p2), "line 5 line 1 should intersect"
  assert None != calculateIntersectPoint(p7, p8, p9, p10), "line 4 line 5 should intersect"
  assert None != calculateIntersectPoint(p9, p10, p7, p8), "line 5 line 4 should intersect"
