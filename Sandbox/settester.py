
from cv import *
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

while True:
    
    time.sleep(500)

