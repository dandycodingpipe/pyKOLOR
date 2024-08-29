import matplotlib as plt
from matplotlib.widgets import Slider, Button
import numpy as np

class Gui:
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