
from cv import *
from math import *
import random
import time

DEFAULT_FILE = "../Pictures/lights_on.png"
WHITE = 255
ADAPTIVE_THRESH_BLOCK_SIZE = 51

def displayImage(name, image):
    ''' Makes a window that displays the given image '''
    width, height = GetSize(image)
    #ratio = float(height)/float(width)
    scale = 0.5
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
#img = CreateImage(imgSize, 8, 1)
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
#hue = CreateImage(imgSize, 8, 1)
#sat = CreateImage(imgSize, 8, 1)
#val = CreateImage(imgSize, 8, 1)

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
CvtColor(houghImage, houghImageColor, CV_GRAY2RGB)

lines = HoughLines2(houghImage, storage, CV_HOUGH_PROBABILISTIC, 1, CV_PI/180, 50, 10, 20)

print "Got", len(lines), "lines"
#for line in lines:
#    Line(houghImageColor, line[0], line[1], CV_RGB(255, 0, 0), 3, 8)

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
    x = float(v1[0] * v2[0])
    y = float(v1[1] * v2[1])
    return (x + y) / (vecLen(v1) * vecLen(v2))

matchedLines = []

print "Finding cards..."
for i in xrange(len(lines)):
    line1 = lines[i]
    for j in xrange(i+1, len(lines)):
        line2 = lines[j]
        if line1 == line2:
            continue
        v1 = lineVec(line1)
        v2 = lineVec(line2)
        dotProduct = dot(v1, v2)
        if abs(dotProduct) > 0.2:
            continue
        if endpointDistance(line1, line2) > 10:
            continue
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
        return polyline + [firstLinePt]
    else:
        return polyline + [lastLinePt]
    

def extractVertices(middle, leg1, leg2):
    vertices = mergeCommonPoint(list(middle), leg1)
    vertices = mergeCommonPoint(vertices, leg2)
    return vertices


cardOutlines = []
for i in xrange(len(matchedLines)):
    line1, line2 = matchedLines[i]
    for j in xrange(i+1, len(matchedLines)):
        other1, other2 = matchedLines[j]
        if (line1 == other1) and (line2 != other2):
            cardOutlines += [extractVertices(line1, line2, other2)]
        if (line2 == other1) and (line1 != other2):
            cardOutlines += [extractVertices(line2, line1, other2)]
        if (line1 == other2) and (line2 != other1):
            cardOutlines += [extractVertices(line1, line2, other1)]
        if (line2 == other2) and (line1 != other1):
            cardOutlines += [extractVertices(line2, line1, other1)]

for set in cardOutlines:
    print set

segmentedImg = CloneMat(origImg)
for quad in cardOutlines:
    PolyLine(segmentedImg, [tuple(quad)], True, randomColor(), 5)
displayImage("segmented cards?", segmentedImg)
    

#
#
#for i in xrange(len(cardOutlines)):
#    cardImg = CreateMat(height, width, CV_8UC3)
#    transform = CreateMat(3, 3, CV_32FC1)
#
#    GetPerspectiveTransform(cardOutlines[i],
#                            [(0,0), (width, 0), (width, height), (0, height)],
#                            transform)
#    WarpPerspective(origImg, cardImg, transform) 
#    windowName = 'card ' +  str(i)
#    displayImage(windowName, cardImg)
#


while True:
    time.sleep(500)

