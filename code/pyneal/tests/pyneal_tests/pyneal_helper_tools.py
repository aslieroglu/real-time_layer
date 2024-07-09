import os
from os.path import join
from os.path import dirname
import shutil
import sys
from threading import Thread
import time

import zmq
import numpy as np

import yaml

def get_pyneal_test_paths():
    """ Return a dictionary with relevant paths for the pyneal_tests
    within the `tests` dir
    """
    # set up directory structure
    testingDir = dirname(dirname(os.path.abspath(__file__)))  # path to `tests` dir
    pynealDir = dirname(testingDir)
    pynealScannerDir = join(pynealDir, 'pyneal_scanner')
    testDataDir = join(testingDir, 'testData')
    GE_dir = join(testDataDir, 'GE_env')
    GE_funcDir = GE_dir
    Philips_dir = join(testDataDir, 'Philips_env')
    Philips_funcDir = join(Philips_dir, 'funcData')
    Siemens_dir = join(testDataDir, 'Siemens_env')
    Siemens_funcDir = join(Siemens_dir, 'funcData')

    # store paths in dict
    paths = {}
    paths['pynealDir'] = pynealDir
    paths['pynealScannerDir'] = pynealScannerDir
    paths['testDataDir'] = testDataDir
    paths['GE_dir'] = GE_dir
    paths['GE_funcDir'] = GE_funcDir
    paths['Philips_dir'] = Philips_dir
    paths['Philips_funcDir'] = Philips_funcDir
    paths['Siemens_dir'] = Siemens_dir
    paths['Siemens_funcDir'] = Siemens_funcDir

    return paths

def createFakeSeriesDir(newSeriesDir):
    """ Mimic the creation of a new series directory at the start of the scan.

    Parameters
    ----------
    newSeriesDir : string
        full path for the new series directory you'd like to create
    """
    if not os.path.isdir(newSeriesDir):
        os.makedirs(newSeriesDir)

class SimRecvSocket(Thread):
    def __init__(self, host, port, nVols):
        Thread.__init__(self)

        self.host = host
        self.port = port
        self.nVols = nVols
        self.alive = True
        self.receivedVols = 0

    def run(self):
        host = '*'
        self.context = zmq.Context.instance()
        sock = self.context.socket(zmq.PAIR)
        sock.bind('tcp://{}:{}'.format(host, self.port))

        # wait for initial contact
        while True:
            msg = sock.recv_string()
            sock.send_string(msg)
            break

        while self.alive:

            # receive header info as json
            volInfo = sock.recv_json(flags=0)

            # retrieve relevant values about this slice
            volIdx = volInfo['volIdx']
            volDtype = volInfo['dtype']
            volShape = volInfo['shape']

            # receive data stream
            data = sock.recv(flags=0, copy=False, track=False)
            voxelArray = np.frombuffer(data, dtype=volDtype)
            voxelArray = voxelArray.reshape(volShape)

            # send response
            sock.send_string('got it')

            self.receivedVols += 1
            if self.receivedVols == self.nVols:
                self.alive = False

    def stop(self):
        self.context.destroy()
        self.alive = False
