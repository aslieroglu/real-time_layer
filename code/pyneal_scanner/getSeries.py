""" Create a Nifti file from specified series data

Take the data in the specified series directory and convert it to a 4D
nifti image in RAS+ orientation, and then save the new data to disk.

If the series is an anatomical scan, the output Nifti will be 3D. If the series
is a functional scan, the output Nifti will be 4D. In all cases, the affine
transformation in the Nifti header will simply convert from voxel space
to mm space using the image voxel sizes (and not moving the origin at all)

"""
import argparse
import os
import sys
from os.path import join
import yaml

from utils.general_utils import initializeSession

# Get the full path to where the pyneal_scanner directory is. This assumes
# getSeries.py lives in the pyneal_scanner directory.
pynealScannerDir = os.path.dirname(os.path.abspath(__file__))

def getSeries_GE(scannerDirs):
    """ Build nifti image from series data, GE format

    Assumes series data are represented as dicom files, one per slice. The path
    to the output Nifti file will be printed to stdOut upon completion (in
    general, expect to find it in the pyneal_scanner/data directory)

    Parameters
    ----------
    scannerDirs : object
        instance of `GE_utils.GE_DirStructure`. Has attributes for the relevant
        paths for the current session. `scannerDirs` is one of the variables
        returned by running `general_utils.initializeSession()`

    """
    from utils.GE_utils import GE_BuildNifti

    # prompt user to specifiy a series. Make sure that it is a valid
    # series before continuing
    seriesDirs = scannerDirs.get_seriesDirs()
    while True:
        selectedSeries = input('Which Series?: ')
        if selectedSeries in seriesDirs:
            break
        else:
            print('{} is not a valid series choice!'.format(selectedSeries))

    # prompt user to specify an output name, and format to remove any spaces
    outputPrefix = input('Output Prefix: ')
    outputPrefix = outputPrefix.replace(' ', '')

    # progress updates
    print('='*5)
    print('Building Nifti...')
    print('\tinput series: {}'.format(selectedSeries))
    print('\toutput prefix: {}'.format(outputPrefix))

    # get the full path to the series dir
    seriesDir = join(scannerDirs.sessionDir, selectedSeries)

    # create an instance of the GE_NiftiBuilder
    niftiBuilder = GE_BuildNifti(seriesDir)
    output_fName = '{}_{}.nii.gz'.format(outputPrefix, selectedSeries)
    print('Successfully built Nifti image: {}\n'.format(output_fName))

    # save Nifti image
    output_path = join(pynealScannerDir, 'data', output_fName)
    saveNifti(niftiBuilder, output_path)


def getSeries_Philips(scannerDirs):
    """ Build nifti image from series data, Philips format

    Assumes series data are represented as par/rec file pairs, one per volume.
    The path to the output Nifti file will be printed to stdOut upon completion
    (in general, expect to find it in the pyneal_scanner/data directory)

    Parameters
    ----------
    scannerDirs : object
        instance of `Philips_utils.Philips_DirStructure`. Has attributes for
        the relvant paths for the current session. `scannerDirs` is one of the
        variables returned by running `general_utils.initializeSession()`

    """
    from utils.Philips_utils import Philips_BuildNifti

    # prompt user to specifiy a series. Make sure that it is a valid
    # series before continuing
    seriesDirs = scannerDirs.get_seriesDirs()
    while True:
        selectedSeries = input('Which Series?: ')
        if selectedSeries in seriesDirs:
            break
        else:
            print('{} is not a valid series choice!'.format(selectedSeries))

    # prompt user to specify an output name, and format to remove any spaces
    outputPrefix = input('Output Prefix: ')
    outputPrefix = outputPrefix.replace(' ', '')

    # progress updates
    print('='*5)
    print('Building Nifti...')
    print('\tinput series: {}'.format(selectedSeries))
    print('\toutput name: {}'.format(outputPrefix))

    # get the full path to the series dir
    seriesDir = join(scannerDirs.sessionDir, selectedSeries)

    # create an instance of the Siemens_NiftiBuilder
    niftiBuilder = Philips_BuildNifti(seriesDir)
    output_fName = '{}_{}.nii.gz'.format(outputPrefix, selectedSeries)
    print('Successfully built Nifti image: {}\n'.format(output_fName))

    # save Nifti image
    output_path = join(pynealScannerDir, 'data', output_fName)
    saveNifti(niftiBuilder, output_path)


def getSeries_Siemens(scannerDirs):
    """ Build nifti image from series data, Siemens format

    Assumes series data are represented as dicom mosaic files, one per volume.
    The path to the output Nifti file will be printed to stdOut upon completion
    (in general, expect to find it in the pyneal_scanner/data directory)

    Parameters
    ----------
    scannerDirs : object
        instance of `Siemens_utils.Siemens_DirStructure`. Has attributes for
        the relvant paths for the current session. `scannerDirs` is one of the
        variables returned by running `general_utils.initializeSession()`

    """
    from utils.Siemens_utils import Siemens_BuildNifti

    # prompt user to specifiy a series. Make sure that it is a valid
    # series before continuing
    currentSeries = scannerDirs.getUniqueSeries()
    while True:
        selectedSeries = input('Which Series?: ')
        if selectedSeries.zfill(6) in currentSeries:
            break
        else:
            print('{} is not a valid series choice!'.format(selectedSeries))

    # prompt user to specify an output name, and format to remove any spaces
    outputPrefix = input('Output Prefix: ')
    outputPrefix = outputPrefix.replace(' ', '')

    # progress updates
    print('='*5)
    print('Building Nifti...')
    print('\tinput series: {}'.format(selectedSeries))
    print('\toutput name: {}'.format(outputPrefix))

    # create an instance of the Siemens_NiftiBuilder
    niftiBuilder = Siemens_BuildNifti(scannerDirs.sessionDir, selectedSeries)
    output_fName = '{}_{}.nii.gz'.format(outputPrefix, selectedSeries)
    print('Successfully built Nifti image: {}\n'.format(output_fName))

    # save the nifti image
    output_path = join(pynealScannerDir, 'data', output_fName)
    saveNifti(niftiBuilder, output_path)


def saveNifti(niftiBuilder, outputPath):
    """ Save the nifti file to disk. Path to output file printed to stdOut

    Parameters
    ----------
    niftiBuilder : object
        instance of the niftiBuilder class for this scanning environment
    outputPath : string
        full path to where you want to save nifti file

    """
    # make sure the output dir exists
    outputDir, fName = os.path.split(outputPath)
    if not os.path.exists(outputDir):
        os.makedirs(outputDir)

    niftiBuilder.write_nifti(outputPath)
    print('saved at: {}'.format(outputPath))


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--settingsDir',
            default=None,
            help="specify the path to a custom settings file")
    parser.add_argument('-series',
            default=0,
            help="Whch series to read?")
    parser.add_argument('-filename',
            default="test",
            help="Name of the output file name")

    args = parser.parse_args()
    #if settings file exists the nset up everything from there
    if args.settingsDir is not None:
        # initialize the session classes:
        scannerSettings, scannerDirs = initializeSession(args.settingsDir) 
        pynealScannerDir = os.path.normpath(scannerSettings.allSettings['outputPath'])
    else:
        # initialize the session classes:
        scannerSettings, scannerDirs = initializeSession() 

    # print all of the current series dirs to the terminal
    scannerDirs.print_currentSeries()

    # load the appropriate tools for this scanning environment
    scannerMake = scannerSettings.allSettings['scannerMake']
    if scannerMake == 'GE':
        getSeries_GE(scannerDirs)
    elif scannerMake == 'Philips':
        getSeries_Philips(scannerDirs)
    elif scannerMake == 'Siemens':
        getSeries_Siemens(scannerDirs)
    else:
        print('Unrecognized scanner make: {}'.format(scannerMake))
