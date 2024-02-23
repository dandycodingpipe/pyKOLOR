import pydicom
import os
import numpy as np
import matplotlib.pyplot as plt

class Sample:
    """
    Oh yeah baby we are doing OOP for package dev. now! 
    
    The sample class has the timepoint attribute which consists of both conventional and kedge 3d arrays
    for a given timepoint. 

    """
    def __init__(self, rabbit_id):
        self.rabbit_id = rabbit_id
        self.acquisition = [] #we are in 4D, regardless if we want to look at conventional or Kedge, it will always correspond to a timepoint in acquisition
        self.fetch_data(rabbit_id)

    def fetch_data(self, rabbit_id):
        """
        Using just the rabbit ID, this function will automatically find the relevant directory
        and add all timepoints from that directory.
        """
        base_path = f"D:\copyRaw\Rabbit_AGUIX_{rabbit_id}"
        directories = [d for d in os.listdir(base_path) if os.path.isdir(os.path.join(base_path, d))]
        directories.sort()

        print("Available directories:")
        for i, directory in enumerate(directories):
            print(f"{i}: {directory}")
        
        for t, acquisitions in enumerate(directories):
            self.add_timepoint(base_path, directories, t)

    def add_timepoint(self, base_path, directories, t):
        """
        Take all the timepoints that fetch_data() identifies in order to create
        and append acquisitions to the acquisition array attribute
        """
        suffix = None
        conventional = None
        kedge = None
        time = t

        for i in range(0,2):
            if(i == 0):
                suffix = r"Conventional"
            elif(i==1):
                suffix = r"Spectral\k_gadolinium"

            specific_path = os.path.join(base_path, directories[t], suffix)
            
            DCMFiles = []
            for dirName, _, fileList in os.walk(specific_path):
                for filename in fileList:
                    if filename.lower().endswith('.dcm'):
                        DCMFiles.append(os.path.join(dirName, filename))

                    if not DCMFiles:
                        print("No DICOM files found in the specified path.")
                        return None

            print(f"File {t} total DICOM files found: {len(DCMFiles)}")

            images = [pydicom.dcmread(f) for f in DCMFiles]
            images.sort(key=lambda x: float(x.ImagePositionPatient[2]))

            ConstPixelDims = (int(images[0].Rows), int(images[0].Columns), len(images))
            ArrayDicom = np.zeros(ConstPixelDims, dtype=np.float64)
    

            for dim2, img in enumerate(images):

                ArrayDicom[:, :, dim2] = rescale_image(images[1], img.pixel_array)
    
            if(i == 0):
                conventional = ArrayDicom
            elif(i==1):
             kedge = redefine_window(ArrayDicom)
             
        #Instantiate a timepoint class object and append it to the acquisition array
        self.acquisition.append(Timepoint(t, conventional, kedge))
    #def import masks from 3d slicer

def rescale_image(medical_image, image):
    """
    The raw intensity values of DICOM images don't correspond to either HU or mg/ml scale so we must convert them with this simple linear transformation
    """
    intercept = medical_image.RescaleIntercept
    slope = medical_image.RescaleSlope
    rescaled_image = image*slope + intercept

    return rescaled_image

def redefine_window(image):
    """
    Although not currently amazingly useful, I find it visually helpful to remove negative concentrations from my K-edges and have a framework for altering the intensity window
    of the conventional CT images.
    """
    window_center = image.mean()

    # K-edge specific windowing
    img_min = 0
    img_max = window_center + (200 // 2)
   
    window_image = image
    window_image[window_image < img_min] = img_min
    window_image[window_image > img_max] = img_max
    
    return window_image

# add ROI
# store measurements in a dictionary
# calculate functional information based on ROI

class Timepoint:
    def __init__(self, time, conventional, kedge):
        self.time = time #identifier
        self.conventional = conventional # 3D array of conventional images
        self.kedge = kedge # 3D array of kedge images


#class Visualize:
#    def __init__(self, sample):