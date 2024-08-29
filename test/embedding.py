import os
import pydicom
import numpy as np
from PIL import Image
from transformers import AutoProcessor, AutoModel
import torch
from util.loader import Loader  # Replace with the actual module name where Loader is defined
from db.pgvector_db import PgVectorDB  # Replace with the actual module name where PgVectorDB is defined

# Initialize the database connection
db = PgVectorDB(dbname='medimages')

# Initialize the Loader class and process the study directory
loader = Loader(base_path="path_to_study_directory")

# Initialize the BiomedCLIP model and processor
model_name = "microsoft/BiomedCLIP-PubMedBERT_256-vit_base_patch16_224"
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

# Create a table in the database if not already present
table_name = "mri_embeddings"
db.create_medical_image_table(table_name=table_name, vector_dimension=512)  # Adjust dimension as needed

# Process the DICOM files using the Loader class and store embeddings
for subdir, volumes in loader.get_dicom_files().items():
    for volume_name, directories in volumes.items():
        for dir_name, dicom_files in directories.items():
            for dicom_file in dicom_files:
                embedding = generate_embedding_for_dicom(dicom_file)
                db.insert_dicom_with_embedding(dicom_file, table_name, embedding)
                print(f"Inserted embedding for {dicom_file}")

# Close the database connection
db.close()
