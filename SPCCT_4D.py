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
    A viewer class that allows the user to visualize both K-edge and Conventional images in one tool. It allows switching between planes and it is initialized in the correct HU units upons initializations but
    be mindful that when adjusting WL and WW this information is lost.
    """
    def __init__(self, sample):
        self.sample = sample
        self.init_time_point = 0
        self.init_slice_index = 50
        self.image_type = 'conventional'  # Initial image type
        self.init_WL = 40
        self.init_WW = 400
        self.plan = "axial"

        #Initial figure display
        self.fig, self.ax = plt.subplots(figsize=(10, 10))
        plt.subplots_adjust(left=0.25, bottom=0.3, right=0.75)  # Adjust the right margin to make space for the sliders
        self.ax.axis('off')
        self.image_display = self.ax.imshow(self.get_image(self.init_time_point, self.init_slice_index), cmap='gray')

        # Sliders
        self.time_slider = Slider(plt.axes([0.2, 0.15, 0.65, 0.03], facecolor='lightgray'), 't', 0, len(self.sample.acquisition)-1, valinit=self.init_time_point, valstep=1)
        self.slice_slider = Slider(plt.axes([0.05, 0.25, 0.0225, 0.63], facecolor='lightgray'), 'Z', 0, self.get_slice_max(), valinit=self.init_slice_index, valstep=1, orientation='vertical')
        self.win_level_slider = Slider(plt.axes([0.8, 0.25, 0.0225, 0.63], facecolor='lightgray'), 'WL', -1024, 3072, valinit=self.init_WL, orientation='vertical')
        self.win_width_slider = Slider(plt.axes([0.85, 0.25, 0.0225, 0.63], facecolor='lightgray'), 'WW', 1, 4096, valinit=self.init_WW, orientation='vertical')
        # Buttons
        self.button = Button(plt.axes([0.2, 0.025, 0.2, 0.075]), 'Switch View', color='lightblue', hovercolor='0.975')
        self.plan_button = Button(plt.axes([0.6, 0.025, 0.2, 0.075]), 'Switch Plane', color='lightblue', hovercolor='0.975')
    
        # Connect Event Handlers
        self.time_slider.on_changed(self.update)
        self.slice_slider.on_changed(self.update)
        self.win_level_slider.on_changed(self.update_windowing)
        self.win_width_slider.on_changed(self.update_windowing)
        self.button.on_clicked(self.switch_image_type)
        self.plan_button.on_clicked(self.switch_plane)

        plt.show()

    def get_image(self, time_point, slice_index):
        """
        Retrieve the 2D image depending on the desired plane: axial, sagittal, or coronal... This function is integral to initialization and updating the image being displayed on the figure.
        """
        if self.plan == "axial":
            return getattr(self.sample.acquisition[time_point], self.image_type)[:, :, slice_index]
        elif self.plan == "sagittal":
            return np.rot90(getattr(self.sample.acquisition[time_point], self.image_type)[:, slice_index, :])
        elif self.plan == "coronal":
            return np.rot90(getattr(self.sample.acquisition[time_point], self.image_type)[slice_index, :, :])


    def get_slice_max(self):
        if self.plan == "axial":
            return getattr(self.sample.acquisition[0], self.image_type).shape[2] - 1
        else:
            return getattr(self.sample.acquisition[0], self.image_type).shape[1] - 1

    def update(self, val):
        """
        To update the figure, we need to make a new image with the values present on the time slider and the slice slider. This is also going to update the contrast based on windowing adjustments
        """
        new_image = self.get_image(int(self.time_slider.val), int(self.slice_slider.val))
    
        if self.image_type == 'conventional':
            # Calculate and adjust window range for conventional images
            level = self.win_level_slider.val
            width = self.win_width_slider.val
            lower = level - (width / 2)
            upper = level + (width / 2)
        
            windowed_image = np.clip(new_image, lower, upper)
            self.image_display.set_clim(vmin=lower, vmax=upper)
        else:
            # For k-edge images, reset clim to the range of the image or a default range
            windowed_image = new_image
            self.image_display.set_clim(vmin=new_image.min(), vmax=new_image.max())

        # set_data changes the data from the old image to the new updated one
        self.image_display.set_data(windowed_image)
        self.fig.canvas.draw_idle()

    def update_windowing(self, val):
        if self.image_type == 'conventional':
            self.update(None)

    def switch_plane(self, event):
        # Cycle through the planes
        if self.plan == "axial":
            self.plan = "sagittal"
        elif self.plan == "sagittal":
            self.plan = "coronal"
        else:
            self.plan = "axial"

        # Update the slice_slider maximum based on the new plane
        self.slice_slider.valmax = self.get_slice_max()
        self.slice_slider.set_val(0)  # Reset to the first slice of the new plane

        # Update the image display
        self.update(None)

    def switch_image_type(self, event):
        self.image_type = 'conventional' if self.image_type == 'kedge' else 'kedge'
        self.slice_slider.valmax = self.get_slice_max()
        self.update(None)
        # Optionally, show/hide window sliders based on image type
        self.win_level_slider.ax.set_visible(self.image_type == 'conventional')
        self.win_width_slider.ax.set_visible(self.image_type == 'conventional')
        plt.draw()  # Redraw to update slider visibility

    def apply_mask(self):
        # Assuming self.image_display.get_array() returns the image data
        image_data = self.image_display.get_array()
        # Apply the mask
        masked_image = np.ma.masked_array(image_data, mask=~self.mask)

        # Now, display the masked image or perform further analysis
        # For example, to update the displayed image with the masked region highlighted:
        self.image_display.set_data(masked_image)
        self.fig.canvas.draw_idle()
    
    def display(self):
        """Display or redisplay the viewer figure."""
        self.fig.show()
