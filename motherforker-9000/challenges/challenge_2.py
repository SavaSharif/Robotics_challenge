import controller
from helper import *

class challenge2:
	"""
	1. An unknown object, typically of size ~ 7cm x 7cm x 7cm, and always clearly visible, is placed at a
	certain distance d ϵ [100 cm, 150 cm] from Position A.
	2. Place your robot on Position A such that the camera is facing towards the unknown object.
	3. Run your program. The robot should automatically drive to Position B, located at a distance of
	around 200cm from Position A, thereby automatically avoiding the unknown object.
	"""

	def __init__(self):
		# Setup ZB controller
		self.ZBC = controller.ZBController()
		curr_frame = openImage("images/sitterzaal/1679116970.84_90cm.jpg")
		self.distance = self.getObjectDistance(curr_frame)
		print('Initialisation done, object is %d CM away' % self.distance)

	def avoid_object(self):
		print('Todo')

	def getObjectDistance(self, curr_frame):
		img_edge = cropImageTop(cannyEdgeDet(curr_frame))
		return determineDistance(img_edge)

	def run(self):
		# self.ZBC.active_commands["forward"] = self.ZBC.current_time + 100
		self.ZBC.update_active_commands()
		self.ZBC.update_servos()
		print('We are on the way!')

if __name__ == '__main__':
	challenge = challenge2()
	challenge.run()
	print('Done')
