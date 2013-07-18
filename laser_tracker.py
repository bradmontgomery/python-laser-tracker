#! /usr/bin/env python
import argparse

from sys import exit, stdout, stderr
from opencv import cv
from opencv import highgui


class LaserTracker(object):

    def __init__(self, cam_width=640, cam_height=480, hue_min=5, hue_max=6,
                 sat_min=50, sat_max=100, val_min=250, val_max=256):

        """
        * ``cam_width`` x ``cam_height`` -- This should be the size of the
        image coming from the camera. Default is 640x480.

        HSV color space Threshold values for a RED laser pointer are determined
        by:

        * ``hue_min``, ``hue_max`` -- Min/Max allowed Hue values
        * ``sat_min``, ``sat_max`` -- Min/Max allowed Saturation values
        * ``val_min``, ``val_max`` -- Min/Max allowed pixel values

        If the dot from the laser pointer doesn't fall within these values, it
        will be ignored.

        """

        self.cam_width = cam_width
        self.cam_height = cam_height
        self.hue_min = hue_min
        self.hue_max = hue_max
        self.sat_min = sat_min
        self.sat_max = sat_max
        self.val_min = val_min
        self.val_max = val_max

        self.capture = None  # camera capture device
        self.channels = {
            'hue': None,
            'saturation': None,
            'value': None,
            'laser': None,
        }

    def create_and_position_window(self, name, xpos, ypos):
        """Creates a named widow placing it on the screen at (xpos, ypos)."""
        # Create a window
        highgui.cvNamedWindow(name, highgui.CV_WINDOW_AUTOSIZE)
        # Resize it to the size of the camera image
        highgui.cvResizeWindow(name, self.cam_width, self.cam_height)
        # Move to (xpos,ypos) on the screen
        highgui.cvMoveWindow(name, xpos, ypos)

    def setup_camera_capture(self, device_num=0):
        """Perform camera setup for the device number (default device = 0).
        Returns a reference to the camera Capture object.

        """
        try:
            device = int(device_num)
            stdout.write("Using Camera Device: {0}\n".format(device))
        except (IndexError, ValueError):
            # assume we want the 1st device
            device = 0
            stderr.write("Invalid Device. Using default device 0\n")

        # Try to start capturing frames
        self.capture = highgui.cvCreateCameraCapture(device)

        # set the wanted image size from the camera
        highgui.cvSetCaptureProperty(
            self.capture,
            highgui.CV_CAP_PROP_FRAME_WIDTH,
            self.cam_width
        )
        highgui.cvSetCaptureProperty(
            self.capture,
            highgui.CV_CAP_PROP_FRAME_HEIGHT,
            self.cam_height
        )

        # check that capture device is OK
        if not self.capture:
            stderr.write("Error opening capture device. Quitting.")
            exit(1)
        return self.capture

    def handle_quit(self):
        """Quit the program if the user presses "Esc" or "q"."""
        k = highgui.cvWaitKey(10)
        if k in ['\x1b', 'q']:
            exit(0)

    def _create_blank_image(self):
        """Create an blank image based on the camera's size."""
        size = cv.cvSize(self.cam_width, self.cam_height)
        img = cv.cvCreateImage(size, 8, 1)
        cv.cvSetZero(img)
        return img

    def initialize_channels(self):
        for k in self.channels.keys():
            self.channels[k] = self._create_blank_image()

    def threshold_image(self, channel):
        if channel == "hue":
            minimum = self.hue_min
            maximum = self.hue_max
        elif channel == "saturation":
            minimum = self.sat_min
            maximum = self.sat_max
        elif channel == "value":
            minimum = self.val_min
            maximum = self.val_max

        cv.cvInRangeS(
            self.channels[channel],
            minimum,
            maximum,
            self.channels[channel]
        )

    def detect(self, frame):
        hsv_image = cv.cvCloneImage(frame)  # temporary copy of the frame
        cv.cvCvtColor(frame, hsv_image, cv.CV_BGR2HSV)  # convert to HSV

        # split the video frame into color channels
        cv.cvSplit(
            hsv_image,
            self.channels['hue'],
            self.channels['saturation'],
            self.channels['value'],
            None
        )

        # Threshold ranges of HSV components; storing the results in place
        self.threshold_image("hue")
        self.threshold_image("saturation")
        self.threshold_image("value")

        # Perform an AND on HSV components to identify the laser!
        cv.cvAnd(
            self.channels['hue'],
            self.channels['value'],
            self.channels['laser']
        )
        # This actually Worked OK for me without using Saturation, but
        # it's something you might want to try.
        #cv.cvAnd(
            #self.channels['laser'],
            #self.channels['satruation'],
            #self.channels['laser']
        #)

        # Merge the HSV components back together.
        cv.cvMerge(
            self.channels['hue'],
            self.channels['saturation'],
            self.channels['value'],
            None,
            hsv_image
        )
        return hsv_image

    def display(self, img, frame):
        """Display the combined image and (optionally) all other image channels
        NOTE: default color space in OpenCV is BGR.
        """
        highgui.cvShowImage('Thresholded_HSV_Image', img)
        highgui.cvShowImage('RGB_VideoFrame', frame)
        highgui.cvShowImage('Hue', self.channels['hue'])
        highgui.cvShowImage('Saturation', self.channels['saturation'])
        highgui.cvShowImage('Value', self.channels['value'])
        highgui.cvShowImage('LaserPointer', self.channels['laser'])

    def run(self):
        stdout.write("Using OpenCV version: {0} ({1}, {2}, {3})\n".format(
            cv.CV_VERSION,
            cv.CV_MAJOR_VERSION,
            cv.CV_MINOR_VERSION,
            cv.CV_SUBMINOR_VERSION
        ))

        # create output windows
        self.create_and_position_window('Thresholded_HSV_Image', 10, 10)
        self.create_and_position_window('RGB_VideoFrame',
            10 + self.cam_width, 10)
        self.create_and_position_window('Hue', 10, 10 + self.cam_height)
        self.create_and_position_window('Saturation', 210,
            10 + self.cam_height)
        self.create_and_position_window('Value', 410, 10 + self.cam_height)
        self.create_and_position_window('LaserPointer', 0, 0)

        # Set up the camer captures
        self.setup_camera_capture()

        # create images for the different channels
        self.initialize_channels()

        while True:
            # 1. capture the current image
            frame = highgui.cvQueryFrame(self.capture)
            if frame is None:
                # no image captured... end the processing
                stderr.write("Could not read camer frame. Quitting\n")
                exit(1)

            hsv_image = self.detect(frame)
            self.display(hsv_image, frame)

            self.handle_quit()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Run the Laser Tracker')
    parser.add_argument('-H', '--height',
        default='640',
        type=int,
        help='Camera Height'
    )
    parser.add_argument('-W', '--width',
        default=480,
        type=int,
        help='Camera Width'
    )
    parser.add_argument('-u', '--huemin',
        default=5,
        type=int,
        help='Hue Minimum Threshold'
    )
    parser.add_argument('-U', '--huemax',
        default=6,
        type=int,
        help='Hue Maximum Threshold'
    )
    parser.add_argument('-s', '--satmin',
        default=50,
        type=int,
        help='Saturation Minimum Threshold'
    )
    parser.add_argument('-S', '--satmax',
        default=100,
        type=int,
        help='Saturation Minimum Threshold'
    )
    parser.add_argument('-v', '--valmin',
        default=250,
        type=int,
        help='Value Minimum Threshold'
    )
    parser.add_argument('-V', '--valmax',
        default=256,
        type=int,
        help='Value Minimum Threshold'
    )
    params = parser.parse_args()

    tracker = LaserTracker(
        cam_width=params.width,
        cam_height=params.height,
        hue_min=params.huemin,
        hue_max=params.huemax,
        sat_min=params.satmin,
        sat_max=params.satmax,
        val_min=params.valmin,
        val_max=params.valmax
    )
    tracker.run()
