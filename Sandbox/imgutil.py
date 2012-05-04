
from cv import *
import cv2
import numpy

WHITE = 255
ADAPTIVE_THRESH_BLOCK_SIZE = 51

def invert(singleChannelImage):
    width, height = GetSize(singleChannelImage)
    result = CreateMat(height, width, CV_8UC1)
    white = CreateMat(height, width, CV_8UC1)
    Set(white, 255)
    Sub(white, singleChannelImage, result)
    return result

def grayscale(img):
    if (img.type == CV_8UC1):
        return img
    width, height = GetSize(img)
    result = CreateMat(height, width, CV_8UC1)
    CvtColor(img, result, CV_RGB2GRAY)
    return result
    
def hsv(img):
    
    width, height = GetSize(img)
    hsvImage = CreateMat(height, width, CV_8UC3)
    CvtColor(img, hsvImage, CV_RGB2HSV)

    hue = CreateMat(height, width, CV_8UC1)
    sat = CreateMat(height, width, CV_8UC1)
    val = CreateMat(height, width, CV_8UC1)

    Split(hsvImage, hue, sat, val, None)
    return (hue, sat, val)
    
def equalizeHist(img):
    return fromarray(cv2.equalizeHist(numpy.asarray(img)))

def getHoughLines(img):
    origImg = img
    img = grayscale(img)

    AdaptiveThreshold(
        img, img, 
        WHITE,
        CV_ADAPTIVE_THRESH_MEAN_C,
        CV_THRESH_BINARY,
        ADAPTIVE_THRESH_BLOCK_SIZE)

    #displayImage("thresholded image", img)

    width, height = GetSize(img)
    hsvImage = CreateMat(height, width, CV_8UC3)
    CvtColor(origImg, hsvImage, CV_RGB2HSV)

    hue = CreateMat(height, width, CV_8UC1)
    sat = CreateMat(height, width, CV_8UC1)
    val = CreateMat(height, width, CV_8UC1)

    Split(hsvImage, hue, sat, val, None)

    #displayImage("value", val)

    houghImage = CreateMat(height, width, CV_8UC1)
    storage = CreateMemStorage(0)
    Canny(val, houghImage, 230, 250, 3)

    #displayImage("post-Canny", houghImage)

    Dilate(houghImage, houghImage, None, 1)
    #displayImage("post-dilated Canny", houghImage)

    lines = HoughLines2(houghImage,
            storage,
            CV_HOUGH_PROBABILISTIC, # method
            1,                      # rho
            CV_PI/180,              # theta
            50,                     # threshold
            10,                     # param1 (min line length)
            20)                     # param2 (max gap between lines)

    return lines


def compareImages(img1, img2):
    width, height = GetSize(img1)
    diff = CreateMat(height, width, CV_8UC1)
    AbsDiff(img1, img2, diff)
    return Sum(diff)
    
def applyMask(img, mask):
    w, h = GetSize(img)
    dst = CreateMat(h, w, CV_8UC1)
    And(img, mask, dst)
    return dst
    
def dither(img):
    ''' Dither an image using Floyd-Steinberg dithering. 
    The image must be CV_8UC1 format.'''
    
    w, h = GetSize(img)
    err = CreateMat(h, w, CV_32FC1)
    Set(err, 0)
    
    out = CreateMat(h, w, CV_8UC1)
    
    for y in xrange(h):
        for x in xrange(w):
            pix = img[y,x]/255.0 + err[y,x]
            newpix = 1
            if pix < 0.5:
                newpix = 0
            out[y,x] = newpix * 255
            
            qerr = pix - newpix
            
            if x + 1 < w:
                err[y,  x+1] += 7.0/16 * qerr
            if y + 1 < h:
                err[y+1,x  ] += 5.0/16 * qerr
                if x - 1 > 0:
                    err[y+1,x-1] += 3.0/16 * qerr
                if x + 1 < w:
                    err[y+1,x+1] += 1.0/16 * qerr
            
    return out
    