from dataclasses import dataclass
import numpy as np

@dataclass
class ImageDTO:
    image_data: np.ndarray
    rescale_intercept: float
    rescale_slope: float

    def rescale_image(self):
        """
        The raw intensity values of DICOM images don't correspond to either HU or mg/ml scale so we must convert them with this simple linear transformation
        """
        rescaled_image = self.image_data * self.rescale_slope + self.rescale_intercept
        return rescaled_image

    def redefine_window(self, window_width=200):
        """
        Although not currently amazingly useful, I find it visually helpful to remove negative concentrations from my K-edges and have a framework for altering the intensity window
        of the conventional CT images.
        """
        window_center = self.image_data.mean()

        # K-edge specific windowing
        img_min = 0
        img_max = window_center + (window_width // 2)
       
        window_image = self.image_data.copy()
        window_image[window_image < img_min] = img_min
        window_image[window_image > img_max] = img_max
        
        return window_image

# Example usage
def process_image(medical_image, image):
    image_dto = ImageDTO(image_data=image, rescale_intercept=medical_image.RescaleIntercept, rescale_slope=medical_image.RescaleSlope)
    rescaled_image = image_dto.rescale_image()
    windowed_image = image_dto.redefine_window()
    return rescaled_image, windowed_image