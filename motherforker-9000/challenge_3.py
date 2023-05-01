import controller
from helper import Camera, ImageProcessor
import numpy as np

class challenge3:
    """
    1. An unknown object, typically of size ~ 7cm x 7cm x 7cm, and always clearly visible,
    is placed on a random location within a region of 250cm x 250cm (see Figure 2). 
    Position A is located at the left lower corner of that region.
    2. Place your robot on Position A such that the camera is facing the direction of the arrow.
    3. Run your program. The robot should automatically search for the unknown object and drive
    towards it and touch it with the front of the robot and subsequently stop.
    """
    def __init__(self):
        self.ZBC = controller.ZBController()
        self.camera = Camera()

        # Settings for object detection
        self.known_object_width = 7 # The width of the object in centimeters.
        self.known_object_width_measured_distance = 110 # The distance at which the object was measured.
        self.observed_width = 15 # The width of the object in pixels.

        # Calculate focal length
        self.ZBC.camera.intialize_focal_length(self.observed_width, self.known_object_width, self.known_object_width_measured_distance)
        self.focal_length = self.ZBC.camera.get_focal_length()
        self.sletsgo = False

    
    def capture_process_image(self):
        self.filename = self.camera.take_picture()
        self.image_processor = ImageProcessor(self.filename)        

    def object_detected(self) -> bool:
        self.capture_process_image()
        if len(np.argwhere(self.image_processor.edges)[0]) > 3:
            return True
        return False
    
    def object_direction(self) -> str:
        x_mean = self.image_processor.edges[:,1].mean()
        if x_mean < 155:
            return "left"
        elif x_mean > 160:
            return "right"
        else:
            return "forward"
        
    # def get_distance(self):
    #     pass

    def main(self):
        while self.ZBC.running:
            self.ZBC.get_input()
            if not self.sletsgo:
                if self.object_detected():
                    direction = self.object_direction()
                    if direction == "right":
                        self.ZBC.move("right", 1)
                    elif direction == "left":
                        self.ZBC.move("left", 1)
                    elif direction == "forward":
                        self.sletsgo = True
                        distance = (self.known_object_width * self.focal_length) / self.image_processor.get_object_width()
                        self.ZBC.move("forward", distance)
                else:
                    self.ZBC.move("right", 1)

            self.ZBC.update_active_commands()
            self.update_servos()


    # def turn2object(self):
    #     """
    #     Slowly turn right until object is in center part of the image
    #     """
    #     filename = self.camera.take_picture()
    #     self.image_processor = ImageProcessor(filename)

    #     while self.object_not_found:
    #         # turn left
    #         # take picture
    #         # Evaluate if object is seen

    #         filename = self.camera.take_picture()
            


    # def drive2object(self):
    #     if self.dist != None:
    #         self.ZBC.move("forward", self.dist)

    # def 

if __name__ == '__main__':
    chlg3 = challenge3()
    chlg3.main()