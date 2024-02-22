import pydicom
import numpy
import numpy as np
import cv2
import os
import math
import pylab
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from scipy import ndimage
from skimage import morphology as MM

#Load a 2D image
# conventional path: "D://copyRaw//2021_01_20.4511.400.2023_09_30.Rabbit_Aguix_4511_b00000//Conventional//dcm//0294.dcm"
# k-edge path : "D://copyRaw//2021_01_20.4511.400.2023_09_30.Rabbit_Aguix_4511_b00000//Spectral//k_gadolinium//0294.dcm"
# phantom is at slice 185
file_path = "D://copyRaw//2021_01_20.4511.700.2023_09_30.Rabbit_Aguix_4511_b00003//Spectral//k_gadolinium//0294.dcm"
medical_image = pydicom.read_file(file_path)

print(medical_image) #shows communication metadata
image = medical_image.pixel_array
print(image.shape)

# Intensity values
print(image.min())
print(image.max())

print(medical_image.RescaleIntercept)

# Conventional and K-edge images alike need to be 
def rescale(medical_image, image):
    intercept = medical_image.RescaleIntercept
    slope = medical_image.RescaleSlope
    rescaled_image = image*slope + intercept

    return rescaled_image

def window(image, window_width):
    window_center = image.mean()
    img_min = 0
    img_max = window_center + window_width // 2

    print(f"min:{img_min}")
    print(f"max: {img_max}")
    window_image = image.copy()
    window_image[window_image < img_min] = img_min
    window_image[window_image > img_max] = img_max
    
    return window_image


plt.subplot(1,3,1)
plt.imshow(image, cmap = 'gray')
plt.title('raw image')

plt.subplot(1,3,2)
rescaled_image = rescale(medical_image, image)
plt.imshow(rescaled_image, cmap = 'gray')
plt.title('rescaled image')

plt.subplot(1,3,3)
windowed_image = window(rescaled_image, 200)
plt.imshow(windowed_image, cmap = 'gray')
plt.title('rescaled rewindowed')
plt.show()


def remove_noise(file_path, display=False):
    medical_image = pydicom.read_file(file_path)
    image = medical_image.pixel_array
    
    k_image = rescale(medical_image, image)
    brain_image = window(k_image, 200) 
    
    segmentation = MM.dilation(brain_image, np.ones((1, 1)))
    labels, label_nb = ndimage.label(segmentation)
    
    label_count = np.bincount(labels.ravel().astype(int))
    label_count[0] = 0

    mask = labels == label_count.argmax()
 
    mask = MM.dilation(mask, np.ones((1, 1)))
    mask = ndimage.morphology.binary_fill_holes(mask)
    mask = MM.dilation(mask, np.ones((3, 3)))
    masked_image = np.invert(mask) * brain_image     
    
    return masked_image
plt.subplot(1,2,1)
plt.imshow(windowed_image, cmap = 'gray')
plt.subplot(1,2,2)
plt.imshow(remove_noise(file_path), 'gray')

plt.show()


