
from controller import ZBController
from helper import Camera, ImageProcessor


def main():
    # Challenge 1: Detect an object in front of the robot, drive towards it, and stop when it touches it.

    robot = ZBController()

    camera = Camera()
    filename = camera.take_picture()
    print("filename:", filename)
    img_processor = ImageProcessor(filename)

    img_processor.apply_knipknip()
    edges = img_processor.detect_edges()
    distance = img_processor.get_distance(edges)

    print('Initialisation done, we are driving %d CM towards the object' % distance)
    _ = input('Do you want to drive this distance?')
    print('We are on the way!')

    robot.move_once(direction="forward", distdeg = distance / 100)


if __name__ == '__main__':
    main()
