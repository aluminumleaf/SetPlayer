from math import *

def lineAngle(line):
    y = line[0][1] - line[1][1]
    x = line[0][0] - line[1][0]
    return atan2(y, x)

def angleDiff(a1, a2):
    a1 = fmod(a1, pi) #CV_PI)
    a2 = fmod(a2, pi) #CV_PI)
    return a2 - a1;

def distance(p1, p2):
    dx = p1[0] - p2[0]
    dy = p1[1] - p2[1]
    return sqrt(dx*dx + dy*dy)

def lineLength(line):
    ''' Compute the length of a line '''
    return distance(line[0], line[1])

def endpointDistance(line1, line2):
    ''' Get the shortest distance from an endpoint of the first line
    to an endpoint of the second '''
    return min(distance(line1[0], line2[0]),
               distance(line1[0], line2[1]),
               distance(line1[1], line2[0]),
               distance(line1[1], line2[1]))

def lineVec(line):
    return ((line[0][0] - line[1][0]), (line[0][1] - line[1][1]))

def vecLen(vec):
    return distance((0,0),vec)

def dot(v1, v2):
    ''' Precondition: vectors have nonzero length '''
    x = float(v1[0] * v2[0])
    y = float(v1[1] * v2[1])
    magnitude = vecLen(v1) * vecLen(v2)
    return (x + y) / magnitude

def intersect(firstLine, secondLine):
    ''' finds the intersections of two line segments '''
    # We'll use parametrization here.
    # The math (since I should show my work):
    # 
    # Let the lines be
    #       first line  = V*s + P
    #       second line = U*t + Q
    # where any captial letter A is some vector A = <ax, ay>
    #
    # The intersection is where they're equal:
    #       V*s + P = U*t + Q
    # which is equivalent to
    #       vx*s + px = ux*t + qx   (1)
    #       vy*s + py = uy*t + qy   (2)
    # 
    # Solving for s with equation (1) yields
    #
    #       s = (ux/vx)*t + (qx - px)/vx
    #
    # and plugging that into equation (2) to solve for t yields
    #
    #            vx(qy - py) - vy(qx - px)
    #       t = ---------------------------
    #                 vy*ux  -  vx*uy
    #
    # Plugging t back into the second line's parametric equation
    # yields our desired point :)

    V = lineVec(firstLine)
    U = lineVec(secondLine)

    vLen = vecLen(V)
    uLen = vecLen(U)

    vx = V[0] / vLen
    vy = V[1] / vLen
    ux = U[0] / uLen
    uy = U[1] / uLen

    px = firstLine[0][0]
    py = firstLine[0][1]
    qx = secondLine[0][0]
    qy = secondLine[0][1]

    denominator = (vy*ux  -  vx*uy)
    if denominator == 0:
        print "OH NO! NOT DIVIDING BY ZERO!"
        return (0, 0)
    numerator = (vx*(qy - py) - vy*(qx - px))
    t = numerator / denominator

    xCoord = int(ux * t + qx)
    yCoord = int(uy * t + qy)
    return (xCoord, yCoord)

def mergeCommonPoint(polyline, line):
    firstPolyPt = polyline[0]
    lastPolyPt = polyline[-1]
    firstLinePt = line[0]
    lastLinePt = line[-1]

    dist1 = distance(firstPolyPt, firstLinePt)
    dist2 = distance(firstPolyPt, lastLinePt)
    dist3 = distance(lastPolyPt, firstLinePt)
    dist4 = distance(lastPolyPt, lastLinePt)
    minDist = min(dist1, dist2, dist3, dist4)

    if dist1 == minDist:
        return [lastLinePt] + polyline
    elif dist2 == minDist:
        return [firstLinePt] + polyline
    elif dist3 == minDist:
        return polyline + [lastLinePt]
    else:
        return polyline + [firstLinePt]

def extractVertices(middle, leg1, leg2):
    firstIntersect = intersect(middle, leg1)
    secondIntersect = intersect(middle, leg2)
    
    if distance(leg1[0], firstIntersect) < distance(leg1[1], firstIntersect):
        vertices = [leg1[1], firstIntersect, secondIntersect]
    else:
        vertices = [leg1[0], firstIntersect, secondIntersect]

    if distance(leg2[0], secondIntersect) < distance(leg2[1], secondIntersect):
        vertices += [leg2[1]]
    else:
        vertices += [leg2[0]]
#    vertices = mergeCommonPoint(list(middle), leg1)
#    vertices = mergeCommonPoint(vertices, leg2)
    return vertices

def areParallelish(firstLine, secondLine, threshold):
    ''' Precondition: firstLine and secondLine have nonzero length '''
    firstVec = lineVec(firstLine)
    secondVec = lineVec(secondLine)
    return abs(dot(firstVec, secondVec)) > 0.95

def areColinearish(firstLine, secondLine):
    parallelishThreshold = 1.0 # TODO: Magic number danger!

    f1, f2 = firstLine
    s1, s2 = secondLine

    # Get a line from a firstLine endpoint to a secondLine endpoint.
    if distance(f1, s1) > distance(f1, s2):
        l1 = (f1, s1)
    else:
        l1 = (f1, s2)

    # If this line isn't parallelish to the original lines, they're not
    # colinearish.
    if not areParallelish(firstLine, l1, parallelishThreshold) or \
       not areParallelish(secondLine, l1, parallelishThreshold):
       return False

    # Get a line from the other firstLine enpdoint to a secondLine endpoint.
    if distance(f2, s1) > distance(f2, s2):
        l2 = (f2, s1)
    else:
        l2 = (f2, s2)

    # Again, if it isn't parallelish to the original lines, they're not
    # collinearish.
    if not areParallelish(firstLine, l2, parallelishThreshold) or \
       not areParallelish(secondLine, l2, parallelishThreshold):
       return False

    # We're done!
    return True

def areOverlapping(firstLine, secondLine):
    ''' Checks whether two line segments overlap.

    Assumption: lines are colinear
    '''
    a1, a2 = firstLine
    b1, b2 = secondLine

    if (a1[0] < b1[0]) and (a1[0] < b2[0]) and (a2[0] < b2[0]) and (a2[0] < b2[0]):
        return False

    if (a1[0] > b1[0]) and (a1[0] > b2[0]) and (a2[0] > b2[0]) and (a2[0] > b2[0]):
        return False

    return True

def longestSegment(points):
    ''' Finds the pair of points farthest apart from each other '''
    lines = [(p1, p2) for p1 in points for p2 in points if p1 != p2]
    sortedLines = sorted(lines, key=lineLength)
    return sortedLines[-1] # last one has largest lineLength

def pointInLineCR(point, line):
    ''' Indicate whether a point is within a line segment's containment region.

    The Containment Region of some line L is the area between boundary 
    lines that intersect the endpoints of L and are perpendicular to L.
    
                         /               /
                        /  Containment  /
                       /      Region   /
                      /               /
        endpoint ->  O```.... L      /
          of L      /        ```....O <- endpoint     
                   /               /      of L
                  /  Containment  / 
                 /      Region   /
                /               /
            boundary        boundary

    This function returns True if the point is within this region and
    False otherwise.
    '''
    firstEndpt, secondEndpt = line

    # Some point p falls into a line L's containment region if lines 
    # between p and L's endpoints do not make obtuse angles with L.
    
    # Check against the first endpoint.
    lineOrient = lineAngle(line)
    compOrient = lineAngle((point, firstEndpt))
    angle = angleDiff(lineOrient, compOrient) 
    if abs(angle) > pi/2: #(CV_PI/2):
        return False

    # Check against the second endpoint.
    compOrient = lineAngle((point, secondEndpt))
    angle = angleDiff(lineOrient, compOrient) 
    if abs(angle) > pi/2: #(CV_PI/2):
        return False

    # If we made it this far, we're in!
    return True


def mergeLineSegments(firstLine, secondLine):
    return longestSegment(firstLine + secondLine)

