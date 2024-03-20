import pydicom
import os
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, Button

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

            print(f"{suffix} file {t+1} total DICOM files found: {len(DCMFiles)}")

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


class Viewer:
    """
    A Viewer class for interactive visualization in Jupyter notebooks using %matplotlib widget.
    
    Usage requires:
    - %matplotlib widget to be called in the notebook.
    - matplotlib and ipympl to be installed.
    """
    def __init__(self, sample):
        self.sample = sample
        self.init_time_point = 0
        self.init_slice_index = 50
        self.image_type = 'kedge'  # Toggle between 'kedge' and 'conventional'

        self.fig, self.ax = plt.subplots(figsize=(10, 10))
        plt.subplots_adjust(left=0.25, bottom=0.3)
        self.ax.axis('off')  # Hide the axis for a cleaner look

        # Display the initial image
        self.image_display = self.ax.imshow(self.get_image(self.init_time_point, self.init_slice_index), cmap='gray')

        # Time point slider
        ax_time = plt.axes([0.25, 0.15, 0.65, 0.03], facecolor='lightgray')
        self.time_slider = Slider(ax_time, 'Time Point', 0, len(self.sample.acquisition)-1, valinit=self.init_time_point, valstep=1)

        # Slice index slider
        ax_slice = plt.axes([0.05, 0.25, 0.0225, 0.63], facecolor='lightgray')
        self.slice_slider = Slider(ax_slice, 'Slice Index', 0, self.get_slice_max(), valinit=self.init_slice_index, valstep=1, orientation='vertical')

        # View switch button
        ax_button = plt.axes([0.4, 0.025, 0.2, 0.075])
        self.button = Button(ax_button, 'Switch View', color='lightblue', hovercolor='0.975')

        # Set up event handlers
        self.time_slider.on_changed(self.update)
        self.slice_slider.on_changed(self.update)
        self.button.on_clicked(self.switch_image_type)

        plt.show()

    def get_image(self, time_point, slice_index):
        """Retrieve the image for the given time point and slice index."""
        return getattr(self.sample.acquisition[time_point], self.image_type)[:, :, slice_index]

    def get_slice_max(self):
        """Get the maximum slice index for the current image type and time point."""
        return getattr(self.sample.acquisition[0], self.image_type).shape[2] - 1

    def update(self, val):
        """Update the displayed image based on slider values."""
        time_point = int(self.time_slider.val)
        slice_index = int(self.slice_slider.val)
        new_image = self.get_image(time_point, slice_index)
        self.image_display.set_data(new_image)
        self.image_display.set_clim(vmin=new_image.min(), vmax=new_image.max())  # Adjust display range dynamically
        self.fig.canvas.draw_idle()

    def switch_image_type(self, event):
        """Switch between 'kedge' and 'conventional' image types."""
        self.image_type = 'conventional' if self.image_type == 'kedge' else 'kedge'
        self.slice_slider.valmax = self.get_slice_max()  # Adjust the max slice index for the new image type
        self.update(None)  # Update the display to reflect the change