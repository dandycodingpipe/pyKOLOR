import pandas as pd
import numpy as np
import matplotlib as plt
from gui.gui import Gui


class DrawingOps:
        def __init__(self, sample, path=None):
            self.sample = sample
            self.path = path
            self.data = pd.DataFrame(columns=["Signal_HU", "Noise_HU", "Signal_std" , "SNR_HU", "Signal_Kedge", "Noise_Kedge", "Kedge_std", "SNR_Kedge", "Signal_Iodine", "Noise_Iodine", "Iodine_std", "CNR_Iodine"])
            self.masks = []
            self.mask_overlay = None

            self.gui = Gui(sample)  # Assuming Viewer is defined elsewhere
            self.cid_click = self.gui.fig.canvas.mpl_connect('button_press_event', self.on_mouse_click)

        def on_mouse_click(self, event):
            if event.inaxes == self.gui.ax and event.button == 1 and event.key == 'g':
                self.add_circular_roi(event.xdata, event.ydata)
                plt.draw()

        def add_circular_roi(self, x_center, y_center):
            radius = 5  # For a diameter of 5 pixels
            washer_radius = 4.5  # For a washer with an outer diameter of 9 pixels (4.5 + 2.5)

            # Create circular ROI and washer mask
            nx, ny = self.gui.image_display.get_array().shape[1], self.viewer.image_display.get_array().shape[0]
            y, x = np.ogrid[:ny, :nx]
            circular_mask = (x - x_center) ** 2 + (y - y_center) ** 2 <= radius ** 2
            washer_mask = (x - x_center) ** 2 + (y - y_center) ** 2 <= washer_radius ** 2
            washer_mask ^= circular_mask  # Remove the inner circular ROI

            # Process the mask and washer, calculate statistics
            self.process_selection(circular_mask, washer_mask, self.sample)

            # Optionally, create an overlay image to show the ROI
            if self.mask_overlay is not None:
                self.mask_overlay.remove()
            self.mask_overlay = self.gui.ax.imshow(circular_mask + washer_mask, cmap='coolwarm', alpha=0.5)
            self.gui.fig.canvas.draw_idle()

        def process_selection(self, circular_mask, washer_mask, sample):
            # Placeholder for image data, replace with actual image data
            measurements = []
            image_data = self.gui.image_display.get_array()

            # Compute statistics for the circular ROI
            signal_HU = np.mean(image_data[circular_mask])
            noise_HU = np.mean
    
            for i in range(len(sample.acquisition)):
                conventional = sample.acquisition[i].conventional[:, :, self.gui.slice_slider.val]
        
                # Calculate metrics for conventional and k-edge images
                signal_HU, noise_HU, signal_Std = np.mean(conventional[circular_mask]), np.mean(conventional[washer_mask]), np.std(conventional[circular_mask])
                CNR_HU = (signal_HU - noise_HU) / np.std(conventional[washer_mask])

                kedge = sample.acquisition[i].kedge[:, :, self.gui.slice_slider.val] if sample.acquisition[i].kedge is not None else None
                iodine = sample.acquisition[i].iodine[:, :, self.gui.slice_slider.val] if sample.acquisition[i].iodine is not None else None
        
                if kedge is None or (isinstance(kedge, np.ndarray) and np.isnan(kedge).any()):
                    signal_Kedge, noise_Kedge, CNR_Kedge = np.nan, np.nan, np.nan
            
                else:
                    kedge = sample.acquisition[i].kedge[:, :, self.gui.slice_slider.val]
                    signal_Kedge, noise_Kedge, kedge_Std = np.mean(kedge[circular_mask]), np.mean(kedge[washer_mask]), np.std(kedge[circular_mask])
                    CNR_Kedge = (signal_Kedge - noise_Kedge) / np.std(kedge[washer_mask])
                
                if iodine is None or (isinstance(iodine, np.ndarray) and np.isnan(iodine).any()):
                    signal_Iodine, noise_Iodine, Iodine_std = np.nan, np.nan, np.nan
            
                else:
                    iodine = sample.acquisition[i].iodine[:, :, self.gui.slice_slider.val]
                    signal_Iodine, noise_Iodine, Iodine_std= np.mean(iodine[circular_mask]), np.mean(iodine[washer_mask]), np.std(iodine[circular_mask])
                    CNR_Iodine = (signal_Iodine- noise_Iodine) / np.std(iodine[washer_mask])
                # Append metrics to the list
                measurements.append([signal_HU, noise_HU, signal_Std, CNR_HU, signal_Kedge, noise_Kedge, kedge_Std, CNR_Kedge, signal_Iodine, noise_Iodine, Iodine_std, CNR_Iodine])
    
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

        self.gui = Gui(sample)  # Assuming Viewer is defined elsewhere
        self.cid_click = self.gpu.fig.canvas.mpl_connect('button_press_event', self.on_mouse_click)
        self.cid_keypress = self.gpu.fig.canvas.mpl_connect('key_press_event', self.on_key_press)
        self.cid_keyrelease = self.gpu.fig.canvas.mpl_connect('key_release_event', self.on_key_release)

    def on_key_press(self, event):
        if event.key == 'g':
            self.g_key_pressed = True

    def on_key_release(self, event):
        if event.key == 'g':
            self.g_key_pressed = False

    def on_mouse_click(self, event):
        if event.inaxes == self.gpu.ax and event.button == 1 and self.g_key_pressed:
            self.add_circular_roi(event.xdata, event.ydata)
            plt.draw()

    def add_circular_roi(self, x_center, y_center):
        radius = 2.5  # For a diameter of 5 pixels

        # Create circular ROI mask
        nx, ny = self.gpu.image_display.get_array().shape[1], self.viewer.image_display.get_array().shape[0]
        y, x = np.ogrid[:ny, :nx]
        circular_mask = (x - x_center) ** 2 + (y - y_center) ** 2 <= radius ** 2

        # Process the mask and calculate statistics
        self.process_selection(circular_mask, self.sample)

        # Optionally, create an overlay image to show the ROI
        if self.mask_overlay is not None:
            self.mask_overlay.remove()
        self.mask_overlay = self.gpu.ax.imshow(circular_mask, cmap='coolwarm', alpha=0.5)
        self.gpu.fig.canvas.draw_idle()

    def process_selection(self, circular_mask, sample):
        # Placeholder for image data, replace with actual image data
        measurements = []
        image_data = self.gpu.image_display.get_array()

        # Compute statistics for the circular ROI
        for i in range(len(sample.acquisition)):
            conventional = sample.acquisition[i].conventional[:, :, self.viewer.slice_slider.val]
            kedge = sample.acquisition[i].kedge[:, :, self.gpu.slice_slider.val] if sample.acquisition[i].kedge is not None else None

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
