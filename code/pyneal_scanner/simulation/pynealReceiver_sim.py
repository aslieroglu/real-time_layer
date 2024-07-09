""" Basic script to mimic the behavior of Pyneal during an actual scan.

This is a quick and dirty server set up to mimic the behavior of Pyneal. It
will listen for incoming data over an assigned port using the same methods
that Pyneal would use during a real scan. This tool allows you to test
components of Pyneal Scanner without having to actually run a full Pyneal
setup.

Usage
-----
    python pynealReceiver_sim.py [--port] [--nVols]

Defaults:
    -p/--port: 5555
    -n/--nVols: 60

After the scan is complete and all of the data has arrived, this will save the
received 4D volume as a nifti image in same directory as this script (output file named 'receivedImg.nii.gz')

"""
from __future__ import division

import os
import time
import json
import argparse

import zmq
import numpy as np
import nibabel as nib


def launchPynealReceiver(port, nVols, saveImage=True):
    """ Launch Pyneal Receiver simulation.

    This method will simulate the behavior of the scanReceiver thread of
    Pyneal. That is, it will listen for incoming 3D volumes sent from Pyneal
    Scanner, enabling you to test Pyneal Scanner without having to run the full
    Pyneal Setup

    Parameters
    ----------
    port : int
        port number that will be used to transfer data between Pyneal Scanner
        and Pyneal
    nVols : int
        number of expected volumes in the dataset
    saveImage : boolean, optional
        flag for whether to save received image or not

    """
    ### Set up socket to listen for incoming data
    # Note: since this is designed for testing, it assumes
    # you are running locally and sets the host accordingly
    host = '*'
    context = zmq.Context.instance()
    sock = context.socket(zmq.PAIR)
    sock.bind('tcp://{}:{}'.format(host, port))
    print('pynealReceiver_sim listening for connection at {}:{}'.format(host,
          port))

    # wait for initial contact
    while True:
        msg = sock.recv_string()
        sock.send_string(msg)
        break

    firstVolHasArrived = False
    print('Waiting for first volume data to appear...')

    while True:
        # receive header info as json
        volInfo = sock.recv_json(flags=0)

        # retrieve relevant values about this slice
        volIdx = volInfo['volIdx']
        volDtype = volInfo['dtype']
        volShape = volInfo['shape']

        # build the imageMatrix if this is the first volume
        if not firstVolHasArrived:
            imageMatrix = np.zeros(shape=(volShape[0],
                                          volShape[1],
                                          volShape[2],
                                          nVols), dtype=volDtype)
            volAffine = np.array(json.loads(volInfo['affine']))

            # update first vol flag
            firstVolHasArrived = True

        # receive raw data stream, reshape to slice dimensions
        data = sock.recv(flags=0, copy=False, track=False)
        voxelArray = np.frombuffer(data, dtype=volDtype)
        voxelArray = voxelArray.reshape(volShape)

        # add the voxel data to the appropriate location
        imageMatrix[:, :, :, volIdx] = voxelArray

        # send slice over socket
        if volIdx == (nVols-1):
            response = 'Received vol {} - STOP'.format(volIdx)
        else:
            response = 'Received vol {}'.format(volIdx)
        sock.send_string(response)
        print(response)

        # if all volumes have arrived, save the image
        if volIdx == (nVols-1):
            if saveImage:
                receivedImg = nib.Nifti1Image(imageMatrix, volAffine)
                outputName = 'receivedImg.nii.gz'
                nib.save(receivedImg, outputName)
                print('Image saved at: {}'.format(os.path.abspath(outputName)))

            # close socket
            time.sleep(.5)
            context.destroy()
            break


if __name__ == '__main__':
    # parse arguments
    parser = argparse.ArgumentParser(description='Simulate Receiving thread of Pyneal')
    parser.add_argument('-p', '--port',
                        type=int,
                        default=5555,
                        help='port number to listen on for incoming data from pynealScanner ')
    parser.add_argument('-n', '--nVols',
                        type=int,
                        default=60,
                        help='number of expected volumes')

    # grab the input args
    args = parser.parse_args()

    # launch
    launchPynealReceiver(args.port, args.nVols)
