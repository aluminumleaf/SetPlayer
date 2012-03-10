
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
displayImage('step 2', img)

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

print "Finding cards..."
for line1 in lines:
    for line2 in lines:
        if line1 == line2:
            continue
        diff = abs(angleDiff(lineAngle(line1), lineAngle(line2)))
        if (diff - CV_PI/2) < 0.1:
            print "    Found match: ", line1, line2
        color = randomColor()
        Line(houghImageColor, line1[0], line1[1], color, 3, 8)
        Line(houghImageColor, line2[0], line2[1], color, 3, 8)

displayImage('Hough Lines', houghImageColor)


while True:
    time.sleep(500)

