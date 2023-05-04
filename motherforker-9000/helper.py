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
        
        self.edges = cv2.Canny(self.image,200,500)
        self.knipknip = self.edges[self.horizon:,200:440]

    def crop_image_top(self):
        """
        Crop the top 50 pixels of an image
        :param img: An array with rgb image data
        :return: Cropped image
        """
        self.image = self.image[50:,:]
    
    def get_lowest_pixel(self) -> float:
        y = max(np.where(self.knipknip == 255)[0])
        print("Lowest edge pixel:", y)
        return y
    
    def get_distance(self, lowest_pixel) -> float:
        distance = 8.2 / np.tan(lowest_pixel * np.arctan(8.2/16) / self.horizon)
        print("Calculated distance:", distance)
        return distance

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

