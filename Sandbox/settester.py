
from cv2 import *
import time

DEFAULT_FILE = "../Pictures/lights_on.png"
WHITE = 255
ADAPTIVE_THRESH_BLOCK_SIZE = 51

filename = raw_input('Name of picture is...?\n')
if filename == "":
    filename = DEFAULT_FILE

#origImg = LoadImage(filename)
#img = CreateMat(1, 1, CV_8UC1)
origImg = imread(filename)
grayImg = cvtColor(origImg, COLOR_RGB2GRAY)

#NamedWindow("original")
#ShowImage("original", img)
imshow('original', origImg)

img = adaptiveThreshold(
    grayImg, 
    WHITE, 
    ADAPTIVE_THRESH_MEAN_C, 
    THRESH_BINARY, 
    ADAPTIVE_THRESH_BLOCK_SIZE, 
    5)
imshow('adaptive threshold', img)

#storage = cv.CreateMemStorage(0)
#contours = cv.FindContours(img, storage, cv.CV_POLY_APPROX_DP, 3, 1)


while True:
    # do nothing! :D
    time.sleep(500)

