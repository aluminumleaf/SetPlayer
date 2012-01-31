
#include <stdio.h>
#include <cxcore.h>
#include <highgui.h>

#define WINDOW_NAME "Hello Webcam!"

int main(int argc, char* argv[]) {
  
  CvCapture* camera = cvCreateCameraCapture(0);
  
  IplImage* frame = 0;
  
  cvNamedWindow(WINDOW_NAME, 1);
  
  while (1) { //Use while (true) if you are on Mac 
    
    frame = cvQueryFrame(camera);
    //Be careful not to change the value or to free the "frame" variable
    
    cvShowImage(WINDOW_NAME, frame);
    
    int keyPressed = cvWaitKey(2);
    
    if (keyPressed == 27)
      break;
  }
  
  cvReleaseCapture(&camera);
  return 0;
}
