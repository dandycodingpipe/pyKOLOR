import pydicom
import matplotlib.pyplot as plt

#Load a 2D image
# conventional path: "D://copyRaw//2021_01_20.4511.400.2023_09_30.Rabbit_Aguix_4511_b00000//Conventional//dcm//0294.dcm"
# k-edge path : "D://copyRaw//2021_01_20.4511.400.2023_09_30.Rabbit_Aguix_4511_b00000//Spectral//k_gadolinium//0294.dcm"
# phantom is at slice 185
file_path ="D://copyRaw//2021_01_20.4511.400.2023_09_30.Rabbit_Aguix_4511_b00000//Conventional//dcm//0185.dcm"
medical_image = pydicom.read_file(file_path)

#print(medical_image) #shows communication metadata
image = medical_image.pixel_array
print(image.shape)

# Intensity values
print(image.min())
print(image.max())

print(medical_image.RescaleIntercept)


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
windowed_image = window(rescaled_image, 200, False)
plt.imshow(windowed_image, cmap = 'gray')
plt.title('rescaled rewindowed')
plt.show()
