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
		self.camera.intialize_focal_length(observed_width, known_object_width, known_object_width_measured_distance)

		focal_length = self.camera.get_focal_length()
		print("Initialized focal length: %d" % focal_length)

		# curr_frame = self.take_curr_frame()

		self.distance = 100#self.getObjectDistance(curr_frame)
		print('Initialisation done, object is %d CM away' % self.distance)

	def avoid_object(self):
		print('Todo')

	# def getObjectDistance(self, curr_frame):
	# 	# img_edge = cropImageTop(cannyEdgeDet(curr_frame))
	# 	img_edge = self.imager.
	# 	return determineDistance(img_edge)

	def take_curr_frame(self):
		self.camera.take_picture('curr_frame.jpg')

	def run(self):
		print('We are on the way!')
		# self.ZBC.active_commands["forward"] = self.ZBC.current_time + 100
		done = False
		while not done:
			# self.ZBC.update_active_commands()
			# self.ZBC.update_servos()
			# time.sleep(0.1)

			# Take image
			self.take_curr_frame()
			# print(img)
			print('test')
			done = True


if __name__ == '__main__':
	challenge = Challenge2()
	challenge.run()
	print('Done')
