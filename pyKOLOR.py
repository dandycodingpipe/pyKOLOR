from util.loader import Loader
import pydicom
import numpy as np
from PIL import Image
from transformers import AutoProcessor, AutoModel
import torch

# Initialize the Loader
sample = Loader()

# Replace these with your actual subdirectory, volume, and sub-directory names
subdirectory_name = "2021_01_25.4533.300.2024_03_17.AGUIX_Rabbit_26608_e00000"
volume_name = "Conventional"
subdir_in_volume = "dcm"

# Access the specific DICOM files
dicom_files_list = sample.dicom_files.get(subdirectory_name, {}).get(volume_name, {}).get(subdir_in_volume, [])

# Print the DICOM files
print(f"DICOM files in '{subdirectory_name}' -> '{volume_name}' -> '{subdir_in_volume}':")
for dicom_file in dicom_files_list:
    print(dicom_file)

# Initialize the BiomedCLIP model and processor
model_name = "monai-test/brats_mri_segmentation"
processor = AutoProcessor.from_pretrained(model_name)
model = AutoModel.from_pretrained(model_name)

# Function to generate embeddings for a DICOM file
def generate_embedding_for_dicom(dicom_path):
    dicom = pydicom.dcmread(dicom_path)
    image = dicom.pixel_array

    # Normalize pixel values to range [0, 255] if needed
    image = ((image - np.min(image)) / (np.max(image) - np.min(image)) * 255).astype(np.uint8)
    
    # Convert grayscale to RGB (required by most pre-trained models)
    image = np.stack([image] * 3, axis=-1)
    image = Image.fromarray(image)

    # Process the image and generate the embedding
    inputs = processor(images=image, return_tensors="pt")
    with torch.no_grad():
        embedding = model.get_image_features(**inputs).cpu().numpy()

    return embedding[0]

# Generate and print embeddings for the accessed DICOM files
for dicom_file in dicom_files_list:
    embedding = generate_embedding_for_dicom(dicom_file)
    print(f"Generated embedding for {dicom_file}: {embedding[:10]}...")  # Print the first 10 values of the embedding for brevity
