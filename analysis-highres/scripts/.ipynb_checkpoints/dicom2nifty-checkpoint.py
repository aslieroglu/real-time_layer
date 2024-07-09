#Converts dicom to a nifty file
#code is extracted from pyneal scanner -> utils -> Siemens Util
import os
from os.path import join
import sys
import time
import re
import json
import glob
import logging

import numpy as np
import pydicom
import nibabel as nib
from nibabel.nicom import dicomreaders


class Siemens_BuildNifti():
    """ Tools to build a 3D or 4D Nifti image from all of the dicom mosaic
    images in a directory.

    Input is a path to a series directory containing dicom images (either
    mosaic images for functional data, or 2D slice image for anatomical data).
    Image parameters, like voxel spacing and dimensions, are obtained
    automatically from the info in the dicom tags

    End result is a Nifti1 formatted 3D (anat) or 4D (func) file in RAS+
    orientation

    """
    def __init__(self, seriesDir, seriesNum):
        """ Initialize class, and set/obtain basic class attributes like file
        paths and scan parameters

        Parameters
        ----------
        seriesDir : string
            full path to the directory containing the raw dicom mosaic files
            for each volume in the series
        seriesNum : string
            series number of the series that you'd like to build the nifti
            image from

        """
        # initialize attributes
        self.seriesDir = seriesDir
        self.seriesNum = seriesNum
        self.niftiImage = None

        # make a list of the specified raw dicom mosaic files in this dir
        rawDicoms = glob.glob(join(self.seriesDir, ('*_' + str(self.seriesNum).zfill(6) + '_*.dcm')))

        # figure out what type of image this is, 4d or 3d
        self.scanType = self._determineScanType(rawDicoms[0])

        # build the nifti image
        if self.scanType == 'anat':
            self.niftiImage = self.buildAnat(rawDicoms)
        elif self.scanType == 'func':
            self.niftiImage = self.buildFunc(rawDicoms)

    def buildAnat(self, dicomFiles):
        """ Build a 3D structural/anatomical image from list of dicom files

        Given a list of `dicomFiles`, build a 3D anatomical image from them.
        Figure out the image dimensions and affine transformation to map
        from voxels to mm from the dicom tags

        Parameters
        ----------
        dicomFiles : list
            list containing the file names (file names ONLY, no path) of all
            dicom slice images to be used in constructing the final nifti image

        Returns
        -------
        anatImage_RAS : Nifti1Image
            nifti-1 formated image of the 3D anatomical data, oriented in
            RAS+

        See Also
        --------
        nibabel.nifti1.Nifti1Image()

        """
        # read the first dicom in the list to get overall image dimensions
        dcm = pydicom.dcmread(join(self.seriesDir, dicomFiles[0]), stop_before_pixels=1)
        sliceDims = (getattr(dcm, 'Columns'), getattr(dcm, 'Rows'))
        self.nSlicesPerVol = len(dicomFiles)
        sliceThickness = getattr(dcm, 'SliceThickness')

        ### Build 3D array of voxel data
        # create an empty array to store the slice data
        imageMatrix = np.zeros(shape=(
                               sliceDims[0],
                               sliceDims[1],
                               self.nSlicesPerVol), dtype='int16')

        # Use the InstanceNumber tag to order the slices. This works for anat
        # 3D images only, since the instance numbers do not repeat as they would
        # with functional data with multiple volumes
        sliceDict = {}
        for s in dicomFiles:
            dcm = pydicom.dcmread(join(self.seriesDir, s))
            sliceDict[dcm.InstanceNumber] = join(self.seriesDir, s)

        # sort by InStackPositionNumber and assemble the image
        for sliceIdx, ISPN in enumerate(sorted(sliceDict.keys())):
            dcm = pydicom.dcmread(sliceDict[ISPN])

            # extract the pixel data as a numpy array. Transpose
            # so that the axes order go [cols, rows]
            pixel_array = dcm.pixel_array.T

            # place in the image matrix
            imageMatrix[:, :, sliceIdx] = pixel_array

        ### create the affine transformation to map from vox to mm space
        # in order to do this, we need to get some values from the first and
        # last slices in the volume.
        firstSlice = sliceDict[sorted(sliceDict.keys())[0]]
        lastSlice = sliceDict[sorted(sliceDict.keys())[-1]]

        dcm_first = pydicom.dcmread(firstSlice)
        dcm_last = pydicom.dcmread(lastSlice)
        self.pixelSpacing = getattr(dcm_first, 'PixelSpacing')
        self.firstSlice_IOP = np.array(getattr(dcm_first, 'ImageOrientationPatient'))
        self.firstSlice_IPP = np.array(getattr(dcm_first, 'ImagePositionPatient'))
        self.lastSlice_IPP = np.array(getattr(dcm_last, 'ImagePositionPatient'))

        # now we can build the affine
        affine = self.buildAffine()

        ### Build a Nifti object, reorder it to RAS+
        anatImage = nib.Nifti1Image(imageMatrix, affine=affine)
        anatImage_RAS = nib.as_closest_canonical(anatImage)     # reoder to RAS+
        print('Nifti image dims: {}'.format(anatImage_RAS.shape))

        return anatImage_RAS

    def buildFunc(self, dicomFiles):
        """ Build a 4D functional image from list of dicom files

        Given a list of dicomFile paths, build a 4d functional image. For
        Siemens scanners, each dicom file is assumed to represent a mosaic
        image comprised of mulitple slices. This tool will split apart the
        mosaic images, and construct a 4D nifti object. The 4D nifti object
        contain a voxel array ordered like RAS+ as well the affine
        transformation to map between vox and mm space

        Parameters
        ----------
        dicomFiles : list
            list containing the file names (file names ONLY, no path) of all
            dicom mosaic images to be used in constructing the final nifti
            image

        """
        imageMatrix = None
        affine = None
        TR = None

        # make dicomFiles store the full path
        dicomFiles = [join(self.seriesDir, f) for f in dicomFiles]

        ### Loop over all dicom mosaic files
        nVols = len(dicomFiles)
        for mosaic_dcm_fname in dicomFiles:
            ### Parse the mosaic image into a 3D volume
            # we use the nibabel mosaic_to_nii() method which does a lot of the
            # heavy-lifting of extracting slices, arranging in a 3D array, and
            # grabbing the affine
            dcm = pydicom.dcmread(mosaic_dcm_fname)     # create dicom object

            # for mosaic files, the instanceNumber tag will correspond to the
            # volume number (using a 1-based indexing, so subtract by 1)
            volIdx = dcm.InstanceNumber - 1

            # convert the dicom object to nii
            thisVol = dicomreaders.mosaic_to_nii(dcm)

            # convert to RAS+
            thisVol_RAS = nib.as_closest_canonical(thisVol)

            if TR is None:
                TR = dcm.RepetitionTime / 1000

            # construct the imageMatrix if it hasn't been made yet
            if imageMatrix is None:
                imageMatrix = np.zeros(shape=(thisVol_RAS.shape[0],
                                              thisVol_RAS.shape[1],
                                              thisVol_RAS.shape[2],
                                              nVols), dtype=np.uint16)

            # construct the affine if it isn't made yet
            if affine is None:
                affine = thisVol_RAS.affine

            # Add this data to the image matrix
            imageMatrix[:, :, :, volIdx] = thisVol_RAS.get_fdata()

        ### Build a Nifti object
        funcImage = nib.Nifti1Image(imageMatrix, affine=affine)
        pixDims = np.array(funcImage.header.get_zooms())
        pixDims[3] = TR
        funcImage.header.set_zooms(pixDims)

        return funcImage

    def buildAffine(self):
        """ Build the affine matrix that will transform the data to RAS+.

        This function should only be called once the required data has been
        extracted from the dicom tags from the relevant slices. The affine
        matrix is constructed by using the information in the
        ImageOrientationPatient and ImagePositionPatient tags from the first
        and last slices in a volume.

        However, note that those tags will tell you how to orient the image to
        DICOM reference coordinate space, which is LPS+. In order to to get to
        RAS+ we have to invert the first two axes.

        Notes
        -----
        For more info on building this affine, please see the documentation at:
        http://nipy.org/nibabel/dicom/dicom_orientation.html
        http://nipy.org/nibabel/coordinate_systems.html

        """
        ### Get the ImageOrientation values from the first slice,
        # split the row-axis values (0:3) and col-axis values (3:6)
        # and then invert the first and second values of each
        rowAxis_orient = self.firstSlice_IOP[0:3] * np.array([-1, -1, 1])
        colAxis_orient = self.firstSlice_IOP[3:6] * np.array([-1, -1, 1])

        ### Get the voxel size along Row and Col axis
        voxSize_row = float(self.pixelSpacing[0])
        voxSize_col = float(self.pixelSpacing[1])

        ### Figure out the change along the 3rd axis by subtracting the
        # ImagePosition of the last slice from the ImagePosition of the first,
        # then dividing by 1/(total number of slices-1), then invert to
        # make it go from LPS+ to RAS+
        slAxis_orient = (self.firstSlice_IPP - self.lastSlice_IPP) / (1 - self.nSlicesPerVol)
        slAxis_orient = slAxis_orient * np.array([-1, -1, 1])

        ### Invert the first two values of the firstSlice ImagePositionPatient.
        # This tag represents the translation needed to take the origin of our 3D voxel
        # array to the origin of the LPS+ reference coordinate system. Since we want
        # RAS+, need to invert those first two axes
        voxTranslations = self.firstSlice_IPP * np.array([-1, -1, 1])

        ### Assemble the affine matrix
        affine = np.matrix([
            [rowAxis_orient[0] * voxSize_row, colAxis_orient[0] * voxSize_col, slAxis_orient[0], voxTranslations[0]],
            [rowAxis_orient[1] * voxSize_row, colAxis_orient[1] * voxSize_col, slAxis_orient[1], voxTranslations[1]],
            [rowAxis_orient[2] * voxSize_row, colAxis_orient[2] * voxSize_col, slAxis_orient[2], voxTranslations[2]],
            [0, 0, 0, 1]
            ])

        return affine

    def _determineScanType(self, dicomFile):
        """ Figure out what type of scan this is, anat or func

        This tool will determine the scan type from a given dicom file.
        Possible scan types are either single 3D volume (anat), or a 4D dataset
        built up of 2D slices (func). The scan type is determined by reading
        the `MRAcquisitionType` tag from the dicom file

        Parameters
        ----------
        dcmFile : string
            file name of dicom file from the current series that you would like
            to open to read the imaging parameters from

        Returns
        -------
        scanType : string
            either 'anat' or 'func' depending on scan type stored in dicom tag

        """
        # read the dicom file
        dcm = pydicom.dcmread(join(self.seriesDir, dicomFile), stop_before_pixels=1)

        if getattr(dcm, 'MRAcquisitionType') == '3D':
            scanType = 'anat'
        elif getattr(dcm, 'MRAcquisitionType') == '2D':
            scanType = 'func'
        else:
            print('Cannot determine a scan type from this image!')
            sys.exit()

        return scanType

    def get_scanType(self):
        """ Return the scan type """
        return self.scanType

    def get_niftiImage(self):
        """ Return the constructed Nifti Image """
        return self.niftiImage

    def write_nifti(self, output_path):
        """ Write the nifti file to disk

        Parameters
        ----------
        outputPath : string
            full path, including filename, you want to use to save the nifti
            image

        """
        nib.save(self.niftiImage, output_path)
        print('Image saved at: {}'.format(output_path))