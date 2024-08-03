#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This experiment was created using PsychoPy3 Experiment Builder (v2022.1.4),
    on Wed Feb 28 15:54:16 2024
If you publish work using this script the most relevant publication is:

    Peirce J, Gray JR, Simpson S, MacAskill M, Höchenberger R, Sogo H, Kastman E, Lindeløv JK. (2019) 
        PsychoPy2: Experiments in behavior made easy Behav Res 51: 195. 
        https://doi.org/10.3758/s13428-018-01193-y

"""

import psychopy
psychopy.useVersion('2022.1.4')

from psychopy import locale_setup
from psychopy import prefs
prefs.hardware['audioLib'] = 'ptb'
prefs.hardware['audioLatencyMode'] = '0'
from psychopy import sound, gui, visual, core, data, event, logging, clock, colors, layout
from psychopy.constants import (NOT_STARTED, STARTED, PLAYING, PAUSED,
                                STOPPED, FINISHED, PRESSED, RELEASED, FOREVER)
from psychopy.hardware import keyboard

import numpy as np  # whole numpy lib is available, prepend 'np.'
from numpy import (sin, cos, tan, log, log10, pi, average,
                   sqrt, std, deg2rad, rad2deg, linspace, asarray)
from numpy.random import random, randint, normal, shuffle, choice as randchoice
import os  # handy system and path functions
import sys  # to get file system encoding

from nfbDisplayModels import timeseriesNFB
from resultsManager import resultsServerHandler
import yaml, argparse

def close_experiment():
    # Flip one final time so any remaining win.callOnFlip() 
    # and win.timeOnFlip() tasks get executed before quitting
    try:
        win.flip()
        # these shouldn't be strictly necessary (should auto-save)
        thisExp.saveAsWideText(filename+'.csv', delim='auto')
        thisExp.saveAsPickle(filename)
        thisExp.abort()  # or data files will save again on exit
    except NameError as e:
        logging.warning(f"Closing early. {e}")
    logging.flush()
    core.quit()


# Ensure that relative paths start from the same directory as this script
_thisDir = os.path.dirname(os.path.abspath(__file__))
os.chdir(_thisDir)
# Store info about the experiment session
psychopyVersion = '2022.1.4'
expName = 'NFB'  # from the Builder filename that created this script
expInfo = {
    'participant_id': 'ENTER SUBJECT ID',
    'session': '001',
    'runs': ' ',
    'volumes': ' ',
    'TR': '2',
    'n_vols_up': ' ',
    'n_vols_down': ' ',
    'start_block': ' ',
    #'baseline': '1.0',
    'pyneal_results_server_IP': ' ',
    'pyneal_results_server_port': ' ',
    'colour_down': 'darkgray',
    'colour_up': 'darkgreen',
    'analysis_typ': 'average',
    'mri_trigger_key': 't',
    'results_dir': '/data/pt_02900/pilot/psychopydata'
}
config_file_available = False
#get the settings file from command line if supplied
parser = argparse.ArgumentParser()
parser.add_argument('-s', '--settingsFile',
    default=None,
    help="specify the path to a custom settings file")
args = parser.parse_args()
customSettingsFile = args.settingsFile
if customSettingsFile:
    logging.exp('Loading config file: {}'.format(customSettingsFile))
    try:
        config_file = open(customSettingsFile, 'r')
    except OSError as e:
        logging.error(f"Couldnt open the config file -> {e}") #let all data be entered from GUI
        endExpNow = True
    else:
        with config_file:
            config = yaml.safe_load(config_file)
            config_file_available = True
if config_file_available:
    expInfo['participant_id'] = config['subjectId']
    expInfo['runs'] = config['runs']
    expInfo['volumes'] = config['numVols']
    expInfo['TR'] = config['TR']
    expInfo['n_vols_up'] = config['numVolsUp']
    expInfo['n_vols_down'] = config['numVolsDown']
    expInfo['start_block'] = config['startBlock']
    expInfo['results_dir'] = config['outputPath']
    #expInfo['baseline'] = config['baseline']
    expInfo['pyneal_results_server_IP'] = config['pynealHostIP']
    expInfo['pyneal_results_server_port'] = config['resultsServerPort']

#show the data entry screen and process response
dlg = gui.DlgFromDict(dictionary=expInfo, sortKeys=False, title=expName)
if dlg.OK == False:
    core.quit()  # user pressed cancel
expInfo['date'] = data.getDateStr()  # add a simple timestamp
expInfo['expName'] = expName
expInfo['psychopyVersion'] = psychopyVersion
#check is results server is running at all
logging.info(f"Pyneal results server at {config['pynealHostIP']}:{config['resultsServerPort']}")
result_server = resultsServerHandler(config['pynealHostIP'], config['resultsServerPort'])
results_server_available = result_server.test_results_server()
if not results_server_available:
    logging.error(f"Pyneal results server not running. Quitting.")
    close_experiment()
#set up the parameters with correct variable type since psychopy dialog returns dict of strings
expInfo['runs'] = int(expInfo['runs'])
expInfo['volumes'] = int(expInfo['volumes'])
expInfo['TR'] = float(expInfo['TR'])
expInfo['n_vols_up'] = int(expInfo['n_vols_up'])
expInfo['n_vols_down'] = int(expInfo['n_vols_down'])
expInfo['pyneal_results_server_port'] = int(expInfo['pyneal_results_server_port'])
expInfo['baseline'] = 1.0

#Create experiment handler, filenames 
# Data file name stem = absolute path + name; later add .psyexp, .csv, .log, etc
filename = os.path.normpath(expInfo['results_dir']) + os.sep + u'data/%s_%s_session_%s' % (expInfo['participant'],expInfo['date'],expInfo['session'])

# An ExperimentHandler isn't essential but helps with data saving
thisExp = data.ExperimentHandler(name=expName, version='',
    extraInfo=expInfo, runtimeInfo=None,
    originPath='/Users/sabi/Techspace/Neurofeedback/code/NFB-controllers/mainExperiment.py',
    savePickle=True, saveWideText=True,
    dataFileName=filename)
# save a log file for detail verbose info
logFile = logging.LogFile(filename+'.log', level=logging.DEBUG)
logging.console.setLevel(logging.WARNING)  # this outputs to the screen, not a file

endExpNow = False  # flag for 'escape' or other condition => quit the exp
frameTolerance = 0.001  # how close to onset before 'same' frame


# Start Code - component code to be run after the window creation

# Setup the Window
win = visual.Window(
    size=[800, 600], fullscr=True, screen=0, 
    winType='pyglet', allowGUI=True, allowStencil=False,
    monitor='testMonitor', color=[0,0,0], colorSpace='rgb',
    blendMode='avg', useFBO=True, 
    units='norm')
# store frame rate of monitor if we can measure it
expInfo['frameRate'] = win.getActualFrameRate()
if expInfo['frameRate'] != None:
    frameDur = 1.0 / round(expInfo['frameRate'])
else:
    frameDur = 1.0 / 60.0  # could not measure, so guess


# create a default keyboard (e.g. to check for escape)
defaultKeyboard = keyboard.Keyboard(backend='event')

# Initialize components for Routine "setup_params"
setup_paramsClock = core.Clock()

# Initialize components for Routine "setup_nfb"
setup_nfbClock = core.Clock()

# Initialize components for Routine "pause_and_check"
pause_and_checkClock = core.Clock()
pause_check_key = keyboard.Keyboard()
pause_check_msg = visual.TextStim(win=win, name='pause_check_msg',
    text='Relax. We start when you are ready.',
    font='Open Sans',
    pos=(0, 0), height=0.1, wrapWidth=None, ori=0.0, 
    color='white', colorSpace='rgb', opacity=None, 
    languageStyle='LTR',
    depth=-1.0);

# Initialize components for Routine "sync_with_mri"
sync_with_mriClock = core.Clock()
sync_mri_key = keyboard.Keyboard()
sync_mri_msg = visual.TextStim(win=win, name='sync_mri_msg',
    text='Waiting for scanning to start ...',
    font='Open Sans',
    pos=(0, 0), height=0.1, wrapWidth=None, ori=0.0, 
    color='green', colorSpace='rgb', opacity=None, 
    languageStyle='LTR',
    depth=-1.0);

# Initialize components for Routine "volume"


# Initialize components for Routine "complete_pending_nfb"
complete_pending_nfbClock = core.Clock()

# Initialize components for Routine "reset_screen"
reset_screenClock = core.Clock()

# Create some handy timers
globalClock = core.Clock()  # to track the time since experiment started
routineTimer = core.CountdownTimer()  # to track time remaining of each (non-slip) routine 

# ------ Routine "setup_nfb"-------
# update component parameters for each repeat
n_blocks,rem =  divmod(expInfo['volumes'],(expInfo['n_vols_up'] + expInfo['n_vols_down']))
if expInfo['start_block'] == "down":
    block_design = np.concatenate([np.full(expInfo['n_vols_down'],"down"),np.full(expInfo['n_vols_up'],"up")])
    last_block = np.full(rem,"down")
else:
    block_design = np.concatenate([np.full(expInfo['n_vols_up'],"up"),np.full(expInfo['n_vols_down'],"down")])
    last_block = np.full(rem,"up")
run_design = np.concatenate([np.tile(block_design,n_blocks),last_block])

block_boundaries = np.where(run_design[:-1]!= run_design[1:])[0] + 1
block_boundaries = np.concatenate([[0],block_boundaries,[expInfo['volumes']]]) #first block starts at index 0
logging.exp(block_boundaries)
    
#create the timeseries NFB display
block_def = dict(order=run_design,
                 colour=dict(down=expInfo['colour_down'],up=expInfo['colour_up'])
                 )
logging.exp(block_def)
nfb = timeseriesNFB(win,
                    volumes=expInfo['volumes'],
                    #baseline=expInfo['baseline'],
                    block_def=block_def
                    )


if endExpNow or defaultKeyboard.getKeys(keyList=["escape"]):
    #core.quit()
    close_experiment()
else:
    # refresh the screen
    win.flip()

# the Routine "setup_nfb" was not non-slip safe, so reset the non-slip timer
routineTimer.reset()

# set up handler to look after randomisation of conditions etc
runs = data.TrialHandler(nReps=expInfo['runs'], method='sequential', 
    extraInfo=expInfo, originPath=-1,
    trialList=[None],
    seed=None, name='runs')
thisExp.addLoop(runs)  # add the loop to the experiment
thisRun = runs.trialList[0]  # so we can initialise stimuli with some values
# abbreviate parameter names if possible (e.g. rgb = thisRun.rgb)
if thisRun != None:
    for paramName in thisRun:
        exec('{} = thisRun[paramName]'.format(paramName))

for thisRun in runs:
    # -------Setup Routine volumes for looping tjhrough each volune -------
    # set up handler to look after randomisation of conditions etc
    volumes = data.TrialHandler(nReps=expInfo['volumes'], method='sequential', 
        extraInfo=expInfo, originPath=-1,
        trialList=[None],
        seed=None, name='volumes')
    thisExp.addLoop(volumes)  # add the loop to the experiment
    thisVolume = volumes.trialList[0]  # so we can initialise stimuli with some values
    # abbreviate parameter names if possible (e.g. rgb = thisVolume.rgb)
    if thisVolume != None:
        for paramName in thisVolume:
            exec('{} = thisVolume[paramName]'.format(paramName))
    # abbreviate parameter names if possible (e.g. rgb = thisRun.rgb)
    if thisRun != None:
        for paramName in thisRun:
            exec('{} = thisRun[paramName]'.format(paramName))
    
    # -------Routine "pause_and_check"-------

    _pause_check_key_allKeys = []
    pause_check_msg.setAutoDraw(True)
    win.flip()
    theseKeys = pause_check_key.waitKeys(keyList=['return','escape'], waitRelease=False)
    _pause_check_key_allKeys.extend(theseKeys)
    pause_check_key.keys = _pause_check_key_allKeys[0].name
    if pause_check_key.keys == 'escape':
        endExpNow = True

    # check for quit (typically the Esc key)
    if endExpNow or defaultKeyboard.getKeys(keyList=["escape"]):
            close_experiment()
            #core.quit()

    # -------Ending Routine "pause_and_check" -------
    pause_check_msg.setAutoDraw(False)
    # the Routine "pause_and_check" was not non-slip safe, so reset the non-slip timer
    routineTimer.reset()

    # ------Prepare to start Routine "sync_with_mri"-------
    continueRoutine = True
    # update component parameters for each repeat
    sync_mri_key.keys = []
    _sync_mri_key_allKeys = []
    # keep track of which components have finished
    sync_with_mriComponents = [sync_mri_key, sync_mri_msg]
    for thisComponent in sync_with_mriComponents:
        thisComponent.tStart = None
        thisComponent.tStop = None
        thisComponent.tStartRefresh = None
        thisComponent.tStopRefresh = None
        if hasattr(thisComponent, 'status'):
            thisComponent.status = NOT_STARTED
    # reset timers
    t = 0
    _timeToFirstFrame = win.getFutureFlipTime(clock="now")
    sync_with_mriClock.reset(-_timeToFirstFrame)  # t0 is time of first possible flip
    frameN = -1
    
    # -------Run Routine "sync_with_mri"-------
    while continueRoutine:
        # get current time
        t = sync_with_mriClock.getTime()
        tThisFlip = win.getFutureFlipTime(clock=sync_with_mriClock)
        tThisFlipGlobal = win.getFutureFlipTime(clock=None)
        frameN = frameN + 1  # number of completed frames (so 0 is the first frame)
        # update/draw components on each frame
        
        # *sync_mri_key* updates
        waitOnFlip = False
        if sync_mri_key.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
            # keep track of start time/frame for later
            sync_mri_key.frameNStart = frameN  # exact frame index
            sync_mri_key.tStart = t  # local t and not account for scr refresh
            sync_mri_key.tStartRefresh = tThisFlipGlobal  # on global time
            win.timeOnFlip(sync_mri_key, 'tStartRefresh')  # time at next scr refresh
            sync_mri_key.status = STARTED
            # keyboard checking is just starting
            waitOnFlip = True
            win.callOnFlip(sync_mri_key.clock.reset)  # t=0 on next screen flip
            win.callOnFlip(sync_mri_key.clearEvents, eventType='keyboard')  # clear events on next screen flip
        if sync_mri_key.status == STARTED and not waitOnFlip:
            theseKeys = sync_mri_key.getKeys(keyList=[expInfo['mri_trigger_key'],'escape'], waitRelease=False)
            _sync_mri_key_allKeys.extend(theseKeys)
            if len(_sync_mri_key_allKeys):
                sync_mri_key.keys = _sync_mri_key_allKeys[0].name  # just the first key pressed
                # a right response ends the routine
                if expInfo['mri_trigger_key'] in theseKeys:
                    continueRoutine = False
                elif 'escape' in theseKeys:
                    endExpNow = True
                    continueRoutine = False
        
        # *sync_mri_msg* updates
        if sync_mri_msg.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
            # keep track of start time/frame for later
            sync_mri_msg.frameNStart = frameN  # exact frame index
            sync_mri_msg.tStart = t  # local t and not account for scr refresh
            sync_mri_msg.tStartRefresh = tThisFlipGlobal  # on global time
            win.timeOnFlip(sync_mri_msg, 'tStartRefresh')  # time at next scr refresh
            sync_mri_msg.setAutoDraw(True)
        
        if sync_mri_msg.status == STARTED:
            # keep track of stop time/frame for later
            sync_mri_msg.tStop = t  # not accounting for scr refresh
            sync_mri_msg.frameNStop = frameN  # exact frame index
            win.timeOnFlip(sync_mri_msg, 'tStopRefresh')  # time at next scr refresh
            #sync_mri_msg.setAutoDraw(False)

        
        # check for quit (typically the Esc key)
        if endExpNow or defaultKeyboard.getKeys(keyList=["escape"]):
            #core.quit()
            close_experiment()
    
        # check if all components have finished
        if not continueRoutine:  # a component has requested a forced-end of Routine
            break
        continueRoutine = False  # will revert to True if at least one component still running
        for thisComponent in sync_with_mriComponents:
            if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
                continueRoutine = True
                break  # at least one component has not yet finished
        
        # refresh the screen
        if continueRoutine:  # don't flip if this routine is over or we'll get a blank screen
            win.flip()
    
    # -------Ending Routine "sync_with_mri"-------
    for thisComponent in sync_with_mriComponents:
        if hasattr(thisComponent, "setAutoDraw"):
            thisComponent.setAutoDraw(False)
    # check responses
    if sync_mri_key.keys in ['', [], None]:  # No response was made
        sync_mri_key.keys = None
    runs.addData('sync_mri_key.keys',sync_mri_key.keys)
    runs.addData('sync_mri_key.started', sync_mri_key.tStartRefresh)
    runs.addData('sync_mri_key.stopped', sync_mri_key.tStopRefresh)
    runs.addData('sync_mri_msg.started', sync_mri_msg.tStartRefresh)
    runs.addData('sync_mri_msg.stopped', sync_mri_msg.tStopRefresh)
    # the Routine "sync_with_mri" was not non-slip safe, so reset the non-slip timer
    routineTimer.reset()
    
    
    # -------Start Looping through the volumes-------
    #setup params for looping throug volumes
    temp_block_boundaries = [i for i in block_boundaries]
    vol_idx  = 0
    recv_first_valid_nfb =  False
    pyneal_Q = []
    nfb.show_bounding_box()
    for thisVolume in volumes:
        # ------Prepare to start Routine "volume"-------
        continueRoutine = True
        routineTimer.add(expInfo['TR'])
        vol_start = win.getFutureFlipTime(clock=None)  # time at next scr refresh
        # update component parameters for each repeat
        if vol_idx == temp_block_boundaries[0]:
            logging.exp(f"Vol idx {vol_idx}")
            nfb.show_block(np.arange(temp_block_boundaries[0],temp_block_boundaries[1]))
            temp_block_boundaries = temp_block_boundaries[1:]

        # -------Run Routine "volume"-------
        while routineTimer.getTime() > 0:
            # update/draw components on each frame
            if len(pyneal_Q) > 0:
                result = result_server.get_result(pyneal_Q[0])
                if result and result["foundResults"]:
                    #read the feedback and process
                    if np.isnan(result[expInfo['analysis_typ']]):
                        nfb.show_feedback(pyneal_Q[0], 1)
                    else:
                        if not recv_first_valid_nfb:
                            recv_first_valid_nfb = True
                            expInfo['baseline'] = result[expInfo['analysis_typ']]
                        nfb.show_feedback(pyneal_Q[0], result[expInfo['analysis_typ']]/expInfo['baseline'])
                    runs.addData(f"result.vol.{pyneal_Q[0]}",result[expInfo['analysis_typ']])
                    runs.addData(f"result.t.vol.{pyneal_Q[0]}",win.getFutureFlipTime(clock=None))
                    pyneal_Q = pyneal_Q[1:]        
            # check for quit (typically the Esc key)
            if endExpNow or defaultKeyboard.getKeys(keyList=["escape"]):
                core.quit()

            win.flip()
        
        # -------Ending Routine "volume"-------
        runs.addData(f'start.vol.{vol_idx}', vol_start)
        pyneal_Q.append(vol_idx)
        vol_idx += 1

    # completed expInfo['volumes'] repeats of 'volumes'
    
    # ------Routine "complete_pending_nfb"-------
 
    # update component parameters for each repeat
    logging.exp(f"Pending NFB {pyneal_Q}")
    while len(pyneal_Q) > 0:
        result = result_server.get_result(pyneal_Q[0])
        if result and result["foundResults"]:
            nfb.show_feedback(pyneal_Q[0], result[expInfo['analysis_typ']]/expInfo['baseline'])
            runs.addData(f"result.vol.{pyneal_Q[0]}",result[expInfo['analysis_typ']])
            runs.addData(f"result.t.vol.{pyneal_Q[0]}",win.getFutureFlipTime(clock=None))
            win.flip()
            pyneal_Q = pyneal_Q[1:]
    win.getMovieFrame()
    win.saveMovieFrames(f"{thisExp.dataFileName}_run_{runs.thisRepN}.png")

    # the Routine "complete_pending_nfb" was not non-slip safe, so reset the non-slip timer
    routineTimer.reset()
    
    # ------ Routine "reset_screen"-------
    # update component parameters for each repeat
    core.wait(5) #to give some time for the experince to sink in
    nfb.reset()
    vol_idx = 0
    recv_first_valid_nfb = False
    
    # the Routine "reset_screen" was not non-slip safe, so reset the non-slip timer
    routineTimer.reset()

    #Move to the next run
    thisExp.nextEntry()
    
# completed expInfo['runs'] repeats of 'runs'

close_experiment()
