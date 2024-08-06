
#pySPCCT is a package that enables quick conventional and spectral data loading, viewing, and analysis
import pandas as pd
import os
import pydicom
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, Button, LassoSelector
import re

class Timepoint:
    def __init__(self, time, conventional, iodine, kedge):
        self.time = time #identifier
        self.conventional = conventional # 3D array of conventional images
        self.kedge = kedge # 3D array of kedge images
        self.iodine = iodine 

class Sample:
    """
    The sample class is pretty self explanatory. It holds all of the data for a single sample (conventional, kedge, iodine) in an acquisition array that separates groups and separates data according to their timepoint.
    """
    
    #TODO: remove path outside to yaml file
    def __init__(self, study_path, sample_idx):
        self.sample_id = str(sample_idx)
        
        self.allData = False #boolean specifying whether you want all spectral data loaded or just k-edge and iodine contrast images
        self.acquisition = [] #acquisition is an array that will hold timepoint class instances
        self.study_path = study_path
        self.fetch_data(study_path, sample_idx)
    
    def rm_timepoint(self, idx):
        del self.acquisition[idx]
        return self.acquisition
    
<<<<<<< HEAD
    def extract_number(self, filename):
        """
        Extracts the first sequence of digits from a given filename.
        """
        import re
        match = re.search(r"\d+", filename)
        return int(match.group()) if match else 0
    
=======
    
    #TODO: remove from this class
>>>>>>> f1472315891d395ab97823091f5182585c285c24
    def fetch_data(self, study_path, sample_idx):
        """
        This function is the bread and butter of the sample class. It pulls your data according to the desired study and the desired sample.
        """
        base_path = study_path + sample_idx
        # ex. D:\copyRaw\Rabbit_AGuIX or D:\copyRaw\Phantom_XeGd
        directories = [d for d in os.listdir(base_path) if os.path.isdir(os.path.join(base_path, d))]
        #directories.sort()
        directories.sort(key=self.extract_number)

        print(f"Available directories:")
        for i, directory in enumerate(directories):
            print(f"{i}: {directory}")

        #create a timepoint for each unique study in the base path
        for t, acquisitions in enumerate(directories):
            self.add_timepoint(base_path, directories, t)
        
    def add_timepoint(self, base_path, directories, t):
        """
        This function losely uses timepoint to describe multiple studies being run for the same sample. This could be time or just different acquisitions. You have the allData option which 
        allows you to pull all dicom data corresponding to a path or just the interesting ones for biodistribution analysis.
        """
        conventional = None
        kedge = None
        iodine = None
        time = t
    
        #TODO: move to its own yaml file
        #suffixes = ["Conventional", r"Spectral/b_dlbasephoto", r"Spectral/b_dlbasescatter",  r"Spectral/k_gadolinium",  r"Spectral/b_dlbasenoise", r"Spectral/b_dlbasescatter", r"Spectral/b_iodine",  r"Spectral/b_water", r"Spectral/n_dlbase_noise"]
        suffixes = ["Conventional", r"Spectral/k_gadolinium", r"Spectral/b_iodine"]

            # Step 1. creating a list of all necessary file paths for pulling
        
        
        # TODO: move path stuff outside where can be
        for suffix in suffixes:
            specific_path = os.path.join(base_path, directories[t], suffix)

            DCMfiles = []
            for dirName, _, fileList in os.walk(specific_path):
                for filename in fileList:
                    if filename.lower().endswith(".dcm"):
                        DCMfiles.append(os.path.join(dirName, filename))
            
            if not DCMfiles:
                print(f"No DICOM files found in {specific_path}")
                continue
            
            print(f"{suffix} file {t+1} total DICOM files found: {len(DCMfiles)}")

            # Step 2. loading dicoms 
            images = [pydicom.dcmread(f) for f in DCMfiles]
            images.sort(key = lambda x: float(x.ImagePositionPatient[2]))

            ConstPixelDims = (int(images[0].Rows), int(images[0].Columns), len(images))
            ArrayDicom = np.zeros(ConstPixelDims, dtype = np.float64)

            for dim2, img in enumerate(images):
                ArrayDicom[:,:, dim2] = rescale_image(images[1], img.pixel_array)
            
            #I like to remove negative concentrations from K-edge images. It makes the visualization much better.
            if(suffix == "Conventional"):
                conventional = ArrayDicom

            elif(suffix == "Spectral/k_gadolinium"):
                kedge = redefine_window(ArrayDicom)
            
            elif(suffix == "Spectral/b_iodine"):
                iodine = redefine_window(ArrayDicom)

        #Instantiate a timepoint class object and append it to the acquisition array
        self.acquisition.append(Timepoint(t, conventional, iodine, kedge))

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

class Viewer:
    """
    A viewer class that allows the user to visualize both K-edge and Conventional images in one tool. It allows switching between planes and it is initialized in the correct HU units upons initializations but
    be mindful that when adjusting WL and WW this information is lost.
    """
    def __init__(self, sample, init_slice_index = 1):
        self.sample = sample
        self.init_time_point = 0
        self.init_slice_index = init_slice_index
        self.image_type = 'conventional'  # Initial image type
        self.init_WL = 40
        self.init_WW = 400
        self.plan = "axial"

        #Initial figure display
        self.fig, self.ax = plt.subplots(figsize=(10, 10))
        plt.subplots_adjust(left=0.25, bottom=0.3, right=0.75)  # Adjust the right margin to make space for the sliders
        self.ax.axis('off')
        self.ax.set_title(f"Current View: {self.image_type.capitalize()}")
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
            return getattr(self.sample.acquisition[self.time_slider.val], self.image_type).shape[2] - 1
        else:
            return getattr(self.sample.acquisition[self.time_slider.val], self.image_type).shape[1] - 1

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
        
        if self.image_type == "conventional":
            self.image_type = "iodine"
            
        elif self.image_type == "iodine":
            self.image_type = "kedge"
        else:
            self.image_type = "conventional"
        
        self.slice_slider.valmax = self.get_slice_max()
        self.ax.set_title(f"Current View: {self.image_type.capitalize()}")
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

class VesselAnalyzer:
        def __init__(self, sample, path=None):
            self.sample = sample
            self.path = path
            self.data = pd.DataFrame(columns=["Signal_HU", "Noise_HU", "Signal_std" , "SNR_HU", "Signal_Kedge", "Noise_Kedge", "Kedge_std", "SNR_Kedge", "Signal_Iodine", "Noise_Iodine", "Iodine_std", "CNR_Iodine"])
            self.masks = []
            self.mask_overlay = None

            self.viewer = Viewer(sample)  # Assuming Viewer is defined elsewhere
            self.cid_click = self.viewer.fig.canvas.mpl_connect('button_press_event', self.on_mouse_click)

        def on_mouse_click(self, event):
            if event.inaxes == self.viewer.ax and event.button == 1 and event.key == 'g':
                self.add_circular_roi(event.xdata, event.ydata)
                plt.draw()

        def add_circular_roi(self, x_center, y_center):
            radius = 5  # For a diameter of 5 pixels
            washer_radius = 4.5  # For a washer with an outer diameter of 9 pixels (4.5 + 2.5)

            # Create circular ROI and washer mask
            nx, ny = self.viewer.image_display.get_array().shape[1], self.viewer.image_display.get_array().shape[0]
            y, x = np.ogrid[:ny, :nx]
            circular_mask = (x - x_center) ** 2 + (y - y_center) ** 2 <= radius ** 2
            washer_mask = (x - x_center) ** 2 + (y - y_center) ** 2 <= washer_radius ** 2
            washer_mask ^= circular_mask  # Remove the inner circular ROI

            # Process the mask and washer, calculate statistics
            self.process_selection(circular_mask, washer_mask, self.sample)

            # Optionally, create an overlay image to show the ROI
            if self.mask_overlay is not None:
                self.mask_overlay.remove()
            self.mask_overlay = self.viewer.ax.imshow(circular_mask + washer_mask, cmap='coolwarm', alpha=0.5)
            self.viewer.fig.canvas.draw_idle()

        def process_selection(self, circular_mask, washer_mask, sample):
            # Placeholder for image data, replace with actual image data
            measurements = []
            image_data = self.viewer.image_display.get_array()

            # Compute statistics for the circular ROI
            signal_HU = np.mean(image_data[circular_mask])
            noise_HU = np.mean
    
            for i in range(len(sample.acquisition)):
                conventional = sample.acquisition[i].conventional[:, :, self.viewer.slice_slider.val]
        
                # Calculate metrics for conventional and k-edge images
                signal_HU, noise_HU, signal_Std = np.mean(conventional[circular_mask]), np.mean(conventional[washer_mask]), np.std(conventional[circular_mask])
                CNR_HU = (signal_HU - noise_HU) / np.std(conventional[washer_mask])

                kedge = sample.acquisition[i].kedge[:, :, self.viewer.slice_slider.val] if sample.acquisition[i].kedge is not None else None
                iodine = sample.acquisition[i].iodine[:, :, self.viewer.slice_slider.val] if sample.acquisition[i].iodine is not None else None
        
                if kedge is None or (isinstance(kedge, np.ndarray) and np.isnan(kedge).any()):
                    signal_Kedge, noise_Kedge, CNR_Kedge = np.nan, np.nan, np.nan
            
                else:
                    kedge = sample.acquisition[i].kedge[:, :, self.viewer.slice_slider.val]
                    signal_Kedge, noise_Kedge, kedge_Std = np.mean(kedge[circular_mask]), np.mean(kedge[washer_mask]), np.std(kedge[circular_mask])
                    CNR_Kedge = (signal_Kedge - noise_Kedge) / np.std(kedge[washer_mask])
                
                if iodine is None or (isinstance(iodine, np.ndarray) and np.isnan(iodine).any()):
                    signal_Iodine, noise_Iodine, Iodine_std = np.nan, np.nan, np.nan
            
                else:
                    iodine = sample.acquisition[i].iodine[:, :, self.viewer.slice_slider.val]
                    signal_Iodine, noise_Iodine, Iodine_std= np.mean(iodine[circular_mask]), np.mean(iodine[washer_mask]), np.std(iodine[circular_mask])
                    CNR_Iodine = (signal_Iodine- noise_Iodine) / np.std(iodine[washer_mask])
                # Append metrics to the list
                measurements.append([signal_HU, noise_HU, signal_Std, CNR_HU, signal_Kedge, noise_Kedge, kedge_Std, CNR_Kedge, signal_Iodine, noise_Iodine, Iodine_std, CNR_Iodine])
    
            # Convert measurements list to a DataFrame and append it to self.data
            new_data = pd.DataFrame(measurements, columns=self.data.columns)
            self.data = pd.concat([self.data, new_data], ignore_index=True)
            print(self.data)
            self.data.to_csv("dataframe.csv", index = False)