
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
    forker = Forker()

    camera = Camera()
    filename = camera.take_picture()
    print("filename:", filename)
    img_processor = ImageProcessor(filename)

    img_processor.apply_knipknip()
    edges = img_processor.detect_color()
    distance = img_processor.get_distance(edges)

    print('Initialisation done, we are driving %d CM towards the object' % distance)
    _ = input('Do you want to drive this distance?')
    print('We are on the way!')

    robot.move_once(direction="forward", distdeg = distance / 100)
    forker.pickup_object()
    _ = input('Do I have the object?')
    print("Driving around!")


    robot.move_once(direction="right", distdeg = 150)
    robot.move_once(direction="forward", distdeg = distance / 100)
    forker.putdown_object()
    robot.move_once(direction="backward", distdeg = 0.1)
    forker.pulse_width_module_cleanup()


if __name__ == '__main__':
    main()
