from controller import ZBController
from helper import *
import time
import numpy as np
import cv2

from picamera.array import PiRGBArray
from picamera import PiCamera

class Challenge2:
	"""
	1. An unknown object, typically of size ~ 7cm x 7cm x 7cm, and always clearly visible, is placed at a
	certain distance d ϵ [100 cm, 150 cm] from Position A.
	2. Place your robot on Position A such that the camera is facing towards the unknown object.
	3. Run your program. The robot should automatically drive to Position B, located at a distance of
	around 200cm from Position A, thereby automatically avoiding the unknown object.
	"""

	def __init__(self):
		# META variables
		known_object_width = 7  # The width of the object in centimeters.
		known_object_width_measured_distance = 110  # The distance at which the object was measured.
		observed_width = 15  # The width of the object in pixels.

		# Setup ZB controller
		self.ZBC = ZBController(False)
		# Setup Camera & ImageProcessor
		self.camera = Camera()
		filename = self.camera.take_picture()
		self.img_processor = ImageProcessor(filename)

		lowest = self.img_processor.get_lowest_pixel()
		self.distance = self.img_processor.get_distance(lowest) - 20 # Because we like to play it safe

		print('Initialisation done, we are driving %d CM towards the object' % self.distance)

	def avoid_object(self):
		# We are avoiding
		self.ZBC.move_once("right", 90)
		self.ZBC.move_once("forward", 0.10)
		self.ZBC.move_once("left", 90)
		self.ZBC.move_once("forward", 0.30)
		self.ZBC.move_once("left", 90)
		self.ZBC.move_once("forward", 0.10)
		self.ZBC.move_once("right", 90)

	def run(self):
		_ = input('Do you want to drive this distance?')
		print('We are on the way!')
		self.ZBC.move_once("forward", self.distance / 100)
		self.avoid_object()
		self.ZBC.move_once("forward", (150 - self.distance) / 100)


if __name__ == '__main__':
	global old_settings
	old_settings = None
	challenge = Challenge2()
	challenge.run()
	print('Done')
