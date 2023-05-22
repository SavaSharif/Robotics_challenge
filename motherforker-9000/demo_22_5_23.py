
from controller import ZBController
from helper import Camera, ImageProcessor, Forker


def main():
    """
    Minimaal:
    - Oppakken
    - Neerzetten

    Het liefst ook:
    - Rij naar object
    - Verplaats object
    """
    robot = ZBController()

    camera = Camera()
    filename = camera.take_picture()
    print("filename:", filename)
    img_processor = ImageProcessor(filename)

    lowest = img_processor.get_lowest_pixel()
    distance = img_processor.get_distance(lowest)

    print('Initialisation done, we are driving %d CM towards the object' % distance)
    _ = input('Do you want to drive this distance?')
    print('We are on the way!')

    robot.move_once(direction="forward", distdeg = distance / 100)

    forker = Forker()
    forker.pickup_object()
    forker.pulse_width_module_cleanup()


if __name__ == '__main__':
    main()
