import os
import pydicom


class SampleDTO:
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
    
    def extract_number(self, filename):
        """
        Extracts the first sequence of digits from a given filename.
        """
        import re
        match = re.search(r"\d+", filename)
        return int(match.group()) if match else 0
    
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

