
from cv import *
from math import *

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
Canny(val, houghImage, 50, 200, 3)
CvtColor(houghImage, houghImageColor, CV_GRAY2RGB)

lines = HoughLines2(houghImage, storage, CV_HOUGH_STANDARD, 1, CV_PI/180, 100, 0, 0)
for i in xrange(min(len(lines), 100)):
    line = lines[i]
    rho = line[0]
    theta = line[1]
    a = cos(theta)
    b = sin(theta)
    x0 = a*rho 
    y0 = b*rho
    pt1 = (Round(x0 + 1000*(-b)), Round(y0 + 1000*(a)))
    pt2 = (Round(x0 - 1000*(-b)), Round(y0 - 1000*(a)))
    Line(houghImageColor, pt1, pt2, CV_RGB(255, 0, 0), 3, 8)
displayImage('Hough Lines', houghImageColor)


while True:
    
    time.sleep(500)

