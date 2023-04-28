# from picamera.array import PiRGBArray
# from picamera import PiCamera
import time
# from motherforker_controller import ZBController
import cv2
import numpy as np
import os

class Camera:
    # def __init__(self):
    #     self.width = 640/2
    #     self.height = 480/2
    #     self.frameRate = 32
    #     self.camera = PiCamera()
    #     self.camera.awb_mode = 'auto'
    #     self.camera.resolution = (int(self.width), int(self.height))
    #     self.camera.framerate = self.frameRate
    #     self.rawCapture = PiRGBArray(self.camera, size=(int(self.width), int(self.height)))
    
    def intialize_focal_length(self, observed_width: float, known_width: float, distance: float):
        # Calculate the focal length of the camera.
        self.focal_length = (observed_width * distance) / known_width
    
    def take_picture(self) -> str:
        # Take a picture and save it to the current directory with the date and time as the filename
        date = time.strftime("%Y-%m-%d_%H-%M-%S")
        filename = date + '.jpg'
        self.camera.capture(filename)
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


def main():
    # Challenge 1: Detect an object in front of the robot, drive towards it, and stop when it touches it.

    known_object_width = 7 # The width of the object in centimeters.
    known_object_width_measured_distance = 110 # The distance at which the object was measured.
    observed_width = 15 # The width of the object in pixels.

    camera = Camera()
    camera.intialize_focal_length(observed_width, known_object_width, known_object_width_measured_distance)
    focal_length = camera.get_focal_length()
    print("Initialized focal length:", focal_length)

    reached_object = False
    while not reached_object:
        # filename = camera.take_picture()
        filename = os.path.join(os.getcwd(), "motherforker-9000/images/sitterzaal/90cm.jpg")
        print("filename:", filename)
        img_processor = ImageProcessor(filename)
        observed_width = img_processor.get_object_width() # The width of the object in pixels.
        print("observed_width:", observed_width)
        
        x,y = img_processor.get_object_center_coordinates()
        print("x,y:", x, y)
        # Calculate the distance to the object.
        distance = (known_object_width * focal_length) / observed_width
        print("distance:", distance)


if __name__ == '__main__':
    main()