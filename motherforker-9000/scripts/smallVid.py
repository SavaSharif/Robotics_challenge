from __future__ import division
import time

from picamera.array import PiRGBArray
from picamera import PiCamera

# import ZeroBorg3

# Camera settings
width = 640/2
height = 480/2
frameRate = 32

# Initializing the camera
camera = PiCamera()
camera.awb_mode = 'auto'
camera.resolution = (int(width), int(height))
camera.framerate = frameRate
rawCapture = PiRGBArray(camera, size=(int(width), int(height)))
camera.capture('foo.jpg')
print('Done')