from utils import loader

#raw_image = loader.Loader("c:\\Users\\Chris\\OneDrive\\Desktop\\sample_data")

sample = loader.Loader()
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