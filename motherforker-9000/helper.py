import os
import cv2
from matplotlib import pyplot as plt
import numpy as np

def getObjectFeet():
	print('test')

def openImage(file):
	"""
	Open an image from a file
	:param file: file string
	:return: return RGB image array
	"""
	if os.path.isfile(file):
		img = cv2.imread(file)
		img = cv2.flip(img, -1)
		return cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
	else:
		print('Image file %s does NOT exist!' % file)
		return None

def cropImageTop(img):
	"""
	Crop the top 50 pixels of an image
	:param img: An array with rgb image data
	:return: Cropped image
	"""
	return img[50:,:]

def cannyEdgeDet(img):
	"""
	Show the canny edge detection for a give image
	:param img: An array with rgb image data
	:return: The image with canny edge detection
	"""
	return cv2.Canny(img,200,500)

def showImage(img, cmap='viridis'):
	"""
	Show the given image, Only use on own OS not ZB!
	:param img: An array with rgb image data
	:param cmap: The color map to display the image in
	"""
	plt.subplot(1, 1, 1)
	plt.imshow(img, cmap=cmap)
	plt.show()
