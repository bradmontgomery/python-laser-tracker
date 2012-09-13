#! /usr/bin/env python
import sys
from opencv import cv
from opencv import highgui


# This should be the size of the image coming from the camera.
cam_width = 640
cam_height = 480

# HSV color space Threshold values for a RED laser pointer. If the dot from the
# laser pointer doesn't fall within these values, it will be ignored.

# hue
hmin = 5
hmax = 6

# saturation
smin = 50
smax = 100

# value
vmin = 250
vmax = 256


def create_and_position_window(name, xpos, ypos):
    """Creates a named widow placing it on the screen at (xpos, ypos)."""
    highgui.cvNamedWindow(name, highgui.CV_WINDOW_AUTOSIZE)  # Create window
    highgui.cvResizeWindow(name, cam_width, cam_height)  # Resize it
    highgui.cvMoveWindow(name, xpos, ypos)  # move to (xpos,ypos) on the screen


def setup_camera_capture(device_num=0):
    """Perform camera setup for the device number (default device = 0).
    Returns a reference to the camera Capture.

    """
    try:
        device = int(device_num)
    except (IndexError, ValueError):
        # assume we want the 1st device
        device = 0
    print 'Using Camera device %d' % device

    # Try to start capturing frames
    capture = highgui.cvCreateCameraCapture(device)

    # set the wanted image size from the camera
    highgui.cvSetCaptureProperty(
        capture,
        highgui.CV_CAP_PROP_FRAME_WIDTH,
        cam_width
    )
    highgui.cvSetCaptureProperty(
        capture,
        highgui.CV_CAP_PROP_FRAME_HEIGHT,
        cam_height
    )

    # check that capture device is OK
    if not capture:
        print "Error opening capture device"
        sys.exit(1)
    return capture


def main():
    print "OpenCV version: %s (%d, %d, %d)" % (cv.CV_VERSION,
                                               cv.CV_MAJOR_VERSION,
                                               cv.CV_MINOR_VERSION,
                                               cv.CV_SUBMINOR_VERSION)

    # create output windows
    create_and_position_window('Thresholded_HSV_Image', 10, 10)
    create_and_position_window('RGB_VideoFrame', 10 + cam_width, 10)

    create_and_position_window('Hue', 10, 10 + cam_height)
    create_and_position_window('Saturation', 210, 10 + cam_height)
    create_and_position_window('Value', 410, 10 + cam_height)
    create_and_position_window('LaserPointer', 0, 0)

    # Set up the camer captures
    capture = setup_camera_capture()

    # create images for the different channels
    h_img = cv.cvCreateImage(cv.cvSize(cam_width, cam_height), 8, 1)
    s_img = cv.cvCreateImage(cv.cvSize(cam_width, cam_height), 8, 1)
    v_img = cv.cvCreateImage(cv.cvSize(cam_width, cam_height), 8, 1)
    laser_img = cv.cvCreateImage(cv.cvSize(cam_width, cam_height), 8, 1)
    cv.cvSetZero(h_img)
    cv.cvSetZero(s_img)
    cv.cvSetZero(v_img)
    cv.cvSetZero(laser_img)

    while True:
        # 1. capture the current image
        frame = highgui.cvQueryFrame(capture)
        if frame is None:
            # no image captured... end the processing
            break

        hsv_image = cv.cvCloneImage(frame)  # temporary copy of the frame
        cv.cvCvtColor(frame, hsv_image, cv.CV_BGR2HSV)  # convert to HSV

        # split the video frame into color channels
        cv.cvSplit(hsv_image, h_img, s_img, v_img, None)

        # Threshold ranges of HSV components.
        cv.cvInRangeS(h_img, hmin, hmax, h_img)
        cv.cvInRangeS(s_img, smin, smax, s_img)
        cv.cvInRangeS(v_img, vmin, vmax, v_img)

        # Perform an AND on HSV components to identify the laser!
        cv.cvAnd(h_img, v_img, laser_img)
        # This actually Worked OK for me without using Saturation, but
        # it's something you might want to try.
        #cv.cvAnd(laser_img, s_img,laser_img)

        # Merge the HSV components back together.
        cv.cvMerge(h_img, s_img, v_img, None, hsv_image)
        #-----------------------------------------------------
        # NOTE: default color space in OpenCV is BGR!!
        #-----------------------------------------------------

        highgui.cvShowImage('Thresholded_HSV_Image', hsv_image)
        highgui.cvShowImage('RGB_VideoFrame', frame)
        highgui.cvShowImage('Hue', h_img)
        highgui.cvShowImage('Saturation', s_img)
        highgui.cvShowImage('Value', v_img)
        highgui.cvShowImage('LaserPointer', laser_img)

        # handle events
        k = highgui.cvWaitKey(10)

        if k == '\x1b' or k == 'q':
            # user has press the ESC key, so exit
            break


if __name__ == '__main__':
    main()
