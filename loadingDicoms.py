import pydicom
import os
import numpy as np
from itkwidgets import view

rabbit = 1
series = "400"
time = "b00000"
PathDicom = f"D://copyRaw//Rabbit_AGUIX_{rabbit}//2021_01_20.4511.{series}.2023_09_30.Rabbit_Aguix_4511_{time}//Conventional"
DCMFiles = [os.path.join(dirName, filename)
            for dirName, _, fileList in os.walk(PathDicom)
            for filename in fileList if filename.lower().endswith('.dcm')]

print(len(DCMFiles))

# Load the first image to get the slice thickness
ref_image = pydicom.read_file(DCMFiles[0])

# Assuming all slices have the same thickness
slice_thickness = float(ref_image.SliceThickness)

# Load all images and sort by ImagePositionPatient (z-axis)
images = [pydicom.read_file(f) for f in DCMFiles]
images.sort(key=lambda x: float(x.ImagePositionPatient[2]))

# Assuming all images have the same dimensions
ConstPixelDims = (int(images[0].Rows), int(images[0].Columns), len(images))

# Create a 3D numpy array for the images
ArrayDicom = np.zeros(ConstPixelDims, dtype=ref_image.pixel_array.dtype)

# Fill the 3D array with the image pixel data
for i, img in enumerate(images):
    ArrayDicom[:, :, i] = img.pixel_array

import matplotlib.pyplot as plt

# Display one slice
plt.figure(figsize=(10, 10))
plt.imshow(ArrayDicom[:, :, int(len(images)/2)], cmap='gray')
plt.axis('off')
plt.show()

view(ArrayDicom)