
import cv
import cv2
from numpy import *
#from cv import *

cv.NamedWindow("w1", cv.CV_WINDOW_AUTOSIZE)
camera_index = 0
size = 600
capture = cv.CaptureFromCAM(camera_index)

def repeat():
    global capture #declare as globals since we are assigning to them now
    global camera_index
    frame = cv.QueryFrame(capture)
    ratio = float(frame.height) / frame.width
    print ratio
    f2 = cv.CreateMat(int(size * ratio), size, cv.CV_8UC3)
    cv.Resize(frame, f2)
    cv.Threshold(f2, f2, 100, 255, cv.CV_THRESH_BINARY)
    cv.ShowImage("w1", f2)
    c = cv.WaitKey(2)
    print c
    if (c == ord('n')): #in "n" key is pressed while the popup window is in focus
        camera_index += 1 #try the next camera index
        capture = cv.CaptureFromCAM(camera_index)
        if not capture: #if the next camera index didn't work, reset to 0.
            camera_index = 0
            capture = cv.CaptureFromCAM(camera_index)
    elif (c == ord('q')):
        sys.exit(0)

while True:
    repeat()
