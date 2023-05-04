
from controller import ZBController
from helper import Camera, ImageProcessor


def main():
    # Challenge 1: Detect an object in front of the robot, drive towards it, and stop when it touches it.

    robot = ZBController()

    camera = Camera()
    filename = camera.take_picture()
    print("filename:", filename)
    img_processor = ImageProcessor(filename)

    lowest = img_processor.get_lowest_pixel()
    distance = img_processor.get_distance(lowest)

    robot.move_once(direction="forward", distdeg = distance / 100)


if __name__ == '__main__':
    main()