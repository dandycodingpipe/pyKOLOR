import pydicom
import os
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, Button, LassoSelector
from matplotlib.path import Path
from skimage.morphology import binary_dilation, disk
import pandas as pd
import re
from multiprocessing import Pool, cpu_count


from multiprocessing import Pool, cpu_count
import os
import pydicom
import numpy as np

class Sample:
    """
    Oh yeah baby we are doing OOP for package dev. now! 
    
    The sample class has the timepoint attribute which consists of both conventional and kedge 3d arrays
    for a given timepoint. 

    """
    def __init__(self, animal_id):
        self.animal_id = str(animal_id)
        self.acquisition = [] #we are in 4D, regardless if we want to look at conventional or Kedge, it will always correspond to a timepoint in acquisition
        self.fetch_data(animal_id)

    def rm_acquisition(self, idx):
        del self.acquisition[idx]
        return self.acquisition

    def fetch_data(self, animal_id):
        """
        Using just the rabbit ID, this function will automatically find the relevant directory
        and add all timepoints from that directory.
        """
        
        # move this outside
        base_path = f"D:\copyRaw\Rabbit_AGUIX_" + animal_id
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
        conventional = None
        kedge = None
        # move outside 
        
        suffixes = ["Conventional", r"Spectral/k_gadolinium"]
        time = t

        for suffix in suffixes:
            specific_path = os.path.join(base_path, directories[t], suffix)

            # Initialize the list to collect DICOM file paths
            DCMFiles = []
            for dirName, _, fileList in os.walk(specific_path):
                for filename in fileList:
                    if filename.lower().endswith('.dcm'):
                        DCMFiles.append(os.path.join(dirName, filename))

            # Check if no DICOM files were found after attempting to collect them
            if not DCMFiles:
                print(f"No DICOM files found in {specific_path}.")
                continue  # Skip the rest of this iteration and proceed with the next suffix

            print(f"{suffix} file {t+1} total DICOM files found: {len(DCMFiles)}")

            images = [pydicom.dcmread(f) for f in DCMFiles]
            images.sort(key=lambda x: float(x.ImagePositionPatient[2]))

            ConstPixelDims = (int(images[0].Rows), int(images[0].Columns), len(images))
            ArrayDicom = np.zeros(ConstPixelDims, dtype=np.float64)
    

            for dim2, img in enumerate(images):

                ArrayDicom[:, :, dim2] = rescale_image(images[1], img.pixel_array)
    
            if(suffix == "Conventional"):
                conventional = ArrayDicom
            elif(suffix == "Spectral/k_gadolinium"):
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
    def __init__(self, sample, init_slice_index = 50):
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

class vesselDiameter:
    """
    This class seeks to extend to simple Viewer class by adding vessel diameter measuring functionalities. A user can manually segment a vessel of interest and generate information aout its signal, noise, and CNR in conventional and Kedge. Optionally, previously created masks can be reloaded for quality assessment instead.
    """
    def __init__(self, sample, path = None):
        self.sample = sample
        self.path = path
        self.data = pd.DataFrame(columns=["Signal_HU", "Noise_HU", "CNR_HU", "Signal_Kedge", "Noise_Kedge", "CNR_Kedge"])
        self.masks = []
        self.mask_overlay = None

        #if the user gives a mask, just load it instead of doing the lassos stuff
        if path:
            match = re.search(r'\d{2,3}', path)
            self.viewer = Viewer(sample, int(match.group(0)))
            self.masks.append(np.load(path))
        else:    
            # Use LassoSelector on the viewer's current axes
            self.viewer = Viewer(sample)
            self.instruction_text = None
            self.lasso = LassoSelector(self.viewer.ax, onselect=self.onselect, useblit=True)
            self.verts = None
            # Connect the key press event
            self.cid = self.viewer.fig.canvas.mpl_connect('key_press_event', self.on_key_press)
            
        # Set up the button for showing/hiding the mask
        self.mask_button = Button(plt.axes([0.4, 0.225, 0.2, 0.075]), 'Toggle Mask', color='lightblue', hovercolor='0.975')
        self.mask_button.on_clicked(self.toggleMask)

    def onselect(self, verts):
        self.verts = verts
        # Remove any existing instruction text
        if self.instruction_text is not None:
            self.instruction_text.remove()
        # Add new instruction text
        self.instruction_text = self.viewer.ax.text(0.5, 0.01, "Press 'Enter' to confirm, 'Esc' to cancel.",
                                                     transform=self.viewer.ax.transAxes,
                                                     horizontalalignment='center',
                                                     bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
        plt.draw()  # Make sure the drawing is updated

    def on_key_press(self, event):
        if event.key == 'enter' and self.verts is not None:
            
            # Remove instruction text and lasso selector after choice is confirmed
            if self.instruction_text is not None:
                self.instruction_text.remove()
                self.instruction_text = None  # Reset the reference
            
            plt.draw()  # Update the drawing to reflect changes
            self.lasso.active = False
            self.process_selection(self.verts)
            # Disconnect keypress as well
            self.viewer.fig.canvas.mpl_disconnect(self.cid)

        elif event.key == 'escape':
            if self.instruction_text is not None:
                self.instruction_text.set_text("Selection cancelled. Make a new selection.")
                plt.draw()

    def vesselMeasurements(self, sample, mask, washer_disk):

        measurements = []

        for i in range(len(sample.acquisition)):
            conventional = sample.acquisition[i].conventional[:, :, self.viewer.slice_slider.val]
        
            # Calculate metrics for conventional and k-edge images
            signal_HU, noise_HU = np.mean(conventional[mask]), np.mean(conventional[washer_disk])
            CNR_HU = (signal_HU - noise_HU) / np.std(conventional[washer_disk])

            kedge = sample.acquisition[i].kedge[:, :, self.viewer.slice_slider.val] if sample.acquisition[i].kedge is not None else None
        
            if kedge is None or (isinstance(kedge, np.ndarray) and np.isnan(kedge).any()):
                signal_Kedge, noise_Kedge, CNR_Kedge = np.nan, np.nan, np.nan
            
            else:
                kedge = sample.acquisition[i].kedge[:, :, self.viewer.slice_slider.val]
                signal_Kedge, noise_Kedge = np.mean(kedge[mask]), np.mean(kedge[washer_disk])
                CNR_Kedge = (signal_Kedge - noise_Kedge) / np.std(kedge[washer_disk])
        
            # Append metrics to the list
            measurements.append([signal_HU, noise_HU, CNR_HU, signal_Kedge, noise_Kedge, CNR_Kedge])
    
        # Convert measurements list to a DataFrame and append it to self.data
        new_data = pd.DataFrame(measurements, columns=self.data.columns)
        self.data = pd.concat([self.data, new_data], ignore_index=True)
        print(self.data)
            
    def process_selection(self, verts):
        print("Processing the selection...")

        #mask_file = input("Name the file to store the mask in. feature_sample_slice:")
        # Create a Path object from the lasso vertices
        lasso_path = Path(verts)

        # Generate a mask for the selected region and an external washer mask for additional measurements
        nx, ny = self.viewer.image_display.get_array().shape[1], self.viewer.image_display.get_array().shape[0]
        x, y = np.meshgrid(np.arange(nx), np.arange(ny))
        x, y = x.flatten(), y.flatten()
        points = np.vstack((x,y)).T
        mask = lasso_path.contains_points(points).reshape((ny,nx))

        dilated_mask = binary_dilation(mask, disk(5))
        washer_disk = dilated_mask & ~mask
        
            # Create an overlay image where the selected region and washer are highlighted
        overlay = np.zeros((*mask.shape, 4))  # Create an RGBA image for overlay
        overlay[mask, :] = [1, 0, 0, 0.5]  # Red with transparency for the selected region
        overlay[washer_disk, :] = [0, 0, 1, 0.5]  # Blue with transparency for the washer region

        if not self.masks:  # If masks list is empty
            self.masks.append(overlay)  # Store the first overlay
        else:
            self.masks[0] = overlay  # Update the existing overlay
        
        np.save("mask.npy", self.masks[0])
    
        # Display the overlay on top of the original image
        #self.viewer.ax.imshow(overlay, extent=self.viewer.image_display.get_extent())

        print(self.viewer.slice_slider.val)

        #Loop through all images and calculate values
        self.vesselMeasurements(self.sample, mask, washer_disk)
        #df = input("Please name the csv with measurements: feature_sample_date")
        self.data.to_csv("dataframe.csv", index = False)
    
        # Force a redraw of the figure to update the display
        self.viewer.fig.canvas.draw_idle()
        
    def toggleMask(self, event):
        # Ensures that if a mask overlay exists, its visibility is toggled
        if self.mask_overlay:
            isVisible = not self.mask_overlay.get_visible()
            self.mask_overlay.set_visible(isVisible)
            self.viewer.fig.canvas.draw_idle()  # Refresh the display to show changes
        else:
            # If no overlay exists (likely because path was None and no selection was made yet),
            # call showMask() to potentially create and show the overlay
            self.showMask()

    def showMask(self):
        # If there's a mask to show, ensure it's properly displayed or updated
        if self.masks:
            if self.mask_overlay:
                # If an overlay already exists, update its data
                self.mask_overlay.set_data(self.masks[0])
            else:
                # Create the overlay with the mask data
                self.mask_overlay = self.viewer.ax.imshow(self.masks[0], extent=self.viewer.image_display.get_extent(), alpha=0.5)
                # Ensure it's visible
                self.mask_overlay.set_visible(True)
            self.viewer.fig.canvas.draw_idle()  # Refresh the display

class VesselAnalyzer:
    def __init__(self, sample, path=None):
        self.sample = sample
        self.path = path
        self.data = pd.DataFrame(columns=["Signal_HU", "Noise_HU", "Signal_std" , "CNR_HU", "Signal_Kedge", "Noise_Kedge", "Kedge_std", "CNR_Kedge"])
        self.masks = []
        self.mask_overlay = None

        self.viewer = Viewer(sample)  # Assuming Viewer is defined elsewhere
        self.cid_click = self.viewer.fig.canvas.mpl_connect('button_press_event', self.on_mouse_click)

    def on_mouse_click(self, event):
        if event.inaxes == self.viewer.ax:
            self.add_circular_roi(event.xdata, event.ydata)
            plt.draw()

    def add_circular_roi(self, x_center, y_center):
        radius = 2.5  # For a diameter of 5 pixels
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
        
            if kedge is None or (isinstance(kedge, np.ndarray) and np.isnan(kedge).any()):
                signal_Kedge, noise_Kedge, CNR_Kedge = np.nan, np.nan, np.nan
            
            else:
                kedge = sample.acquisition[i].kedge[:, :, self.viewer.slice_slider.val]
                signal_Kedge, noise_Kedge, kedge_Std = np.mean(kedge[circular_mask]), np.mean(kedge[washer_mask]), np.std(kedge[circular_mask])
                CNR_Kedge = (signal_Kedge - noise_Kedge) / np.std(kedge[washer_mask])
        
            # Append metrics to the list
            measurements.append([signal_HU, noise_HU, signal_Std, CNR_HU, signal_Kedge, noise_Kedge, kedge_Std, CNR_Kedge])
    
        # Convert measurements list to a DataFrame and append it to self.data
        new_data = pd.DataFrame(measurements, columns=self.data.columns)
        self.data = pd.concat([self.data, new_data], ignore_index=True)
        print(self.data)
        self.data.to_csv("dataframe.csv", index = False)

  
class draw2D:
    def __init__(self, sample, path=None):
        self.sample = sample
        self.path = path
        self.data = pd.DataFrame(columns=["Mean_HU", "Std_HU", "Median_HU", "Min_HU", "Max_HU", "IQ1_HU", "IQ3_HU", 
                                          "Mean_Kedge", "Std_Kedge", "Median_Kedge", "Min_Kedge", "Max_Kedge", "IQ1_Kedge", "IQ3_Kedge"])
        self.masks = []
        self.mask_overlay = None
        self.g_key_pressed = False

        self.viewer = Viewer(sample)  # Assuming Viewer is defined elsewhere
        self.cid_click = self.viewer.fig.canvas.mpl_connect('button_press_event', self.on_mouse_click)
        self.cid_keypress = self.viewer.fig.canvas.mpl_connect('key_press_event', self.on_key_press)
        self.cid_keyrelease = self.viewer.fig.canvas.mpl_connect('key_release_event', self.on_key_release)

    def on_key_press(self, event):
        if event.key == 'g':
            self.g_key_pressed = True

    def on_key_release(self, event):
        if event.key == 'g':
            self.g_key_pressed = False

    def on_mouse_click(self, event):
        if event.inaxes == self.viewer.ax and event.button == 1 and self.g_key_pressed:
            self.add_circular_roi(event.xdata, event.ydata)
            plt.draw()

    def add_circular_roi(self, x_center, y_center):
        radius = 2.5  # For a diameter of 5 pixels

        # Create circular ROI mask
        nx, ny = self.viewer.image_display.get_array().shape[1], self.viewer.image_display.get_array().shape[0]
        y, x = np.ogrid[:ny, :nx]
        circular_mask = (x - x_center) ** 2 + (y - y_center) ** 2 <= radius ** 2

        # Process the mask and calculate statistics
        self.process_selection(circular_mask, self.sample)

        # Optionally, create an overlay image to show the ROI
        if self.mask_overlay is not None:
            self.mask_overlay.remove()
        self.mask_overlay = self.viewer.ax.imshow(circular_mask, cmap='coolwarm', alpha=0.5)
        self.viewer.fig.canvas.draw_idle()

    def process_selection(self, circular_mask, sample):
        # Placeholder for image data, replace with actual image data
        measurements = []
        image_data = self.viewer.image_display.get_array()

        # Compute statistics for the circular ROI
        for i in range(len(sample.acquisition)):
            conventional = sample.acquisition[i].conventional[:, :, self.viewer.slice_slider.val]
            kedge = sample.acquisition[i].kedge[:, :, self.viewer.slice_slider.val] if sample.acquisition[i].kedge is not None else None

            mean_HU = np.mean(conventional[circular_mask])
            std_HU = np.std(conventional[circular_mask])
            median_HU = np.median(conventional[circular_mask])
            min_HU = np.min(conventional[circular_mask])
            max_HU = np.max(conventional[circular_mask])
            iq1_HU = np.percentile(conventional[circular_mask], 25)
            iq3_HU = np.percentile(conventional[circular_mask], 75)

            if kedge is None or (isinstance(kedge, np.ndarray) and np.isnan(kedge).any()):
                mean_Kedge, std_Kedge, median_Kedge, min_Kedge, max_Kedge, iq1_Kedge, iq3_Kedge = [np.nan] * 7
            else:
                mean_Kedge = np.mean(kedge[circular_mask])
                std_Kedge = np.std(kedge[circular_mask])
                median_Kedge = np.median(kedge[circular_mask])
                min_Kedge = np.min(kedge[circular_mask])
                max_Kedge = np.max(kedge[circular_mask])
                iq1_Kedge = np.percentile(kedge[circular_mask], 25)
                iq3_Kedge = np.percentile(kedge[circular_mask], 75)

            # Append metrics to the list
            measurements.append([mean_HU, std_HU, median_HU, min_HU, max_HU, iq1_HU, iq3_HU,
                                 mean_Kedge, std_Kedge, median_Kedge, min_Kedge, max_Kedge, iq1_Kedge, iq3_Kedge])

        # Convert measurements list to a DataFrame and append it to self.data
        new_data = pd.DataFrame(measurements, columns=self.data.columns)
        self.data = pd.concat([self.data, new_data], ignore_index=True)
        print(self.data)
        self.data.to_csv("dataframe.csv", index=False)

