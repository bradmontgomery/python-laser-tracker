python laser tracker
====================

This is a quick attempt to track the dot from a red laser pointer.

Right now, the code performs the following steps, and displays the results in
several HighGUI windows. The general idea is to:

1. Grab the video frame.
2. Convert it to HSV
3. Split the frame into individual components (separate images for H, S, and V)
4. Apply a threshold to each compenent (hopefully keeping just the dot from the laser)
5. Perform an AND operation on the 3 images (which "should" cut down on false positives)

TODO (or, what should you do now!)
----------------------------------

* Identify the _best_ location for the identified laser. ie: x,y coordinates in the image.
* Do something interesting with it; e.g. draw a circle around it, control the mouse cursor, build a game, etc.

Requirments
-----------

This requires Python and the Python wrapper for OpenCV.

Configuration
-------------

You'll need to look at the source, but there are global constants at the top
of the ``laser_tracker.py`` file. You may need to adjust these to suite your 
situation.

License
-------

This code is MIT-licensed. You can basically do whatever you want with it.


