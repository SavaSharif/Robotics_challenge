
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

    # With a distance of 30 cm (1 A4 length)
    robot = ZBController()

    forker = Forker()

    robot.move_once(direction='forward', distdeg=0.3)
    forker.pickup_object()
    robot.move_once("right", 180)
    robot.move_once(direction='forward', distdeg=0.3)
    forker.putdown_object()
    robot.move_once(direction='backward', distdeg=0.3)

    forker.pulse_width_module_cleanup()


if __name__ == '__main__':
    main()
