python laser tracker
====================

This is a quick & dirty OpenCV app to track the dot from a red laser pointer.

Right now, the code performs the following steps, and displays the results in
several windows. The general idea is to:

1. Grab the video frame.
2. Convert it to HSV
3. Split the frame into individual components (separate images for H, S, and V)
4. Apply a threshold to each compenent (hopefully keeping just the dot from the laser)
5. Perform an AND operation on the 3 images (which "should" cut down on false positives)
6. Display the result.


Requirments
-----------

This requires Python and the Python wrapper for OpenCV. It was tested on Mac
OS X using OpenCV 2.4.5 installed with homebrew.


Usage
-----

Run ``python laster_tracker.py -h`` to see some command-line parameters.


License
-------

This code is MIT-licensed. You can basically do whatever you want with it.


Contributing
------------

Any suggestions, bug reports, or pull requests are welcome! If there's
something I should be doing differently, here, feel free to open an Issue and
let me know.
