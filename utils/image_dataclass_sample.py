import os
from utils import loader
import pydicom

class ImageDTO:
    """
    The image data transfer object takes a defined directory and converts 3D map_decomps stored as map_decomps into numpy arrays.
    """
    
    def __init__(self, loaded_directories):
        self.ingest_directory = loaded_directories


        image_standardization()

        pydicom.dcmread()


    def create_3d_stack():

    def rescale_images():

    

