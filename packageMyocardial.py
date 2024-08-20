<<<<<<< HEAD
import pydicom
import os
import numpy as np
import matplotlib.pyplot as plt

def load3dStack(rabbit, kedge):
    """
    Interactively load DICOM files from the project hardrive into a 3D numpy array.
    """
    base_path = f"D:\copyRaw\Rabbit_AGUIX_{rabbit}"
    directories = [d for d in os.listdir(base_path) if os.path.isdir(os.path.join(base_path, d))]
    directories.sort()

    print("Available directories:")
    for i, directory in enumerate(directories):
        print(f"{i}: {directory}")

    choice_index = int(input("Enter the index of the directory to choose: "))
    if 0 <= choice_index < len(directories):
        specific_path = os.path.join(base_path, directories[choice_index])
    else:
        print("Invalid selection, exiting.")
        return None

    suffix = "Spectral\k_gadolinium" if kedge else "Conventional"
    PathDicom = os.path.join(specific_path, suffix)
    print(f"\nPath to DICOM files: {PathDicom}")

    DCMFiles = []
    for dirName, _, fileList in os.walk(PathDicom):
        for filename in fileList:
            if filename.lower().endswith('.dcm'):
                DCMFiles.append(os.path.join(dirName, filename))

    if not DCMFiles:
        print("No DICOM files found in the specified path.")
        return None

    print(f"Total DICOM files found: {len(DCMFiles)}")

    images = [pydicom.dcmread(f) for f in DCMFiles]
    images.sort(key=lambda x: float(x.ImagePositionPatient[2]))

    ConstPixelDims = (int(images[0].Rows), int(images[0].Columns), len(images))
    ArrayDicom = np.zeros(ConstPixelDims, dtype=np.float64)
    
    choice = ""
    if(kedge == False):
        choice = input("Choose window (all, abdomen, bone, chest, lungs): ").lower()

    for i, img in enumerate(images):

        ArrayDicom[:, :, i] = redefine_window(rescale_image(images[1], img.pixel_array), kedge, choice)

    return ArrayDicom


def rescale_image(medical_image, image):
    """
    The raw intensity values of DICOM images don't correspond to either HU or mg/ml scale so we must convert them with this simple linear transformation
    """
    intercept = medical_image.RescaleIntercept
    slope = medical_image.RescaleSlope
    rescaled_image = image*slope + intercept

    return rescaled_image

def redefine_window(image, kedge, choice):
    """
    Although not currently amazingly useful, I find it visually helpful to remove negative concentrations from my K-edges and have a framework for altering the intensity window
    of the conventional CT images.
    """
    window_center = image.mean()

    # Default values in case they are not set in the conditions below
    img_min, img_max = image.min(), image.max()
 
    if kedge:
        # K-edge specific windowing
        img_min = 0
        img_max = window_center + (200 // 2)
    else:
        # User choice for windowing
        
        predefined_windows = {
            "all": {"WL": window_center, "WW": 400},
            "abdomen": {"WL": 60, "WW": 400},
            "bone": {"WL": 700, "WW": 2000},
            "chest": {"WL": 40, "WW": 400},
            "lungs": {"WL": -600, "WW": 1500}
        }

        if choice in predefined_windows:
            WL = predefined_windows[choice]["WL"]
            WW = predefined_windows[choice]["WW"]
            img_min = WL - WW // 2
            img_max = WL + WW // 2
        else:
            pass

    
    window_image = image
    window_image[window_image < img_min] = img_min
    window_image[window_image > img_max] = img_max
    return window_image
    


class ImageSlider:
    def __init__(self, image_arrays):
        self.image_arrays = image_arrays
        self.current_index = 0

        self.fig, self.ax = plt.subplots()
        plt.subplots_adjust(bottom=0.25)

        self.img_plot = self.ax.imshow(self.image_arrays[self.current_index], cmap='gray')

        ax_slider = plt.axes([0.25, 0.1, 0.65, 0.03], facecolor='lightgoldenrodyellow')
        self.slider = Slider(ax_slider, 'Image', 0, len(self.image_arrays) - 1, valinit=0, valstep=1)
        self.slider.on_changed(self.update_image)

    def update_image(self, val):
        self.current_index = int(self.slider.val)
        self.img_plot.set_array(self.image_arrays[self.current_index])
        self.fig.canvas.draw_idle()
=======
import pydicom
import os
import numpy as np
import matplotlib.pyplot as plt

def load3dStack(rabbit, kedge):
    """
    Interactively load DICOM files from the project hardrive into a 3D numpy array.
    """
    base_path = f"D:\copyRaw\Rabbit_AGUIX_{rabbit}"
    directories = [d for d in os.listdir(base_path) if os.path.isdir(os.path.join(base_path, d))]
    directories.sort()

    print("Available directories:")
    for i, directory in enumerate(directories):
        print(f"{i}: {directory}")

    choice_index = int(input("Enter the index of the directory to choose: "))
    if 0 <= choice_index < len(directories):
        specific_path = os.path.join(base_path, directories[choice_index])
    else:
        print("Invalid selection, exiting.")
        return None

    suffix = "Spectral\k_gadolinium" if kedge else "Conventional"
    PathDicom = os.path.join(specific_path, suffix)
    print(f"\nPath to DICOM files: {PathDicom}")

    DCMFiles = []
    for dirName, _, fileList in os.walk(PathDicom):
        for filename in fileList:
            if filename.lower().endswith('.dcm'):
                DCMFiles.append(os.path.join(dirName, filename))

    if not DCMFiles:
        print("No DICOM files found in the specified path.")
        return None

    print(f"Total DICOM files found: {len(DCMFiles)}")

    images = [pydicom.dcmread(f) for f in DCMFiles]
    images.sort(key=lambda x: float(x.ImagePositionPatient[2]))

    ConstPixelDims = (int(images[0].Rows), int(images[0].Columns), len(images))
    ArrayDicom = np.zeros(ConstPixelDims, dtype=np.float64)
    
    choice = ""
    if(kedge == False):
        choice = input("Choose window (all, abdomen, bone, chest, lungs): ").lower()

    for i, img in enumerate(images):

        ArrayDicom[:, :, i] = redefine_window(rescale_image(images[1], img.pixel_array), kedge, choice)

    return ArrayDicom


def rescale_image(medical_image, image):
    """
    The raw intensity values of DICOM images don't correspond to either HU or mg/ml scale so we must convert them with this simple linear transformation
    """
    intercept = medical_image.RescaleIntercept
    slope = medical_image.RescaleSlope
    rescaled_image = image*slope + intercept

    return rescaled_image

def redefine_window(image, kedge, choice):
    """
    Although not currently amazingly useful, I find it visually helpful to remove negative concentrations from my K-edges and have a framework for altering the intensity window
    of the conventional CT images.
    """
    window_center = image.mean()

    # Default values in case they are not set in the conditions below
    img_min, img_max = image.min(), image.max()
 
    if kedge:
        # K-edge specific windowing
        img_min = 0
        img_max = window_center + (200 // 2)
    else:
        # User choice for windowing
        
        predefined_windows = {
            "all": {"WL": window_center, "WW": 400},
            "abdomen": {"WL": 60, "WW": 400},
            "bone": {"WL": 700, "WW": 2000},
            "chest": {"WL": 40, "WW": 400},
            "lungs": {"WL": -600, "WW": 1500}
        }

        if choice in predefined_windows:
            WL = predefined_windows[choice]["WL"]
            WW = predefined_windows[choice]["WW"]
            img_min = WL - WW // 2
            img_max = WL + WW // 2
        else:
            pass

    
    window_image = image
    window_image[window_image < img_min] = img_min
    window_image[window_image > img_max] = img_max
    return window_image
    


class ImageSlider:
    def __init__(self, image_arrays):
        self.image_arrays = image_arrays
        self.current_index = 0

        self.fig, self.ax = plt.subplots()
        plt.subplots_adjust(bottom=0.25)

        self.img_plot = self.ax.imshow(self.image_arrays[self.current_index], cmap='gray')

        ax_slider = plt.axes([0.25, 0.1, 0.65, 0.03], facecolor='lightgoldenrodyellow')
        self.slider = Slider(ax_slider, 'Image', 0, len(self.image_arrays) - 1, valinit=0, valstep=1)
        self.slider.on_changed(self.update_image)

    def update_image(self, val):
        self.current_index = int(self.slider.val)
        self.img_plot.set_array(self.image_arrays[self.current_index])
        self.fig.canvas.draw_idle()
>>>>>>> 2b78048e44ec8e2995233c6d28a6734d7a3eecb7
