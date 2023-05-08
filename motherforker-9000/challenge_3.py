import controller
from helper import Camera, ImageProcessor
import numpy as np
import time

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
        self.ZBC = controller.ZBController(user_control=False)
        self.camera = Camera()
        self.sletsgo = False
    
    def capture_process_image(self):
        self.filename = self.camera.take_picture()
        print("Image captured with name", self.filename)
        self.image_processor = ImageProcessor(self.filename)        

    def object_detected(self) -> bool:
        self.capture_process_image()
        distance = self.image_processor.get_distance(self.image_processor.get_lowest_pixel())
        if len(np.argwhere(self.image_processor.edges)) > 3 and distance < 150 :
            print("Object detected")
            return True
        return False
    
    def object_direction(self) -> str:
        edge_list = np.argwhere(self.image_processor.edges)
        x_mean = edge_list.mean()
        print(x_mean)
        if x_mean < 250:
            return "left"
        elif x_mean > 390:
            return "right"
        else:
            return "forward"
        

    def main(self):
        while self.ZBC.running:
            # self.ZBC.get_input()
            if not self.sletsgo:
                if self.object_detected():
                    direction = self.object_direction()
                    print("Object in sight", direction)
                    if direction == "right":
                        self.ZBC.move_once("right", 5)
                    elif direction == "left":
                        self.ZBC.move_once("left", 5)
                    elif direction == "forward":
                        self.sletsgo = True
                        lowest_pixel = self.image_processor.get_lowest_pixel()
                        distance = self.image_processor.get_distance(lowest_pixel) 
                        print("Moving forward with distance", distance)
                        self.ZBC.move_once("forward", distance / 100)
                else:
                    print("No object found, turning right")
                    self.ZBC.move_once("right", 5)



if __name__ == '__main__':
    global old_settings
    old_settings = None
    chlg3 = challenge3()
    chlg3.main()