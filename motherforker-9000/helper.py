import os
import cv2
# from matplotlib import pyplot as plt
from picamera.array import PiRGBArray
from picamera import PiCamera
import numpy as np
import time

class Camera:
    def __init__(self):
        self.cam_width = 640
        self.cam_height = 480
        self.resize_resolution = (320, 240)
        self.frameRate = 32
        self.camera = PiCamera()
        self.camera.awb_mode = 'auto'
        self.camera.resolution = (int(self.cam_width), int(self.cam_height))
        self.camera.framerate = self.frameRate
        # self.rawCapture = PiRGBArray(self.camera, size=(int(self.width), int(self.height))) #NOT USED?

    def intialize_focal_length(self, observed_width: float, known_width: float, distance: float):
            # Calculate the focal length of the camera.
            self.focal_length = (observed_width * distance) / known_width

    def take_picture(self, filename = time.strftime("%Y-%m-%d_%H-%M-%S") + '.jpg') -> str:
            # Take a picture and save it to the current directory with the date and time as the filename
            self.camera.capture(filename, resize=self.resize_resolution)
            return filename

    def get_focal_length(self) -> float:
            # Return the focal length of the camera.
            return self.focal_length

class ImageProcessor:
    def __init__(self, filename: str):
        self.image = cv2.imread(filename)
        self.image = cv2.flip(self.image, -1)
        img_rgb = cv2.cvtColor(self.image, cv2.COLOR_BGR2RGB)
        edges = cv2.Canny(img_rgb,200,500)
        contours, hierarchy = cv2.findContours(edges, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        self.largest_contour = max(contours, key=cv2.contourArea)

    def crop_image_top(self, image: np.ndarray) -> np.ndarray:
        """
        Crop the top 50 pixels of an image
        :param img: An array with rgb image data
        :return: Cropped image
        """
        return image[50:,:]

    def open_image(self, filename) -> np.ndarray:
        """
        Open an image file and return it as a numpy array
        :param filename: The filename of the image to open
        :return: The image as a numpy array
        """
        if os.path.isfile(filename):
            img = cv2.imread(filename)
            img = cv2.flip(img, -1)
            return cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        else:
            print('Image file %s does NOT exist!' % filename)
            return None

    def get_object_contours(self) -> np.ndarray:
        # Get the contours of the object in the image.
        return self.largest_contour

    def get_object_width(self) -> float:
        # Get the leftmost and rightmost points of the object.
        leftmost = tuple(self.largest_contour[self.largest_contour[:,:,0].argmin()][0])
        rightmost = tuple(self.largest_contour[self.largest_contour[:,:,0].argmax()][0])
        # Calculate the width of the object.
        width = rightmost[0] - leftmost[0]
        return width

    def get_object_center_coordinates(self) -> tuple:
        # Get the center coordinates of the object.
        M = cv2.moments(self.largest_contour)
        cx = int(M['m10']/M['m00'])
        cy = int(M['m01']/M['m00'])
        print("middle point of largest contour:", cx, cy)

        return cx, cy

    class Helper:
        def get_distance(known_object_width: float, focal_length: float, observed_width: float) -> float:
            return (known_object_width * focal_length) / observed_width
