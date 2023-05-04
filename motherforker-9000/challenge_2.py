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
		# We are avoiding
		avoiding = True
		# Actions to avoid
		actions = [["right", 90], ["forward", 0.30], ["left", 90]]
		curr_action, last_action = 0, 0
		while avoiding:
			if self.ZBC.ready_to_move():
				if curr_action == last_action:
					self.ZBC.move(actions[curr_action][0], actions[curr_action][1])
					curr_action += 1
				else:
					last_action += 1
			if self.ZBC.ready_to_move() and last_action >= len(actions):
				avoiding = False

			# Default loop do not touch
			self.ZBC.update_active_commands()
			self.ZBC.update_servos()
			# Prevent the system from overloading during the loop
			time.sleep(0.05)

			# self.ZBC.move("left", 90)
			# self.ZBC.move("forward", 0.20)
			# self.ZBC.move("left", 90)
			# self.ZBC.move("forward", 0.15)
			# self.ZBC.move("right", 90)

	def run(self):
		print('Are we on the way?', self.ZBC.ready_to_move(), self.ZBC.servos)

		# self.ZBC.active_commands["forward"] = self.ZBC.current_time + 100
		done = False
		avoided = False
		print('We are on the way!')
		self.ZBC.move("forward", 1)
		while not done:

			# Default loop do not touch
			self.ZBC.update_active_commands()
			self.ZBC.update_servos()
			# Prevent the system from overloading during the loop
			time.sleep(0.05)

			if self.ZBC.ready_to_move():
				if not avoided:
					self.avoid_object()
					avoided = True
				else:
					done = True

			# Take image
			# self.take_curr_frame()
			# print(img)
			print('Are we on the way?', self.ZBC.ready_to_move())


if __name__ == '__main__':
	global old_settings
	old_settings = None
	challenge = Challenge2()
	challenge.run()
	print('Done')
