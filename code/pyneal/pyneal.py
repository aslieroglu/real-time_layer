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
import json

import yaml
import nibabel as nib
import numpy as np
import zmq
import uuid
import subprocess
import logging

from src.pynealLogger import createLogger
from src.scanReceiver import ScanReceiver
from src.pynealPreprocessing import Preprocessor
from src.pynealAnalysis import Analyzer
from src.resultsServer import ResultsServer
import src.GUIs.pynealSetup.setupGUI as setupGUI

# Parallel Processing Libraries
import multiprocessing as mp

scan_queue = mp.Queue()              # Queue for incoming scans
result_queue = mp.Queue()            #
shared_ns = mp.Manager().Namespace() # shared namespace for sharing common variables across processes

NUM_WORKERS = 2           
  
# Set the Pyneal Root dir based on where this file lives
pynealDir = os.path.abspath(os.path.dirname(__file__))

def preProcessVol(vol, volIdx, affine, ref, startTime):
    logger = logging.getLogger('PynealLog')
    aligned_img = None
    niiVol = nib.Nifti1Image(vol, affine)
    temp_input = f"/dev/shm/input_{uuid.uuid4().hex}.nii.gz"
    temp_output = f"/dev/shm/out_{uuid.uuid4().hex}.nii.gz"
    nib.save(niiVol, temp_input)
    
    command_start = time.time()
    #FSL subprocess
    command = ["mcflirt",
                "-in",
                temp_input,
                "-reffile",
                ref,
                "-out",
                temp_output,
                "-spline_final"]
    subprocess.run(command, check=True) # Possibly improve this
    command_done = time.time()
    logger.info(f"Ran commmand for vol {volIdx} in time {command_done - command_start:.2f}")
    aligned_img = nib.load(temp_output)
    logger.debug(
                f"estimateMotion: volIdx {volIdx} - Aligned image stats: "
                f"mean={np.mean(aligned_img.get_fdata())}, "
                f"max={np.max(aligned_img.get_fdata())}, "
                f"min={np.min(aligned_img.get_fdata())}"
        )
    elapsedTime = time.time() - startTime
    logger.info(f"Completed processing Vol {volIdx} at t = {np.round(elapsedTime, decimals=2)}")
    
    return aligned_img.get_fdata()

def worker_process(scan_queue, result_queue, ref, startTime, shared_ns):
    """ Worker that continuously listens for scans in queue and 
    processes them as they are available.
    
    Parameters
    ----------
    scan_queue : mp.Queue() 

    """
    logger = logging.getLogger('PynealLog')
    while True:
        task = scan_queue.get()
        if task is None:
            break
        
        volIdx, vol = task
        logger.info(f"[Worker-{os.getpid()}] Processing scan {volIdx}... at t = {np.round(time.time() - startTime, 2)}")
        start_time = time.time()
        processedVol = preProcessVol(vol, volIdx, shared_ns.affine, ref, startTime) # Take care of output later...
        elapsedTime = time.time() - start_time
        result_queue.put((volIdx, elapsedTime))
            
    logger.info(f"[Worker-{os.getpid()}] Exiting.")

def scanner_process(scan_queue, result_queue, settings, shared_ns):
    logger = logging.getLogger('PynealLog')
    logger.info("Scanner Process Started!")
    # get vars from settings dict
    numTimepts = int(settings['numTimepts'])
    seriesOutputDir = settings['seriesOutputDir']
    # set up socket server to listen for msgs from pyneal-scanner
    host = settings['pynealHost']
    scannerPort = settings['pynealScannerPort']
    context = zmq.Context.instance()
    scannerSocket = context.socket(zmq.PAIR)
    scannerSocket.setsockopt(zmq.LINGER, 0)
    scannerSocket.bind('tcp://{}:{}'.format(host, scannerPort))
    logger.info('bound to {}:{}'.format(host, scannerPort))
    logger.info('Scan Receiver Server alive and listening....')
    
    atexit.register(destroy_context, scannerSocket, context)

    # class config vars
    scanStarted = False
    shared_ns.affine = None
    tr = None
    
    while True:
        print('Waiting for connection from pyneal_scanner')
        msg = scannerSocket.recv_string()
        # msg = scannerSocket.recv()
        print('Received message: ', msg)
        scannerSocket.send_string(msg)
        break
    logger.debug('scanner socket connected to Pyneal-Scanner')
    
    while True:
        volHeader = scannerSocket.recv_json(flags=0)
        logger.debug(f"Received volHeader: volIdx={volHeader['volIdx']}, "
                f"dtype={volHeader['dtype']}, shape={volHeader['shape']}, "
                f"TR={volHeader.get('TR', 'N/A')}")
        volIdx = volHeader['volIdx']
        logger.debug('received volHeader volIdx {}'.format(volIdx));

        # if this is the first vol, initialize the matrix and store the affine
        if not scanStarted:
            shared_ns.affine = np.array(json.loads(volHeader['affine']))
            tr = json.loads(volHeader['TR'])

            scanStarted = True     # toggle the scanStarted flag

        # now listen for the image data as a string buffer
        voxelArray = scannerSocket.recv(flags=0, copy=False, track=False)
        
        # send response back to Pyneal-Scanner
        response = "received volIdx {}".format(volIdx) 
        response += " STOP" if int(volIdx) == numTimepts - 1 else ""
        scannerSocket.send_string(response)
        logger.info(response)
        
        # format the voxel array according to params from the vol header
        voxelArray = np.frombuffer(voxelArray, dtype=volHeader['dtype'])
        voxelArray = voxelArray.reshape(volHeader['shape'])

        logger.debug(
            f"Right after voxelArray reshape: Received volume data for volIdx {volIdx}: "
            f"mean={np.mean(voxelArray)}, max={np.max(voxelArray)}, min={np.min(voxelArray)}"
        )
        
        # Push scanned volIdx into queue for processing
        scan_queue.put((volIdx, voxelArray))
        
        # End Loop if all timepoints have been received
        if int(volIdx) == numTimepts - 1:
            break
    
     
    # Signal workers to stop
    for _ in range(NUM_WORKERS):
        scan_queue.put(None)  # None signals termination
    
    # Signal dashboard to stop
    result_queue.put(None)
    

def dashboard_process(result_queue, settings):
    logger = logging.getLogger('PynealLog')
    logger.info("Started dashboard process")
     ### Launch Real-time Scan Monitor GUI

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
    atexit.register(cleanup, p, dashboardSocket, dashboardContext)

    # Open dashboard in browser
    # s = '127.0.0.1:{}'.format(settings['dashboardClientPort'])
    # print(s)
    # web.open('127.0.0.1:{}'.format(settings['dashboardClientPort']))

    # send configuration settings to dashboard
    configDict = {'mask': os.path.split(settings['maskFile'])[1],
                    'analysisChoice': (settings['analysisChoice'] if settings['analysisChoice'] in ['Average', 'Median'] else 'Custom'),
                    'volDims': str(nib.load(settings['maskFile']).shape),
                    'numTimepts': settings['numTimepts'],
                    'outputPath': settings['seriesOutputDir']}
    sendToDashboard(dashboardSocket,
                    topic='configSettings',
                    content=configDict)
    while True:
        task = result_queue.get()
        if task is None:
            break
        volIdx, elapsedTime = task
        logger.info(f"Dashboard process got {volIdx}")
        # completed volIdx
        sendToDashboard(dashboardSocket, topic='volIdx', content=volIdx)

        # timePerVol
        timingParams = {'volIdx': volIdx,
                        'processingTime': np.round(elapsedTime, decimals=3)}
        sendToDashboard(dashboardSocket, topic='timePerVol',
                        content=timingParams)
        
    logger.info("Closing Dashboard.")

def parallelPyneal(settings):
    logger = logging.getLogger('PynealLog')
    startTime = time.time()
    # Start the scan receiver in a separate process
    logger.info("Starting scanner process...")
    
    
    receiver_proc = mp.Process(target=scanner_process, args=(scan_queue, result_queue, settings, shared_ns))
    receiver_proc.start()
    if settings['launchDashboard']:
        logger.info("Starting dashboard process...")
        dashboard_proc = mp.Process(target=dashboard_process, args=(result_queue, settings))
        dashboard_proc.start()
    
    worker_procs = []
    for _ in range(NUM_WORKERS):
        p = mp.Process(target=worker_process, args=(scan_queue,
                                                    result_queue, 
                                                    settings['referenceImage'], 
                                                    startTime, 
                                                    shared_ns))
        p.start()
        worker_procs.append(p)
    
    # Wait for all processes to finish
    receiver_proc.join()
    for p in worker_procs:
        p.join()
    if settings['launchDashboard']:
        dashboard_proc.join()
        
    logger.info("[Main] All processes completed.")

def serialPyneal(settings):
    logger = logging.getLogger('PynealLog')
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
        atexit.register(cleanup, p, dashboardSocket, dashboardContext)

        # Open dashboard in browser
        # s = '127.0.0.1:{}'.format(settings['dashboardClientPort'])
        # print(s)
        # web.open('127.0.0.1:{}'.format(settings['dashboardClientPort']))

        # send configuration settings to dashboard
        configDict = {'mask': os.path.split(settings['maskFile'])[1],
                      'analysisChoice': (settings['analysisChoice'] if settings['analysisChoice'] in ['Average', 'Median'] else 'Custom'),
                      'volDims': str(nib.load(settings['maskFile']).shape),
                      'numTimepts': settings['numTimepts'],
                      'outputPath': settings['seriesOutputDir']}
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
    # Loop over all expected volumes
    for volIdx in range(settings['numTimepts']):

        ### make sure this volume has arrived before continuing
        while not scanReceiver.completedVols[volIdx]:
            time.sleep(.1)

        ### start timer
        startTime = time.time()

        ### Retrieve the raw volume
        rawVol = scanReceiver.get_vol(volIdx)
        
        ### Preprocess the raw volume
        preprocVol, procflag = preprocessor.runPreprocessing(rawVol, volIdx)

        ### Analyze this volume
        result = analyzer.runAnalysis(preprocVol, volIdx, procflag)

        # send result to the resultsServer
        resultsServer.updateResults(volIdx, result)

        ### Calculate processing time for this volume
        elapsedTime = time.time() - startTime

        # update dashboard (if dashboard is launched)
        if settings['launchDashboard']:
            # completed volIdx
            sendToDashboard(dashboardSocket, topic='volIdx', content=volIdx)

            # timePerVol
            timingParams = {'volIdx': volIdx,
                            'processingTime': np.round(elapsedTime, decimals=3)}
            sendToDashboard(dashboardSocket, topic='timePerVol',
                            content=timingParams)

    ### Save output files
    resultsServer.saveResults()
    scanReceiver.saveResults()

    ### Figure out how to clean everything up nicely at the end
    resultsServer.killServer()
    scanReceiver.killServer()
    
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
        
    parallelPyneal(settings) if settings['parallel'] else serialPyneal(settings)
        

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
    # print("Sending message as json: {}".format(msg))
    dashboardSocket.send_json(msg)
    # logger.info('sent to dashboard: {}'.format(msg))

    # recv the response (should just be 'success')
    # print("waiting for response from dashboard socket")
    response = dashboardSocket.recv_string()
    if response != 'success':
        print(response)
        raise Exception('Could not send this dashboard: {}'.format(msg))
    #added by Saurabh
    else:
        pass
        # print('Successfuly sent msg to dashboard')

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

def destroy_context(socket, context):
    print("Destroying context")
    socket.close()
    context.term()

def cleanup(pid, socket,  context):

    # kill dashboard server subprocess
    print('stopping dashboard subprocess')
    pid.terminate()

    # kill dashboard client server
    socket.setsockopt(zmq.LINGER, 0)
    socket.close()
    context.term()



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
