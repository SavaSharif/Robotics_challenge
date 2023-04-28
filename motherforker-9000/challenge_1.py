
from controller import ZBController
from helper import Camera, ImageProcessor


def main():
    # Challenge 1: Detect an object in front of the robot, drive towards it, and stop when it touches it.

    known_object_width = 7 # The width of the object in centimeters.
    known_object_width_measured_distance = 110 # The distance at which the object was measured.
    observed_width = 15 # The width of the object in pixels.
    robot = ZBController()

    camera = Camera()
    camera.intialize_focal_length(observed_width, known_object_width, known_object_width_measured_distance)
    focal_length = camera.get_focal_length()
    print("Initialized focal length:", focal_length)

    reached_object = False
    while not reached_object:
        filename = camera.take_picture()
        # filename = os.path.join(os.getcwd(), "motherforker-9000/images/sitterzaal/90cm.jpg")
        print("filename:", filename)
        img_processor = ImageProcessor(filename)
        observed_width = img_processor.get_object_width() # The width of the object in pixels.
        print("observed_width:", observed_width)
        
        x,y = img_processor.get_object_center_coordinates()
        print("x,y:", x, y)
        # Calculate the distance to the object.
        distance = (known_object_width * focal_length) / observed_width
        print("distance:", distance)
        robot.move(direction="forward",distdeg = distance)


if __name__ == '__main__':
    main()