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
        self.image_processor.apply_knipknip()        

    def object_detected(self) -> bool:
        self.capture_process_image()
        self.edges = self.image_processor.detect_edges()
        distance = self.image_processor.get_distance(self.edges)
        if len(np.argwhere(self.edges)) > 3 and distance < 150 :
            print("Object detected")
            return True
        return False
    
    def object_direction(self) -> str:
        edge_list = np.argwhere(self.edges)
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
                        self.ZBC.move_once("right", 10)
                    elif direction == "left":
                        self.ZBC.move_once("left", 10)
                    elif direction == "forward":
                        self.sletsgo = True
                        distance = self.image_processor.get_distance(self.edges) 
                        print("Moving forward with distance", distance)
                        self.ZBC.move_once("forward", distance / 100)
                else:
                    print("No object found, turning right")
                    self.ZBC.move_once("left", 10)



if __name__ == '__main__':
    global old_settings
    old_settings = None
    chlg3 = challenge3()
    chlg3.main()
