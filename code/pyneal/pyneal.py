"""Pyneal Real-time fMRI Acquisition and Analysis

This is the main Pyneal application, designed to be called directly from the
command line on the computer designated as your real-time analysis machine.
It expects to receive incoming slice data from the Pyneal-Scanner application,
which should be running concurrently elsewhere (e.g. on the scanner console
itself)

Once this application is called, it'll take care of opening the
GUI, loading settings, launching separate threads for monitoring and analyzing
incoming data, and hosting the Analysis output server

"""
# python 2/3 compatibility
from __future__ import print_function

import os
import sys
from os.path import join
import glob
import time
import argparse
import subprocess
import atexit
import webbrowser as web
import socket
import logging

import yaml
import nibabel as nib
import numpy as np
import zmq
import asyncio
from concurrent.futures import ProcessPoolExecutor
import multiprocessing as mp

from src.pynealLogger import createLogger
from src.scanReceiver import ScanReceiver
from src.pynealPreprocessing import Preprocessor
from src.pynealAnalysis import Analyzer
from src.resultsServer import ResultsServer
import src.GUIs.pynealSetup.setupGUI as setupGUI


# Set the Pyneal Root dir based on where this file lives
pynealDir = os.path.abspath(os.path.dirname(__file__))

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(), logging.FileHandler("multiprocessing_debug.log")]
)

def produce_volumes(queue, scanReceiver, num_volumes):
    """Producer process to add volumes to the queue."""
    for volIdx in range(num_volumes):
        while not scanReceiver.completedVols[volIdx]:
            logging.debug(f"scanReceiver.completedVols[{volIdx}] = {scanReceiver.completedVols[volIdx]}")
            logging.debug(f"Waiting for volIdx {volIdx} to complete...")
            time.sleep(0.1)
        logging.debug(f"Exiting wait loop: completedVols[{volIdx}] is now {scanReceiver.completedVols[volIdx]}")
        rawVol = scanReceiver.get_vol(volIdx)
        logging.info(f"Producer added volume {volIdx} to the queue")
        queue.put((volIdx, rawVol))
    # Send stop signals
    for _ in range(mp.cpu_count()):
        queue.put((None, None))
    logging.info("Producer finished adding all tasks.")

def worker(name, queue, preprocessor, analyzer, resultsServer):
    """Worker process to process volumes from the queue."""
    while True:
        volIdx, rawVol = queue.get()
        if volIdx is None:  # Stop signal
            logging.info(f"{name} received stop signal.")
            break
        logging.info(f"{name} processing volume {volIdx}")
        try:
            # Preprocessing
            preprocVol, proc_flag = preprocessor.runPreprocessing(rawVol, volIdx)
            logging.info(f"{name} completed preprocessing for volume {volIdx}")
            # Analysis
            result = analyzer.runAnalysis(preprocVol, volIdx, proc_flag)
            logging.info(f"{name} completed analysis for volume {volIdx}")
            # Results update
            resultsServer.updateResults(volIdx, result)
            logging.info(f"{name} updated results for volume {volIdx}")
        except Exception as e:
            logging.error(f"{name} encountered an error with volume {volIdx}: {e}")

def process_volumes_multiprocessing(settings, scanReceiver, preprocessor, analyzer, resultsServer):
    """Main function to manage producer and workers."""
    num_volumes = settings['numTimepts']
    queue = mp.Queue()
    num_workers = min(mp.cpu_count(), 4)  # Use a limited number of workers for testing

    logging.info(f"Starting multiprocessing with {num_workers} workers.")

    # Start producer process
    producer = mp.Process(target=produce_volumes, args=(queue, scanReceiver, num_volumes))
    producer.start()

    # Start worker processes
    workers = []
    for i in range(num_workers):
        worker_name = f"Worker-{i}"
        p = mp.Process(target=worker, args=(worker_name, queue, preprocessor, analyzer, resultsServer))
        workers.append(p)
        p.start()

    # Wait for the producer to finish
    producer.join()

    # Wait for all workers to finish
    for p in workers:
        p.join()

    logging.info("All tasks completed.")

def launchPyneal(headless=False, customSettingsFile=None):
    """Main Pyneal Loop.

    This function will launch setup GUI, retrieve settings, initialize all
    threads, and start processing incoming scans

    """
    ### Read Settings ------------------------------------
    # Read the settings file, and launch the setup GUI to give the user
    # a chance to update the settings. Hitting 'submit' within the GUI
    # will update the setupConfig file with the new settings
    if customSettingsFile:
        print('Loading custom settings file: {}'.format(customSettingsFile))
        settingsFile = customSettingsFile
    else:
        settingsFile = join(pynealDir, 'src/GUIs/pynealSetup/setupConfig.yaml')

    if not headless:
        # Launch GUI to let user update the settings file
        setupGUI.launchPynealSetupGUI(settingsFile)
    elif headless:
        print('Running headless...')
        print('Using settings in {}'.format(settingsFile))
        assert os.path.exists(settingsFile), 'Running headless, but settings file does not exist: {}'.format(settingsFile)

    # Read the new settings file, store as dict
    with open(settingsFile, 'r') as ymlFile:
        settings = yaml.safe_load(ymlFile)
    

    #get the host ip and save in config file
    hostname = socket.gethostname()
    ip_address = socket.gethostbyname(hostname)
    print(f"### Pyneal running on {hostname} at IP {ip_address} ###")
    settings['pynealHostIP'] = ip_address
    with open(settingsFile, 'w') as f:
        yaml.dump(settings,f)
        
    ###Set up various directories
    settings['pynealDir'] = pynealDir
    ### Create the output directory, put in settings dict
    outputDir = createOutputDir(settings['outputPath'])
    settings['seriesOutputDir'] = outputDir
    settings['run_ref_img'] = os.path.join(settings['seriesOutputDir'],'ref_img.nii')
    #settings['run_mask'] = os.path.join(settings['seriesOutputDir'],'mask.nii.gz')
    settings['xfrm_file'] = os.path.join(settings['seriesOutputDir'],'ref2run_ref.mat')
    
    ### Set Up Logging ------------------------------------
    # The createLogger function will do a lot of the formatting set up
    # behind the scenes. You can write to this log by calling the
    # logger var and specifying the level, e.g.: logger.debug('msg')
    # Other modules can write to this same log by calling
    # the command: logger = logging.getLogger('PynealLog')
    logFname = join(outputDir, 'pynealLog.log')
    logger = createLogger(logFname)
    print('Logs written to: {}'.format(logFname))

    # write all settings to log
    for k in settings:
        logger.info('Setting: {}: {}'.format(k, settings[k]))
    print('-'*20)

    ### Launch Threads -------------------------------------
    # Scan Receiver Thread, listens for incoming volume data, builds matrix
    scanReceiver = ScanReceiver(settings)
    scanReceiver.daemon = True
    scanReceiver.start()
    logger.debug('Starting Scan Receiver')

    # Results Server Thread, listens for requests from end-user (e.g. task
    # presentation), and sends back results
    resultsServer = ResultsServer(settings)
    resultsServer.daemon = True
    resultsServer.start()
    logger.debug('Starting Results Server')

    ### Create processing objects --------------------------
    # Class to handle all preprocessing
    preprocessor = Preprocessor(settings)

    # Class to handle all analysis
    analyzer = Analyzer(settings)

    ### Launch Real-time Scan Monitor GUI
    if settings['launchDashboard']:
        ### launch the dashboard app as its own separate process. Once called,
        # it will set up a zmq socket to listen for inter-process messages on
        # the 'dashboardPort', and will host the dashboard website on the
        # 'dashboardClientPort'
        pythonExec = sys.executable     # path to the local python executable
        p = subprocess.Popen([
                        pythonExec,
                        join(pynealDir,
                             'src/GUIs/pynealDashboard/pynealDashboard.py'),
                        str(settings['dashboardPort']),
                        str(settings['dashboardClientPort'])
                        ])

        # Set up the socket to communicate with the dashboard server
        dashboardContext = zmq.Context.instance()
        dashboardSocket = dashboardContext.socket(zmq.REQ)
        dashboardSocket.connect('tcp://127.0.0.1:{}'.format(settings['dashboardPort']))

        # make sure subprocess and dashboard ports get killed at close
        atexit.register(cleanup, p, dashboardContext)

        # Open dashboard in browser
        s = '127.0.0.1:{}'.format(settings['dashboardClientPort'])
        print(s)
        web.open('127.0.0.1:{}'.format(settings['dashboardClientPort']))

        # send configuration settings to dashboard
        configDict = {'mask': (None if settings['analysisChoice'] == 'Layers' else os.path.split(settings['maskFile'])[1]),
                      'analysisChoice': (settings['analysisChoice'] if settings['analysisChoice'] in ['Average', 'Median','Layers'] else 'Custom'),
                      'volDims': str(nib.load(settings['layerMaskSuperior']).shape) if settings['analysisChoice'] == 'Layers' else 
                                    str(nib.load(settings['maskFile']).shape),
                      'numTimepts': settings['numTimepts'],
                      'outputPath': outputDir}
        sendToDashboard(dashboardSocket,
                        topic='configSettings',
                        content=configDict)

    ### Wait For Scan To Start -----------------------------
    while not scanReceiver.scanStarted:
        time.sleep(.5)
    logger.debug('Scan started')

    ### Set up remaining configuration settings after first volume arrives
    while not scanReceiver.completedVols[0]:
        time.sleep(.1)
    preprocessor.set_affine(scanReceiver.get_affine())

    ### Process scan  -------------------------------------
    # Launch asynchronous processing
    process_volumes_multiprocessing(settings, scanReceiver, preprocessor, analyzer, resultsServer)

    #asyncio.run(process_volumes_async(settings, scanReceiver, preprocessor, analyzer, resultsServer))

        # # update dashboard (if dashboard is launched)
        # if settings['launchDashboard']:
        #     # completed volIdx
        #     sendToDashboard(dashboardSocket, topic='volIdx', content=volIdx)

        #     # timePerVol
        #     timingParams = {'volIdx': volIdx,
        #                     'processingTime': np.round(elapsedTime, decimals=3)}
        #     sendToDashboard(dashboardSocket, topic='timePerVol',
        #                     content=timingParams)
        #     logger.debug(f"volIdx:{volIdx} total_proc_time:{elapsedTime}")


    ### Save output files and stop the scanreceiver server
    # Saurabh: Increased to ensure server not closed before client's last request
    #time.sleep(2)
    time.sleep(3)
    resultsServer.saveResults()
    scanReceiver.saveResults()
    ### Figure out how to clean everything up nicely at the end
    resultsServer.killServer()
    scanReceiver.killServer()
    


def sendToDashboard(dashboardSocket, topic=None, content=None):
    """ Send a message to the dashboard

    Construct a JSON message using the supplied `topic` and `content`, and send
    it out over the `dashboardSocket` object

    Parameters:
    -----------
    dashboardSocket : zmq socket object
        Instance of dashboard socket class
    topic : string
        Topic type of message to send to Pyneal dashboard. Must be one of the
        expected topic types in order for the dashboard to make sense of it.
        (See: src/GUIs/pynealDashboard/pynealDashboard.py)
    content :
        The actual content you want sent to the dashboard. The `content`
        dtype will vary depending on topic

    """
    if topic is None:
        raise Exception('Dashboard message has topic set to None')
    if content is None:
        raise Exception('Dashboard message has content set to None')

    # format the message to send to dashboard
    msg = {'topic': topic, 'content': content}

    # send
    dashboardSocket.send_json(msg)
    #logger.debug('sent to dashboard: {}'.format(msg))

    # recv the response (should just be 'success')
    response = dashboardSocket.recv_string()
    if response != 'success':
        print(response)
        raise Exception('Could not send this dashboard: {}'.format(msg))
    #added by Saurabh
    else:
        print('Sent to dashboard: {}'.format(msg))

    #logger.debug('response from dashboard: {}'.format(response))


def createOutputDir(parentDir):
    """Create a new output directory

    A new output subdirectory will be created in the supplied parent dir.
    Output directories are named sequentially, starting with pyneal_001. This
    function will find all existing pyneal_### directories in the `parentDir`
    and name the new output directory accordingly.

    Parameters:
    -----------
    parentDir : string
        full path to the parent directory where you'd like the new output
        subdirectory to appear

    Returns:
    --------
    string
        full path to the new output subdirectory

    """
    # find any existing pyneal_### directories, create the next one in series
    existingDirs = glob.glob(join(parentDir, 'pyneal_*'))
    if len(existingDirs) == 0:
        outputDir = join(parentDir, 'pyneal_001')
    else:
        # add 1 to highest numbered existing dir
        nextDirNum = int(sorted(existingDirs)[-1][-3:]) + 1
        outputDir = join(parentDir, 'pyneal_' + str(nextDirNum).zfill(3))

    # create the output dir and return full path to it
    os.makedirs(outputDir)
    return outputDir


def cleanup(pid, context):

    # kill dashboard server subprocess
    print('stopping dashboard subprocess')
    pid.terminate()

    # kill dashboard client server
    context.destroy()



### ----------------------------------------------
if __name__ == '__main__':
    # Start Pyneal by calling pyneal.py from the command line
    parser = argparse.ArgumentParser()
    parser.add_argument('--noGUI',
            action='store_true',
            help="run in headless mode, no setup GUI. (requires a valid settings file, either supplied here with -s option, or in {pyneal root}/src/GUIs/pynealSetup/setupConfig.yaml)")
    parser.add_argument('-s', '--settingsFile',
            default=None,
            help="specify the path to a custom settings file")

    args = parser.parse_args()
    launchPyneal(headless=args.noGUI, customSettingsFile=args.settingsFile)
