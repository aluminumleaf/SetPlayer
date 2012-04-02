
from cv import *
from math import *
import random
import time
import os

DEFAULT_FILE = "../Pictures/black_bg.png"
WHITE = 255
ADAPTIVE_THRESH_BLOCK_SIZE = 51

def displayImage(name, image):
    ''' Makes a window that displays the given image '''
    width, height = GetSize(image)
    #ratio = float(height)/float(width)
    scale = 1.0
    newHeight = int(height*scale)
    newWidth = int(width*scale)
    scaledImg = CreateMat(newHeight, newWidth, image.type)
    Resize(image, scaledImg)
    NamedWindow(name)
    ShowImage(name, scaledImg)

filename = raw_input('Name of picture is...?\n')
if filename == "":
    filename = DEFAULT_FILE

origImg = LoadImageM(filename)
displayImage('original', origImg)

imgSize = GetSize(origImg)
width, height = imgSize
img = CreateMat(height, width, CV_8UC1)
CvtColor(origImg, img, CV_RGB2GRAY)
#displayImage('step 1', img)

AdaptiveThreshold(
    img, img, 
    WHITE,
    CV_ADAPTIVE_THRESH_MEAN_C,
    CV_THRESH_BINARY,
    ADAPTIVE_THRESH_BLOCK_SIZE)
#displayImage('step 2', img)

hsvImage = CreateMat(height, width, CV_8UC3)
#hsvImage = CreateImage(imgSize, 8, 3)
CvtColor(origImg, hsvImage, CV_RGB2HSV)

hue = CreateMat(height, width, CV_8UC1)
sat = CreateMat(height, width, CV_8UC1)
val = CreateMat(height, width, CV_8UC1)

Split(hsvImage, hue, sat, val, None)

#displayImage('Hue', hue)
#displayImage('Saturation', sat)
#displayImage('Value', val)

#storage = CreateMemStorage(0)
#contours = FindContours(img, storage, 

houghImage = CreateMat(height, width, CV_8UC1)
houghImageColor = CreateMat(height, width, CV_8UC3)
storage = CreateMemStorage(0)
Canny(val, houghImage, 230, 250, 3)


lines = HoughLines2(houghImage, storage, CV_HOUGH_PROBABILISTIC, 1, CV_PI/180, 50, 10, 20)

print "Got", len(lines), "lines"
for line in lines:
    Line(houghImageColor, line[0], line[1], CV_RGB(255, 0, 0), 3, 8)

def lineAngle(line):
    y = line[0][1] - line[1][1]
    x = line[0][0] - line[1][0]
    return atan2(y, x)

def angleDiff(a1, a2):
    a1 = fmod(a1, CV_PI)
    a2 = fmod(a2, CV_PI)
    return a2 - a1;

def randomColor():
    r = random.randint(0, 255)
    g = random.randint(0, 255)
    b = random.randint(0, 255)
    return CV_RGB(r, g, b)

def distance(p1, p2):
    dx = p1[0] - p2[0]
    dy = p1[1] - p2[1]
    return sqrt(dx*dx + dy*dy)

def endpointDistance(line1, line2):
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

print "Finding cards..."

# Match orthogonal lines
matchedLines = []
for i in xrange(len(lines)):
    line1 = lines[i]

    for j in xrange(i+1, len(lines)):
        line2 = lines[j]
    
        if line1 == line2:
            continue

        v1 = lineVec(line1)
        v2 = lineVec(line2)

        dotProduct = dot(v1, v2)
        
        if abs(dotProduct) > 0.1:
            continue
#        if endpointDistance(line1, line2) > 10:
#            continue
        
        print "    Found match: ", line1, line2
        matchedLines += [(line1, line2)]
        
        color = randomColor()
        Line(houghImageColor, line1[0], line1[1], color, 3, 8)
        Line(houghImageColor, line2[0], line2[1], color, 3, 8)
        
displayImage('Hough Lines', houghImageColor)

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

cardOutlines = []
for i in xrange(len(matchedLines)):
    line1, line2 = matchedLines[i]
    for j in xrange(i+1, len(matchedLines)):
        
        other1, other2 = matchedLines[j]

        if (line1 == other1) and (line2 != other2):
            quad = extractVertices(line1, line2, other2)
            segments = (line2, line1, other2)

        elif (line2 == other1) and (line1 != other2):
            quad = extractVertices(line2, line1, other2)
            segments = (line1, line2, other2)

        elif (line1 == other2) and (line2 != other1):
            quad = extractVertices(line1, line2, other1)
            segments = (line2, line1, other1)

        elif (line2 == other2) and (line1 != other1):
            quad = extractVertices(line2, line1, other1)
            segments = (line1, line2, other1)

        else:
            continue

        cardOutlines += [(quad, segments)]

def areParallel(firstLine, secondLine):
    ''' Precondition: firstLine and secondLine have nonzero length '''
    firstVec = lineVec(firstLine)
    secondVec = lineVec(secondLine)
    return abs(dot(firstVec, secondVec)) > 0.95

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

def roughlyEqual(v1, v2, threshold):
    return abs(v1 - v2) < threshold

def isCardOutline(quad, segments):
    ''' Check whether the given quad likely outlines a card.

    Assumptions:
       - the vertices in quad and lines in segments have the same ordering
    '''

    a, b, c, d = quad
    leg1, middle, leg2 = segments

    if a == b or b == c or c ==d or d == a:
        return False
    
    # Are lines parallel where they should be?
    if not(areParallel((a,b), (c,d)) and areParallel((b,c), (d,a))):
        return False
    
    # Do line segments fall in reasonable locations?
    if not(areOverlapping(leg1,   (a,b)) and areOverlapping(middle, (b,c)) and areOverlapping(leg2,   (c,d))):
        return False

    # Does the aspect ratio make sense?
    ab = distance(a,b)
    bc = distance(b,c)
    cd = distance(c,d)
    da = distance(d,a)

    ratio1 = ab/bc
    ratio2 = cd/da

    if (ratio1 < 1):
        ratio1 = 1/ratio1
        ratio2 = 1/ratio2

    if not(roughlyEqual(ratio1, ratio2, 0.1)):
        return False
    if ratio1 > 2 or ratio2 > 2:
        return False

    return True

def orientCard(quad):
    a, b, c, d = quad
    if distance(a,b) > distance(b,c):
        return [b, c, d, a]
    return quad

def quadIsCardOutline(q):
    quad, segments = q
    return isCardOutline(quad, segments)

cardOutlines = filter(quadIsCardOutline, cardOutlines)

segmentedImg = CloneMat(origImg)
for (quad, segments) in cardOutlines: #[0:10]:
    PolyLine(segmentedImg, [tuple(quad)], True, randomColor(), 2)
displayImage("segmented cards?", segmentedImg)

def colorOfCard(cardImg, threshCardImg):
    redSum = greenSum = blueSum = 0
    width, height = GetSize(cardImg)
    for row in xrange(height):
        for col in xrange(width):
            redSum   += cardImg[row,col][2] * threshCardImg[row,col]
            greenSum += cardImg[row,col][1] * threshCardImg[row,col]
            blueSum  += cardImg[row,col][0] * threshCardImg[row,col]
    if greenSum > redSum:
        return "green"
    if redSum > greenSum and blueSum > redSum * 0.75:
        return "purple"
    return "red"

colors   = ["red", "green", "purple"]
shapes   = ["diamonds", "ovals", "squiggles"]
textures = ["open", "filled", "shaded"]
counts   = ["one", "two", "three"]

def templateImageFilename(count, texture, shape):
    return ("../Pictures/Training/" + 
            count + "_" + texture + "_" + shape + ".png")

def templateImage(count, texture, shape):
    file = templateImageFilename(count, texture, shape)
    if not os.path.exists(file):
        print "Warning: file not found (",file,")"
        return ()
    img = LoadImageM(file)
    width, height = GetSize(img)
    result = CreateMat(height, width, CV_8UC1)
    CvtColor(img, result, CV_RGB2GRAY)
    return result

templates = [(count, texture, shape, templateImage(count, texture, shape)) 
             for count in counts
             for texture in textures 
             for shape in shapes]
templates = filter(lambda x: x[3] != (), templates)

def compareImages(img1, img2):
    width, height = GetSize(img1)
    diff = CreateMat(height, width, CV_8UC1)
    AbsDiff(img1, img2, diff)
    return Sum(diff)

def bestMatch(templates, card):
    '''returns the template that best matches the card'''
    return sorted(templates, key=lambda c: compareImages(c[3],card))[0]

cardImgWidth = 100
cardImgHeight = 150

for i in xrange(len(cardOutlines)):
    cardImg = CreateMat(cardImgHeight, cardImgWidth, CV_8UC3)
    transform = CreateMat(3, 3, CV_32FC1)

    quad = orientCard(cardOutlines[i][0])
    GetPerspectiveTransform(quad,
                            [(0,0), 
                             (cardImgWidth, 0), 
                             (cardImgWidth, cardImgHeight), 
                             (0, cardImgHeight)],
                            transform)
    WarpPerspective(origImg, cardImg, transform) 
    grayCardImg = CreateMat(cardImgHeight, cardImgWidth, CV_8UC1)
    CvtColor(cardImg, grayCardImg, CV_RGB2GRAY)

    AdaptiveThreshold(
        grayCardImg, grayCardImg,
        WHITE,
        CV_ADAPTIVE_THRESH_MEAN_C,
        CV_THRESH_BINARY_INV,
        ADAPTIVE_THRESH_BLOCK_SIZE)

    windowName = 'card ' +  str(i)
    displayImage(windowName, grayCardImg)

#    SaveImage("../Pictures/Training/" + pictureName + str(i) + ".png", grayCardImg)

    color = colorOfCard(cardImg, grayCardImg)
    count, texture, shape, _ = bestMatch(templates, grayCardImg)
    print i, " is ", count, color, texture, shape


while True:
    time.sleep(500)

