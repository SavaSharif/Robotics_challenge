from controller import ZBController
from helper import Camera, ImageProcessor, Forker
import numpy as np

class final_project:
    """
    1. An unknown object, typically of size ~ 7cm x 7cm x 7cm, and always clearly visible,
    is placed on a random location within a region of 250cm x 250cm (see Figure 2). 
    Position A is located at the left lower corner of that region.
    2. Place your robot on Position A such that the camera is facing the direction of the arrow.
    3. Run your program. The robot should automatically search for the unknown object and drive
    towards it and touch it with the front of the robot and subsequently stop.
    """
    def __init__(self):
        self.robot =  ZBController()
        self.camera = Camera()
        self.forker = Forker()

    def object_direction(self, edges) -> str:
        edge_list = np.argwhere(edges)
        x_mean = edge_list.mean()
        print(x_mean)
        if x_mean < 270:
            return "left"
        elif x_mean > 370:
            return "right"
        else:
            return "forward"

    def main(self):
        lets_go = False
        object_detected = False
        object_color = 150

        while self.robot.running:
            print("Running")
            if not lets_go:
                filename = self.camera.take_picture()
                print("Took picture")
                self.image_processor = ImageProcessor(filename)
                self.image_processor.apply_knipknip()
                print("Applied knip knip")
                edges = self.image_processor.detect_edges()
                color = self.image_processor.detect_color(object_color)

                if len(np.argwhere(color)) > 20 and self.image_processor.get_distance(edges) < 150:
                    print("Object detected true")
                    object_detected = True
                if object_detected:
                    direction = self.object_direction(color)
                    print("Object in sight", direction)
                    if direction == "right":
                        self.robot.move_once("right", 8)
                        print("Moving right")
                    elif direction == "left":
                        self.robot.move_once("left", 8)
                        print("Moving left")
                    elif direction == "forward":
                        lets_go = True
                        print("Lets go true")
                        distance = self.image_processor.get_distance(edges)
                        print("Moving forward with distance", distance)
                        self.robot.move_once("right", 20)
                        self.robot.move_once("forward", distance / 100)
                        print("Forking")
                        self.forker.pickup_object()
                        self.robot.move_once(direction="right", distdeg = 150)
                        self.robot.move_once(direction="forward", distdeg = distance / 100)
                        self.forker.putdown_object()
                        self.robot.move_once(direction="backward", distdeg = 0.1)
                        self.robot.move_once(direction="right", distdeg = 150)
                        lets_go = False
                        object_color = 30
                        object_detected = False
                        # forker.pulse_width_module_cleanup()

                else:
                    print("No object detected, turning left")
                    self.robot.move_once("left", 10)
                
                


if __name__ == '__main__':
    global old_settings
    old_settings = None
    chlg3 = final_project()
    chlg3.main()
