import numpy as np
import pydicom
import os
import SimpleITK as sitk
import time
from tqdm import tqdm

def writeSlices(series_tag_values, new_img, i, out_dir):
    image_slice = new_img[:,:,i]
    writer = sitk.ImageFileWriter()
    writer.KeepOriginalImageUIDOn()

    # Tags shared by the series.
    list(map(lambda tag_value: image_slice.SetMetaData(tag_value[0], tag_value[1]), series_tag_values))

    # Slice specific tags.
    image_slice.SetMetaData("0008|0012", time.strftime("%Y%m%d")) # Instance Creation Date
    image_slice.SetMetaData("0008|0013", time.strftime("%H%M%S")) # Instance Creation Time

    # Setting the type to CT preserves the slice location.
    image_slice.SetMetaData("0008|0060", "CT")  # set the type to CT so the thickness is carried over

    # (0020, 0032) image position patient determines the 3D spacing between slices.
    image_slice.SetMetaData("0020|0032", '\\'.join(map(str,new_img.TransformIndexToPhysicalPoint((0,0,i))))) # Image Position (Patient)
    image_slice.SetMetaData("0020,0013", str(i)) # Instance Number

    # Write to the output directory and add the extension dcm, to force writing in DICOM format.
    writer.SetFileName(os.path.join(out_dir,'slice' + str(i).zfill(4) + '.dcm'))
    writer.Execute(image_slice)


def convert_nifti_to_dicom(nifti_dir, out_dir):
    new_img = sitk.ReadImage(nifti_dir) 
    modification_time = time.strftime("%H%M%S")
    modification_date = time.strftime("%Y%m%d")
    out_path = os.path.join(out_dir)
    direction = new_img.GetDirection()
    series_tag_values = [("0008|0031",modification_time), # Series Time
                    ("0008|0021",modification_date), # Series Date
                    ("0008|0008","DERIVED\\SECONDARY"), # Image Type
                    ("0020|000e", "1.2.826.0.1.3680043.2.1125."+modification_date+".1"+modification_time), # Series Instance UID
                    ("0020|0037", '\\'.join(map(str, (direction[0], direction[3], direction[6],# Image Orientation (Patient)
                                                        direction[1],direction[4],direction[7])))),
                    ("0008|103e", "Created-SimpleITK")] # Series Description

    # Write slices to output directory
    list(map(lambda i: writeSlices(series_tag_values, new_img, i, out_dir), tqdm(range(new_img.GetDepth()))))
    


def nifti2dicom_mfiles(nifti_dir, out_dir=''):
    """
    This function is to convert multiple nifti files into dicom files
    `nifti_dir`: You enter the global path to all of the nifti files here.
    `out_dir`: Put the path to where you want to save all the dicoms here.
    PS: Each nifti file's folders will be created automatically, so you do not need to create an empty folder for each patient.
    """

    files = os.listdir(nifti_dir)
    for file in files:
        in_path = os.path.join(nifti_dir, file)
        out_path = os.path.join(out_dir, file)
        os.mkdir(out_path)
        convert_nifti_to_dicom(in_path, out_path)

    print("La conversion de NIfTI vers dicom est terminée.")


if __name__ == "__main__":
    nifti_dir = "Specify the path to the folder that contains the nifti files"
    out_dir = "scpecifies the path to the folder where the dicom files will be saved"
    nifti2dicom_mfiles(nifti_dir, out_dir)