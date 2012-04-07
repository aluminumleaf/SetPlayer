
# system imports
from cv import *
from math import *
import random
import time
import os

# our imports
from geometry import *

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

def getImage():
    filename = raw_input('Name of picture is...?\n')
    if filename == "":
        filename = DEFAULT_FILE
    return LoadImageM(filename)

def grayscale(img):
    if (img.type == CV_8UC1):
        return img
    width, height = GetSize(img)
    result = CreateMat(height, width, CV_8UC1)
    CvtColor(img, result, CV_RGB2GRAY)
    return result

def getHoughLines(img):
    img = grayscale(img)

    AdaptiveThreshold(
        img, img, 
        WHITE,
        CV_ADAPTIVE_THRESH_MEAN_C,
        CV_THRESH_BINARY,
        ADAPTIVE_THRESH_BLOCK_SIZE)

    width, height = GetSize(img)
    hsvImage = CreateMat(height, width, CV_8UC3)
    CvtColor(origImg, hsvImage, CV_RGB2HSV)

    hue = CreateMat(height, width, CV_8UC1)
    sat = CreateMat(height, width, CV_8UC1)
    val = CreateMat(height, width, CV_8UC1)

    Split(hsvImage, hue, sat, val, None)

    houghImage = CreateMat(height, width, CV_8UC1)
    storage = CreateMemStorage(0)
    Canny(val, houghImage, 230, 250, 3)

    lines = HoughLines2(houghImage, storage, CV_HOUGH_PROBABILISTIC, 1, CV_PI/180, 50, 10, 20)

    return lines

def randomColor():
    r = random.randint(0, 255)
    g = random.randint(0, 255)
    b = random.randint(0, 255)
    return CV_RGB(r, g, b)

# Match orthogonal lines
origImg = getImage()
displayImage('original', origImg)
width, height = GetSize(origImg)
houghImageColor = CreateMat(height, width, CV_8UC3)
lines = getHoughLines(origImg)
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
        
#        print "    Found match: ", line1, line2
        matchedLines += [(line1, line2)]
        
        color = randomColor()
        Line(houghImageColor, line1[0], line1[1], color, 3, 8)
        Line(houghImageColor, line2[0], line2[1], color, 3, 8)
        
        

def areSameOutline(firstOutline, secondOutline, imageWidth, imageHeight):
    ''' indicates whether two outlines are more or less the same '''

    # Constants (TODO: refactor out later)
    PERMISSIBLE_OVERLAP_FACTOR = 0.9
    MAX_SAME_OUTINES_AREA_DIFF = 0.9
    
    # Create Images to draw polygons for each outline on
    firstPoly = CreateMat(imageHeight, imageWidth, CV_8UC1)
    secondPoly = CreateMat(imageHeight, imageWidth, CV_8UC1)
    bothPolys = CreateMat(imageHeight, imageWidth, CV_8UC1)

    # Black all the images out
    Set(firstPoly, 0)
    Set(secondPoly, 0)
    Set(bothPolys, 0)

    # Draw the polygons on
    FillPoly(firstPoly, [firstOutline], 255) # TODO: make 255 a constant.
    FillPoly(secondPoly, [secondOutline], 255) # TODO: 0 too :P.
    FillPoly(bothPolys, [firstOutline], 255) 
    FillPoly(bothPolys, [secondOutline], 255) 
    
    # Calculate how many pixels they take up
    firstArea = Sum(firstPoly)[0]
    secondArea = Sum(secondPoly)[0]
    expectedTotalArea = firstArea + secondArea
    actualTotalArea = Sum(bothPolys)[0]

    if secondArea == 0:
        return False
    areaRatio = firstArea / secondArea
    if areaRatio > 1:
        areaRatio = 1.0 / areaRatio
    if areaRatio < MAX_SAME_OUTINES_AREA_DIFF:
        return False

#    # For debugging purposes...
#    if actualTotalArea < PERMISSIBLE_OVERLAP_FACTOR * expectedTotalArea:
#        
#        displayImage("first polygons", firstPoly)
#        displayImage("second polygons", secondPoly)
#        displayImage("both polygons", bothPolys)
#        
#        print "first polygon:  ", firstArea
#        print "second polygon: ", secondArea
#        print "both polygons:  ", actualTotalArea
#        print "expected area:  ", expectedTotalArea
#        print "threshold is:   ", expectedTotalArea * PERMISSIBLE_OVERLAP_FACTOR
#
#        print "same card? -> ",  actualTotalArea < PERMISSIBLE_OVERLAP_FACTOR * expectedTotalArea
#
#        raw_input(" ... hit ENTER to continue... ")
#
#        DestroyWindow("first polygons")
#        DestroyWindow("second polygons")
#        DestroyWindow("both polygons")
#
    # Decide whether or not they are the same
    return actualTotalArea < PERMISSIBLE_OVERLAP_FACTOR * expectedTotalArea


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
textures = ["open", "filled", "striped"]
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

def wordToInt(word):
    return counts.index(word) + 1

templates = [(wordToInt(count), texture, shape, templateImage(count, texture, shape)) 
             for count in counts
             for texture in textures 
             for shape in shapes]
templates = filter(lambda x: x[3] != (), templates)

newTemplates = []
for t in templates:
    if t[2] == "squiggles":
        img = t[3]
        width, height = GetSize(img)
        newImg = CreateMat(height, width, CV_8UC1)
        Flip(img, newImg, 1) # horizontal flip
        newTemplates += [(t[0], t[1], t[2], newImg)]
templates += newTemplates

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

def cardShadeLevelIndex(cardImage, shapeCount):
    ''' Determines how shaded a card is (open, striped, or filled) 
    
    Assumes:
     - cardImage is a black and white image of the card
     - shapeCount is not 0
    '''
    return Sum(cardImage)[0] / (shapeCount * 255)

width, height = GetSize(templates[0][3])
maskImg = CreateMat(height, width, CV_8UC1)
Set(maskImg, 255)
border = 15
Rectangle(maskImg, (border, border), (width-border, height-border), 0, CV_FILLED)
displayImage("mask", maskImg)

def getCardImage(outline):
    global origImg, cardImgHeight, cardImgWidth

    cardImg = CreateMat(cardImgHeight, cardImgWidth, CV_8UC3)
    transform = CreateMat(3, 3, CV_32FC1)

    quad = orientCard(outline)
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
    return (cardImg, grayCardImg)


def removeDuplicateCards(outlines, imageWidth, imageHeight):
    ''' Spits out a cleaned up list of outlines without rough duplicates '''
    prunedOutlines = []
    numOutlines = len(outlines)

    for i in range(numOutlines):
        isDuplicate = False
        
        for j in range(i+1, numOutlines):
            if areSameOutline(outlines[i], outlines[j], 
                              imageWidth, imageHeight):
                isDuplicate = True
                break
        if not isDuplicate:
            prunedOutlines.append(outlines[i])

    return prunedOutlines

# Might use later in refactoring...
# ------------------------------------
#BORDER_MASK = maskImg
#def hasCardlikeBorder(candidateImg):
#    ''' Determines whether a given "card"s border is all white '''
#    PERMISSIBLE_BORDER_NOISE = 1000
#    maskedImg = applyMask(candidateImg, BORDER_MASK)
#    borderNoise = Sum(maskedImg)[0] / 255
#    return borderNoise <= PERMISSIBLE_BORDER_NOISE

imgWidth, imgHeight = GetSize(origImg)
justOutlines = map(lambda x: x[0], cardOutlines)
justOutlines = removeDuplicateCards(justOutlines, imgWidth, imgHeight)

cardImages = map(getCardImage, justOutlines)

def applyMask(img, mask):
    w, h = GetSize(img)
    dst = CreateMat(h, w, CV_8UC1)
    And(img, mask, dst)
    return dst

for i in xrange(len(cardImages)):

    cardImg, grayCardImg = cardImages[i]

    maskedImg = applyMask(grayCardImg, maskImg)

    maskSum = Sum(maskedImg)[0] / 255

    PERMISSIBLE_BORDER_NOISE = 1000
    if maskSum >= PERMISSIBLE_BORDER_NOISE:
        continue

    windowName = 'card ' +  str(i)
    displayImage(windowName, grayCardImg)

#    SaveImage("../Pictures/Training/" + pictureName + str(i) + ".png", grayCardImg)

    color = colorOfCard(cardImg, grayCardImg)
    count, texture, shape, _ = bestMatch(templates, grayCardImg)
    print i, " is ", count, color, texture, shape, " with total # pixels/shape = ", cardShadeLevelIndex(grayCardImg, count)
    

while True:
    time.sleep(500)

