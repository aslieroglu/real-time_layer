""" Simulate a GE Multiband scan

GE scanners store reconstructed slice images as individual DICOM files within
a certain directory on the scanner console. This script will simulate that
directory and copy in individual slice DICOM images.

Usage:
------
    python GEMB_sim.py inputDir [--outputDir] [--TR]

You must specify a local path to the inputDir. That is, the directory that
already contains a set of reconstructed GE slice DICOMS. Let's call this
directory the seriesDir. Everything in the path up to the seriesDir we'll call
the sessionDir.

So, your input slice data is stored somewhere like:

<sessionDir>/<seriesDir>/

To use this tool, you must specify an inputDir as the full path
(i.e. <sessionDir>/<seriesDir>) to the source data.

[OPTIONAL]: You can specify the full path to an output directory where the
slices will be copied to. If you don't specify an output directory, this tool
will default to creating a new seriesDir, named 's9999' in the sessionDir.

e.g. python GEMB_sim.py /Path/To/My/Existing/Slice/Data --outputDir /Where/I/Want/New/Slice/Data/To/appear

if you did not specify an outputDir, new slices would be copied to:

/Path/To/My/Existing/Slice/s9999

[OPTIONAL]: You can specify the TR at which new slice data is copied. Default
is 1000ms, and represents the approximate amount of time it should take to copy
over all of the slices for one volume of data.

e.g. python GE_sim.py /Path/To/My/Existing/Slice/Data --TR 2000

"""
# python 2/3 compatibility
from __future__ import print_function
from builtins import input

import os
import sys
from os.path import join
import argparse
import atexit
import re
import time
import subprocess

import pydicom

# regEx for GE style file naming
GE_filePattern = re.compile('i\d*.MRDC.\d*')

# 'Locations in acquisition' private tag
locInAcqTag = [0x0021, 0x104f]

def GEMB_sim(dicomDir, outputDir, TR):
    """ Simulate a GE multiband scanning environment

    To simulate a scan, this function will read all of the dicom slice files
    from a specified `dicomDir`, and will then copy each file, in order of
    acquisition, to a specified `outputDir`.

    The `outputDir` therefore serves as the directory for Pyneal Scanner to
    monitor for new images as though it was a real scan. The rate that dicom
    slice files are copied from the `dicomDir` to the `outputDir` is determined
    by the `TR` parameter

    Parameters
    ----------
    dicomDir : string
        full path to directory containing dicom slice files from an existing
        scan
    outputDir : string
        full path to the directory you want to copy existing slice files to.
        Pyneal Scanner should be set to monitor this directory as though it was
        a real scan
    TR : int
        the time it takes to copy all of the slices pertaining to a single
        volume of data. Units: milliseconds

    """

    # build full path to outputDir
    print('-'*25)
    print('Source slices: {}'.format(dicomDir))
    print('Output dir: {}'.format(outputDir))

    # if outputDir exists, delete
    if os.path.isdir(outputDir):
        print('Deleting existing {}'.format(outputDir))
        subprocess.call(['rm', '-r', outputDir])

    # make a dictionary of slice files
    sliceFiles = {}
    for f in os.listdir(dicomDir):
        if GE_filePattern.match(f):
            dicomNumber = f.split('.')[-1]
            sliceFiles[dicomNumber] = f

    # read slice (first entry in sliceFiles dict) to get TR and # of slices/vol
    ds = pydicom.dcmread(join(dicomDir,
                         sliceFiles[list(sliceFiles.keys())[0]]))
    slicesPerVol = ds[locInAcqTag].value
    totalVols = ds.NumberOfTemporalPositions

    # calculate delay between slices
    sliceDelay = TR/slicesPerVol/1000

    # print parameters
    print('Total Slices Found: ', len(sliceFiles))
    print('TR: ', TR)
    print('Vols: ', totalVols)
    print('slices per vol:', slicesPerVol)
    print('delay between slices:', sliceDelay)

    # wait for input to begin
    input('Press ENTER to begin the "scan" ')

    # create the outputDir:
    os.makedirs(outputDir)

    # loop over all sorted slice files
    print('copied dicom #:', end=' ')
    simStart = time.time()
    for i, sliceNum in enumerate(sorted(sliceFiles, key=int)):
        startTime = time.time()
        src_file = join(dicomDir, sliceFiles[sliceNum])
        dst_file = join(outputDir, sliceFiles[sliceNum])

        # copy the file
        subprocess.call(['cp', src_file, dst_file])
        print(sliceNum, end=', ', flush=True)

        # introduce interslice delay (minus any elapsed time)
        elapsedTime = time.time()-startTime
        if elapsedTime < sliceDelay:
            time.sleep(sliceDelay - elapsedTime)

    simElapsed = time.time() - simStart
    print('Mean time per vol: {}'.format(simElapsed/totalVols))
    input('Scan completed. Press ENTER to delete temp output directory...')


def rmOutputDir(outputDir):
    """ Remove the `outputDir`

    """
    # if outputDir exists, delete
    if os.path.isdir(outputDir):
        print('Deleting output dir: {}'.format(outputDir))
        subprocess.call(['rm', '-r', outputDir])


if __name__ == "__main__":
    # parse arguments
    parser = argparse.ArgumentParser(description='Simulate a GE scan')
    parser.add_argument('inputDir',
                        help='full path to directory that contains slice DICOMS')
    parser.add_argument('-o', '--outputDir',
                        default=None,
                        help='full path to output directory where new slices images will appear (i.e. series directory)')
    parser.add_argument('-t', '--TR',
                        type=int,
                        default=1000,
                        help='TR (ms) [default = 1000]')

    # grab the input args
    args = parser.parse_args()

    # check if input dir is valid
    if not os.path.isdir(args.inputDir):
        print('Invalid input dir: {}').format(args.inputDir)
        sys.exit()

    # check if the output Dir is specified. If not, create it
    if args.outputDir is None:
        # strip trailing slash, if present
        if args.inputDir[-1] == os.sep:
            args.inputDir = args.inputDir[:-1]
        sessionDir, seriesDir = os.path.split(args.inputDir)
        defaultNewDir = 's9999'
        outputDir = join(sessionDir, defaultNewDir)
    else:
        outputDir = args.outputDir

    # set the cleanup function to remove the output directory
    atexit.register(rmOutputDir, outputDir)

    # run main function
    GEMB_sim(args.inputDir, outputDir, args.TR)
