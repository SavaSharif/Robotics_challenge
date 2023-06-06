from controller import ZBController
from helper import *


class Challenge2:
	"""
	1. An unknown object, typically of size ~ 7cm x 7cm x 7cm, and always clearly visible, is placed at a
	certain distance d ϵ [100 cm, 150 cm] from Position A.
	2. Place your robot on Position A such that the camera is facing towards the unknown object.
	3. Run your program. The robot should automatically drive to Position B, located at a distance of
	around 200cm from Position A, thereby automatically avoiding the unknown object.
	"""

	def __init__(self):
		# Setup ZB controller
		self.ZBC = ZBController(False)
		# Setup Camera & ImageProcessor
		self.camera = Camera()
		filename = self.camera.take_picture()
		self.img_processor = ImageProcessor(filename)
		
		self.img_processor.apply_knipknip()
		edges = self.img_processor.detect_edges()
		self.distance = self.img_processor.get_distance(edges) - 7 # Because we like to play it safe

		print('Initialisation done, we are driving %d CM towards the object' % self.distance)

	def avoid_object(self):
		# We are avoiding
		self.ZBC.move_once("right", 90)
		self.ZBC.move_once("forward", 0.10)
		self.ZBC.move_once("left", 90)
		self.ZBC.move_once("forward", 0.35)
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
