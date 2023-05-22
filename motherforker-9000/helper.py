import os
import cv2
# from matplotlib import pyplot as plt
from picamera.array import PiRGBArray
from picamera import PiCamera
import RPi.GPIO as GPIO
import pigpio
import numpy as np
import time

class Forker:
    def __init__(self):
        # Run pigpiod
        processes = os.popen("ps -Af").read()
        if not processes.count('pigpiod'):
            print('pigpiod is not running, starting pigpiod...')
            os.system('sudo pigpiod')
        else:
            print('pigpiod is running...')

        # Setup servo pins
        self.close_servo = {'id':25, 'value':2000}
        self.updown_servo = {'id':9, 'value':1250}

        # init servo's
        self.pwm = pigpio.pi()
        self.pwm.set_mode(self.close_servo['id'], pigpio.OUTPUT)
        self.pwm.set_mode(self.updown_servo['id'], pigpio.OUTPUT)

        # Open arm
        self.pwm.set_servo_pulsewidth(self.close_servo['id'], self.close_servo['value'])
        # Lower arm
        self.pwm.set_servo_pulsewidth(self.updown_servo['id'], self.updown_servo['value'])
        self.putdown_object()

    def pickup_object(self):
        self.__move_servo_to(900, self.close_servo)
        self.__move_servo_to(1000, self.updown_servo)

    def putdown_object(self):
        self.__move_servo_to(1250, self.updown_servo)
        self.__move_servo_to(2000, self.close_servo)

    def __move_servo_to(self, to, servo, steps=10):
        if servo['value'] < to:
            [self.__set_servo(servo['id'], step) for step in range(servo['value'], to, steps)]
        else:
            [self.__set_servo(servo['id'], step) for step in range(servo['value'], to, -steps)]
        servo['value'] = to

    def __set_servo(self, servo, value):
        self.pwm.set_servo_pulsewidth(servo, value)
        time.sleep(.05)

    def pulse_width_module_cleanup(self):
        # Reset pos
        self.__move_servo_to(2000, self.close_servo)
        self.__move_servo_to(1250, self.updown_servo)
        # Cleanup
        self.pwm.set_PWM_dutycycle(self.close_servo['id'], 0)
        self.pwm.set_PWM_frequency(self.close_servo['id'], 0)
        self.pwm.set_PWM_dutycycle(self.updown_servo['id'], 0)
        self.pwm.set_PWM_frequency(self.updown_servo['id'], 0)

    def main(self):
        self.pickup_object()
        time.sleep(2)
        self.putdown_object()
        # TMP
        time.sleep(5)
        self.pulse_width_module_cleanup()


class Camera:
    def __init__(self):
        self.cam_width = 640
        self.cam_height = 480
        # self.resize_resolution = (320, 240)
        self.frameRate = 32
        self.camera = PiCamera()
        self.camera.awb_mode = 'auto'
        self.camera.resolution = (int(self.cam_width), int(self.cam_height))
        self.camera.framerate = self.frameRate
        # self.rawCapture = PiRGBArray(self.camera, size=(int(self.width), int(self.height))) #NOT USED?

    def intialize_focal_length(self, observed_width: float, known_width: float, distance: float):
            # Calculate the focal length of the camera by the lowest pixel
            self.focal_length = (observed_width * distance) / known_width

    def take_picture(self, filename = time.strftime("%Y-%m-%d_%H-%M-%S") + '.jpg') -> str:
            # Take a picture and save it to the current directory with the date and time as the filename
            self.camera.capture(filename)
            return filename

    def get_focal_length(self) -> float:
            # Return the focal length of the camera.
            return self.focal_length

class ImageProcessor:
    def __init__(self, filename: str):
        img = cv2.imread(filename)
        img = cv2.flip(img, -1)

        self.image = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.horizon = 223
    
    def apply_knipknip(self) -> np.ndarray:
        self.image = self.image[self.horizon:,200:440]

    def detect_edges(self) -> np.ndarray:
        """
        Detect the edges of an image
        :param img: An array with rgb image data
        :return: An array with the edges of the image
        """
        print("Detecting edges...")
        return cv2.Canny(self.image,200,500)

    def detect_color(self) -> np.ndarray:
        """
        Detect the color of an image
        :param img: An array with rgb image data
        :return: An array with the color of the image
        """
        print("Detecting color...")
        # Define the color ranges
        min_hue = 120
        max_hue = 150
        min_sat = 50
        max_sat = 255
        min_val = 50
        max_val = 255

        # Blur the image to reduce noise
        img_blur = cv2.GaussianBlur(self.image,(5,5),0)
        img_hsv = cv2.cvtColor(img_blur, cv2.COLOR_RGB2HSV)

        return cv2.inRange(img_hsv, (min_hue, min_sat, min_val), (max_hue, max_sat, max_val))

    def detect_contours(self):
        """
        Detect the contours of an image
        :param img: An array with rgb image data
        :return: An array with the contours of the image
        """
        print("Detecting contours...")
        self.contours, _ = cv2.findContours(self.image, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    def crop_image(self, part: str, pixels: int):
        # Crop the image to the part of the image we are interested in
        if part == 'top':
            self.image = self.image[:pixels, :]
        elif part == 'bottom':
            self.image = self.image[-pixels:, :]
        elif part == 'left':
            self.image = self.image[:, :pixels]
        elif part == 'right':
            self.image = self.image[:, -pixels:]
        else:
            print('Invalid part name!')

    def get_distance(self, img: np.ndarray) -> float:
        y = max(np.where(img == 255)[0])
        distance = 8.2 / np.tan(y * np.arctan(8.2/16) / self.horizon)
        print("Calculated distance:", distance)
        return distance

