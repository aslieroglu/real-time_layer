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
#prefs.hardware['audioLib'] = 'ptb'
#prefs.hardware['audioLatencyMode'] = '0'
from psychopy import sound, gui, visual, core, data, event, logging, clock, colors, layout
from psychopy.constants import (NOT_STARTED, STARTED, PLAYING, PAUSED,
                                STOPPED, FINISHED, PRESSED, RELEASED, FOREVER)

import numpy as np  # whole numpy lib is available, prepend 'np.'
from numpy import (sin, cos, tan, log, log10, pi, average,
                   sqrt, std, deg2rad, rad2deg, linspace, asarray)
from numpy.random import random, randint, normal, shuffle, choice as randchoice
import os  # handy system and path functions
import sys  # to get file system encoding

from psychopy.hardware import keyboard



# Ensure that relative paths start from the same directory as this script
_thisDir = os.path.dirname(os.path.abspath(__file__))
os.chdir(_thisDir)
# Store info about the experiment session
psychopyVersion = '2022.1.4'
expName = 'LayerNFB'  # from the Builder filename that created this script
expInfo = {
    'participant': 'ENTER SUBJECT ID',
    'session': '001',
    'config_file': '/data/pt_02900/Neurofeedback/config/config_layer.yaml',
    'runs': '5',
    #'volumes': '240',
    #'TR': '2',
    #'n_vols_up': '30',
    #'n_vols_down': '30',
    #'start_block': 'down',
    'colour_down': 'darkgray',
    'colour_up': 'darkgreen',
    'baseline Superior': '218.9',
    'baseline Middle': 0,
    'baseline Deep': '218.9',
    'mri_trigger_key': 't',
    'results dir': '/data/pt_02900/pilot/psychopydata'
}
dlg = gui.DlgFromDict(dictionary=expInfo, sortKeys=False, title=expName)
if dlg.OK == False:
    core.quit()  # user pressed cancel
expInfo['date'] = data.getDateStr()  # add a simple timestamp
expInfo['expName'] = expName
expInfo['psychopyVersion'] = psychopyVersion

# Data file name stem = absolute path + name; later add .psyexp, .csv, .log, etc
filename = os.path.normpath(expInfo['results dir']) + os.sep + u'data/%s_%s_session_%s' % (expInfo['participant'],expInfo['date'],expInfo['session'])

# An ExperimentHandler isn't essential but helps with data saving
thisExp = data.ExperimentHandler(name=expName, version='',
    extraInfo=expInfo, runtimeInfo=None,
    originPath='/data/pt_02900/Neurofeedback/code/NFB-controllers/layerExperiment.py',
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
# Setup ioHub
ioConfig = {}
ioSession = ioServer = eyetracker = None

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
    pos=(0, 0), height=0.05, wrapWidth=None, ori=0.0, 
    color='white', colorSpace='rgb', opacity=None, 
    languageStyle='LTR',
    depth=-1.0);

# Initialize components for Routine "sync_with_mri"
sync_with_mriClock = core.Clock()
sync_mri_key = keyboard.Keyboard()
sync_mri_msg = visual.TextStim(win=win, name='sync_mri_msg',
    text='Waiting for scanning to start ...',
    font='Open Sans',
    pos=(0, 0), height=0.05, wrapWidth=None, ori=0.0, 
    color='white', colorSpace='rgb', opacity=None, 
    languageStyle='LTR',
    depth=-1.0);

# Initialize components for Routine "volume"
volumeClock = core.Clock()
volume_placeholder = visual.TextStim(win=win, name='volume_placeholder',
    text=None,
    font='Open Sans',
    pos=(0, 0), height=0.05, wrapWidth=None, ori=0.0, 
    color=[0.0000, 0.0000, 0.0000], colorSpace='rgb', opacity=None, 
    languageStyle='LTR',
    depth=-1.0);

# Initialize components for Routine "complete_pending_nfb"
complete_pending_nfbClock = core.Clock()

# Initialize components for Routine "reset_screen"
reset_screenClock = core.Clock()

# Create some handy timers
globalClock = core.Clock()  # to track the time since experiment started
routineTimer = core.CountdownTimer()  # to track time remaining of each (non-slip) routine 

# ------Prepare to start Routine "setup_params"-------
continueRoutine = True
# update component parameters for each repeat
from nfbDisplayModels import timeseriesNFB
from resultsManager import resultsServerHandler
import yaml
exit_experiment = False
"""
expInfo['volumes'] =  int(expInfo['volumes'])
expInfo['TR'] = float(expInfo['TR'])
expInfo['n_vols_up'] = int(expInfo['n_vols_up'])
expInfo['n_vols_down'] = int(expInfo['n_vols_down'])
"""
expInfo['baseline Superior'] = float(expInfo['baseline Superior'])
expInfo['baseline Middle'] = float(expInfo['baseline Middle'])
expInfo['baseline Deep'] = float(expInfo['baseline Deep'])
#set up pyneal connections
config_file_available = False
results_server_available = False
try:
    config_file = open(expInfo["config_file"], 'r')
except OSError as e:
    logging.error(f"Couldnt open Pyneal Config file -> {e}")
    exit_experiment = False
else:
    with config_file:
        config = yaml.safe_load(config_file)
        config_file_available = True
if config_file_available:
    expInfo['volumes'] =  int(config['numTimepts'])
    expInfo['TR'] = float(config['TR'])
    expInfo['n_vols_up'] = int(config['numTimeptsUp'])
    expInfo['n_vols_down'] = int(config['numTimeptsDown'])
    expInfo['start_block'] = config['startBlock']
    n_blocks,rem =  divmod(expInfo['volumes'],(expInfo['n_vols_up'] + expInfo['n_vols_down']))
    if rem != 0:
        logging.exp(f"Non-integer no. of blocks per run. Exiting.")
    n_blocks = int(n_blocks)
    logging.info(f"Pyneal results server at {config['pynealHostIP']}:{config['resultsServerPort']}")
    result_server = resultsServerHandler(config['pynealHostIP'], config['resultsServerPort'])
    results_server_available = result_server.test_results_server()
else:
    logging.error("No config file")
    exit_experiment = True
# keep track of which components have finished
setup_paramsComponents = []
for thisComponent in setup_paramsComponents:
    thisComponent.tStart = None
    thisComponent.tStop = None
    thisComponent.tStartRefresh = None
    thisComponent.tStopRefresh = None
    if hasattr(thisComponent, 'status'):
        thisComponent.status = NOT_STARTED
# reset timers
t = 0
_timeToFirstFrame = win.getFutureFlipTime(clock="now")
setup_paramsClock.reset(-_timeToFirstFrame)  # t0 is time of first possible flip
frameN = -1

# -------Run Routine "setup_params"-------
while continueRoutine:
    # get current time
    t = setup_paramsClock.getTime()
    tThisFlip = win.getFutureFlipTime(clock=setup_paramsClock)
    tThisFlipGlobal = win.getFutureFlipTime(clock=None)
    frameN = frameN + 1  # number of completed frames (so 0 is the first frame)
    # update/draw components on each frame
    
    # check for quit (typically the Esc key)
    if endExpNow or defaultKeyboard.getKeys(keyList=["escape"]):
        core.quit()
    
    # check if all components have finished
    if not continueRoutine:  # a component has requested a forced-end of Routine
        break
    continueRoutine = False  # will revert to True if at least one component still running
    for thisComponent in setup_paramsComponents:
        if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
            continueRoutine = True
            break  # at least one component has not yet finished
    
    # refresh the screen
    if continueRoutine:  # don't flip if this routine is over or we'll get a blank screen
        win.flip()

# -------Ending Routine "setup_params"-------
for thisComponent in setup_paramsComponents:
    if hasattr(thisComponent, "setAutoDraw"):
        thisComponent.setAutoDraw(False)
# the Routine "setup_params" was not non-slip safe, so reset the non-slip timer
routineTimer.reset()

# ------Prepare to start Routine "setup_nfb"-------
continueRoutine = True
# update component parameters for each repeat
if expInfo['start_block'] == "down":
    block_design = np.concatenate([np.repeat("down",expInfo['n_vols_down']),np.repeat("up",expInfo['n_vols_up'])])
else:
    block_design = np.concatenate([np.repeat("up",expInfo['n_vols_up']),np.repeat("up",expInfo['n_vols_down'])])
run_design = np.tile(block_design,n_blocks)
block_boundaries = [0]
block_boundaries = np.where(run_design[:-1]!= run_design[1:])[0] + 1
block_boundaries = np.concatenate([[0],block_boundaries,[expInfo['volumes']]])
logging.exp(block_boundaries)
    
#create the timeseries NFB display
block_def = dict(order=run_design,
                 colour=dict(down=expInfo['colour_down'],up=expInfo['colour_up'])
                 )
logging.exp(block_def)
nfb = timeseriesNFB(win,
                    volumes=expInfo['volumes'],
                    baseline=1,
                    nfb_scale=dict(lower=-2,upper=2),
                    block_def=block_def
                    )

# keep track of which components have finished
setup_nfbComponents = []
for thisComponent in setup_nfbComponents:
    thisComponent.tStart = None
    thisComponent.tStop = None
    thisComponent.tStartRefresh = None
    thisComponent.tStopRefresh = None
    if hasattr(thisComponent, 'status'):
        thisComponent.status = NOT_STARTED
# reset timers
t = 0
_timeToFirstFrame = win.getFutureFlipTime(clock="now")
setup_nfbClock.reset(-_timeToFirstFrame)  # t0 is time of first possible flip
frameN = -1

# -------Run Routine "setup_nfb"-------
while continueRoutine:
    # get current time
    t = setup_nfbClock.getTime()
    tThisFlip = win.getFutureFlipTime(clock=setup_nfbClock)
    tThisFlipGlobal = win.getFutureFlipTime(clock=None)
    frameN = frameN + 1  # number of completed frames (so 0 is the first frame)
    # update/draw components on each frame
    
        
    
    
    # check for quit (typically the Esc key)
    if endExpNow or defaultKeyboard.getKeys(keyList=["escape"]):
        core.quit()
    
    # check if all components have finished
    if not continueRoutine:  # a component has requested a forced-end of Routine
        break
    continueRoutine = False  # will revert to True if at least one component still running
    for thisComponent in setup_nfbComponents:
        if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
            continueRoutine = True
            break  # at least one component has not yet finished
    
    # refresh the screen
    if continueRoutine:  # don't flip if this routine is over or we'll get a blank screen
        win.flip()

# -------Ending Routine "setup_nfb"-------
for thisComponent in setup_nfbComponents:
    if hasattr(thisComponent, "setAutoDraw"):
        thisComponent.setAutoDraw(False)
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
    currentLoop = runs
    # abbreviate parameter names if possible (e.g. rgb = thisRun.rgb)
    if thisRun != None:
        for paramName in thisRun:
            exec('{} = thisRun[paramName]'.format(paramName))
    
    # ------Prepare to start Routine "pause_and_check"-------
    continueRoutine = True
    # update component parameters for each repeat
    pause_check_key.keys = []
    pause_check_key.rt = []
    _pause_check_key_allKeys = []
    flag_proceed = False
    # keep track of which components have finished
    pause_and_checkComponents = [pause_check_key, pause_check_msg]
    for thisComponent in pause_and_checkComponents:
        thisComponent.tStart = None
        thisComponent.tStop = None
        thisComponent.tStartRefresh = None
        thisComponent.tStopRefresh = None
        if hasattr(thisComponent, 'status'):
            thisComponent.status = NOT_STARTED
    # reset timers
    t = 0
    _timeToFirstFrame = win.getFutureFlipTime(clock="now")
    pause_and_checkClock.reset(-_timeToFirstFrame)  # t0 is time of first possible flip
    frameN = -1
    
    # -------Run Routine "pause_and_check"-------
    while continueRoutine:
        # get current time
        t = pause_and_checkClock.getTime()
        tThisFlip = win.getFutureFlipTime(clock=pause_and_checkClock)
        tThisFlipGlobal = win.getFutureFlipTime(clock=None)
        frameN = frameN + 1  # number of completed frames (so 0 is the first frame)
        # update/draw components on each frame
        
        # *pause_check_key* updates
        waitOnFlip = False
        if pause_check_key.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
            # keep track of start time/frame for later
            pause_check_key.frameNStart = frameN  # exact frame index
            pause_check_key.tStart = t  # local t and not account for scr refresh
            pause_check_key.tStartRefresh = tThisFlipGlobal  # on global time
            win.timeOnFlip(pause_check_key, 'tStartRefresh')  # time at next scr refresh
            pause_check_key.status = STARTED
            # keyboard checking is just starting
            waitOnFlip = True
            win.callOnFlip(pause_check_key.clock.reset)  # t=0 on next screen flip
            win.callOnFlip(pause_check_key.clearEvents, eventType='keyboard')  # clear events on next screen flip
        if pause_check_key.status == STARTED and not waitOnFlip:
            theseKeys = pause_check_key.getKeys(keyList=['return','escape'], waitRelease=False)
            _pause_check_key_allKeys.extend(theseKeys)
            if len(_pause_check_key_allKeys):
                pause_check_key.keys = _pause_check_key_allKeys[0].name  # just the first key pressed
                pause_check_key.rt = _pause_check_key_allKeys[0].rt
                # a response ends the routine
                continueRoutine = False
        
        # *pause_check_msg* updates
        if pause_check_msg.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
            # keep track of start time/frame for later
            pause_check_msg.frameNStart = frameN  # exact frame index
            pause_check_msg.tStart = t  # local t and not account for scr refresh
            pause_check_msg.tStartRefresh = tThisFlipGlobal  # on global time
            win.timeOnFlip(pause_check_msg, 'tStartRefresh')  # time at next scr refresh
            pause_check_msg.setAutoDraw(True)
        if pause_check_msg.status == STARTED:
            if bool(flag_proceed):
                # keep track of stop time/frame for later
                pause_check_msg.tStop = t  # not accounting for scr refresh
                pause_check_msg.frameNStop = frameN  # exact frame index
                win.timeOnFlip(pause_check_msg, 'tStopRefresh')  # time at next scr refresh
                pause_check_msg.setAutoDraw(False)
        if pause_check_key.status == STARTED:
            theseKeys = pause_check_key.getKeys(["return","escape"])
            if 'return' in theseKeys:
                flag_proceed = True
                continueRoutine = False
            elif 'escape' in theseKeys:
                core.quit()
                continueRoutine = False
        
        # check for quit (typically the Esc key)
        if endExpNow or defaultKeyboard.getKeys(keyList=["escape"]):
            core.quit()
        
        # check if all components have finished
        if not continueRoutine:  # a component has requested a forced-end of Routine
            break
        continueRoutine = False  # will revert to True if at least one component still running
        for thisComponent in pause_and_checkComponents:
            if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
                continueRoutine = True
                break  # at least one component has not yet finished
        
        # refresh the screen
        if continueRoutine:  # don't flip if this routine is over or we'll get a blank screen
            win.flip()
    
    # -------Ending Routine "pause_and_check"-------
    for thisComponent in pause_and_checkComponents:
        if hasattr(thisComponent, "setAutoDraw"):
            thisComponent.setAutoDraw(False)
    # check responses
    if pause_check_key.keys in ['', [], None]:  # No response was made
        pause_check_key.keys = None
    runs.addData('pause_check_key.keys',pause_check_key.keys)
    if pause_check_key.keys != None:  # we had a response
        runs.addData('pause_check_key.rt', pause_check_key.rt)
    runs.addData('pause_check_key.started', pause_check_key.tStartRefresh)
    runs.addData('pause_check_key.stopped', pause_check_key.tStopRefresh)
    runs.addData('pause_check_msg.started', pause_check_msg.tStartRefresh)
    runs.addData('pause_check_msg.stopped', pause_check_msg.tStopRefresh)
    flag_proceed = False
    temp_block_boundaries = [i for i in block_boundaries]
    vol_idx  = 0
    pyneal_Q = []
    # the Routine "pause_and_check" was not non-slip safe, so reset the non-slip timer
    routineTimer.reset()
    
    # ------Prepare to start Routine "sync_with_mri"-------
    continueRoutine = True
    # update component parameters for each repeat
    sync_mri_key.keys = []
    sync_mri_key.rt = []
    _sync_mri_key_allKeys = []
    flag_proceed=False
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
                sync_mri_key.rt = _sync_mri_key_allKeys[0].rt
                # a response ends the routine
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
            if bool(flag_proceed):
                # keep track of stop time/frame for later
                sync_mri_msg.tStop = t  # not accounting for scr refresh
                sync_mri_msg.frameNStop = frameN  # exact frame index
                win.timeOnFlip(sync_mri_msg, 'tStopRefresh')  # time at next scr refresh
                sync_mri_msg.setAutoDraw(False)
        if sync_mri_key.status == STARTED:
            theseKeys = sync_mri_key.getKeys([expInfo['mri_trigger_key'],"escape"])
            if expInfo['mri_trigger_key'] in theseKeys:
                flag_proceed = True
                continueRoutine = False
            elif 'escape' in theseKeys:
                continue_experiment = False
                continueRoutine = False
                core.quit()
                
        
        # check for quit (typically the Esc key)
        if endExpNow or defaultKeyboard.getKeys(keyList=["escape"]):
            core.quit()
    
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
    if sync_mri_key.keys != None:  # we had a response
        runs.addData('sync_mri_key.rt', sync_mri_key.rt)
    runs.addData('sync_mri_key.started', sync_mri_key.tStartRefresh)
    runs.addData('sync_mri_key.stopped', sync_mri_key.tStopRefresh)
    runs.addData('sync_mri_msg.started', sync_mri_msg.tStartRefresh)
    runs.addData('sync_mri_msg.stopped', sync_mri_msg.tStopRefresh)
    flag_proceed = False
    # the Routine "sync_with_mri" was not non-slip safe, so reset the non-slip timer
    routineTimer.reset()
    
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
    
    for thisVolume in volumes:
        currentLoop = volumes
        # abbreviate parameter names if possible (e.g. rgb = thisVolume.rgb)
        if thisVolume != None:
            for paramName in thisVolume:
                exec('{} = thisVolume[paramName]'.format(paramName))
        
        # ------Prepare to start Routine "volume"-------
        continueRoutine = True
        routineTimer.add(expInfo['TR'])
        # update component parameters for each repeat
        if vol_idx == temp_block_boundaries[0]:
            logging.exp(f"Vol idx {vol_idx}")
            nfb.show_block(np.arange(temp_block_boundaries[0],temp_block_boundaries[1]))
            temp_block_boundaries = temp_block_boundaries[1:]
        # keep track of which components have finished
        volumeComponents = [volume_placeholder]
        for thisComponent in volumeComponents:
            thisComponent.tStart = None
            thisComponent.tStop = None
            thisComponent.tStartRefresh = None
            thisComponent.tStopRefresh = None
            if hasattr(thisComponent, 'status'):
                thisComponent.status = NOT_STARTED
        # reset timers
        t = 0
        _timeToFirstFrame = win.getFutureFlipTime(clock="now")
        volumeClock.reset(-_timeToFirstFrame)  # t0 is time of first possible flip
        frameN = -1
        
        # -------Run Routine "volume"-------
        while continueRoutine and routineTimer.getTime() > 0:
            # get current time
            t = volumeClock.getTime()
            tThisFlip = win.getFutureFlipTime(clock=volumeClock)
            tThisFlipGlobal = win.getFutureFlipTime(clock=None)
            frameN = frameN + 1  # number of completed frames (so 0 is the first frame)
            # update/draw components on each frame
            if len(pyneal_Q) > 0:
                result = result_server.get_result(pyneal_Q[0])
                if result and result["foundResults"]:
                    #read the feedback and process
                    sup = result['layers']['Superior'] / expInfo['baseline Superior'] -1
                    deep = result['layers']['Deep'] / expInfo['baseline Deep'] -1
                    feedback = deep/sup
                    nfb.show_feedback(pyneal_Q[0], feedback)
                    runs.addData(f"result.vol.{pyneal_Q[0]}",feedback)
                    runs.addData(f"result.t.vol.{pyneal_Q[0]}",win.getFutureFlipTime())
                    pyneal_Q = pyneal_Q[1:]
            
            # *volume_placeholder* updates
            if volume_placeholder.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
                # keep track of start time/frame for later
                volume_placeholder.frameNStart = frameN  # exact frame index
                volume_placeholder.tStart = t  # local t and not account for scr refresh
                volume_placeholder.tStartRefresh = tThisFlipGlobal  # on global time
                win.timeOnFlip(volume_placeholder, 'tStartRefresh')  # time at next scr refresh
                volume_placeholder.setAutoDraw(True)
            if volume_placeholder.status == STARTED:
                # is it time to stop? (based on global clock, using actual start)
                if tThisFlipGlobal > volume_placeholder.tStartRefresh + expInfo['TR']-frameTolerance:
                    # keep track of stop time/frame for later
                    volume_placeholder.tStop = t  # not accounting for scr refresh
                    volume_placeholder.frameNStop = frameN  # exact frame index
                    win.timeOnFlip(volume_placeholder, 'tStopRefresh')  # time at next scr refresh
                    volume_placeholder.setAutoDraw(False)
            
            # check for quit (typically the Esc key)
            if endExpNow or defaultKeyboard.getKeys(keyList=["escape"]):
                core.quit()
            
            # check if all components have finished
            if not continueRoutine:  # a component has requested a forced-end of Routine
                break
            continueRoutine = False  # will revert to True if at least one component still running
            for thisComponent in volumeComponents:
                if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
                    continueRoutine = True
                    break  # at least one component has not yet finished
            
            # refresh the screen
            if continueRoutine:  # don't flip if this routine is over or we'll get a blank screen
                win.flip()
        
        # -------Ending Routine "volume"-------
        for thisComponent in volumeComponents:
            if hasattr(thisComponent, "setAutoDraw"):
                thisComponent.setAutoDraw(False)
        runs.addData(f'start.vol.{vol_idx}', volume_placeholder.tStartRefresh)
        pyneal_Q.append(vol_idx)
        vol_idx += 1
        
    # completed expInfo['volumes'] repeats of 'volumes'
    
    
    # ------Prepare to start Routine "complete_pending_nfb"-------
    continueRoutine = True
    # update component parameters for each repeat
    logging.exp(f"Pending NFB {pyneal_Q}")
    while len(pyneal_Q) > 0 :
        result = result_server.get_result(pyneal_Q[0])
        if result and result["foundResults"]:
            sup = result['layers']['Superior'] / expInfo['baseline Superior'] -1
            deep = result['layers']['Deep'] / expInfo['baseline Deep'] -1
            feedback = deep/sup
            nfb.show_feedback(pyneal_Q[0], feedback)
            runs.addData(f"result.vol.{pyneal_Q[0]}",feedback)
            runs.addData(f"result.t.vol.{pyneal_Q[0]}",win.getFutureFlipTime())
            win.flip()
            pyneal_Q = pyneal_Q[1:]
    win.getMovieFrame()
    win.saveMovieFrames(f"{thisExp.dataFileName}_run_{runs.thisRepN}.png")
    continueRoutine = False
    # keep track of which components have finished
    complete_pending_nfbComponents = []
    for thisComponent in complete_pending_nfbComponents:
        thisComponent.tStart = None
        thisComponent.tStop = None
        thisComponent.tStartRefresh = None
        thisComponent.tStopRefresh = None
        if hasattr(thisComponent, 'status'):
            thisComponent.status = NOT_STARTED
    # reset timers
    t = 0
    _timeToFirstFrame = win.getFutureFlipTime(clock="now")
    complete_pending_nfbClock.reset(-_timeToFirstFrame)  # t0 is time of first possible flip
    frameN = -1
    
    # -------Run Routine "complete_pending_nfb"-------
    while continueRoutine:
        # get current time
        t = complete_pending_nfbClock.getTime()
        tThisFlip = win.getFutureFlipTime(clock=complete_pending_nfbClock)
        tThisFlipGlobal = win.getFutureFlipTime(clock=None)
        frameN = frameN + 1  # number of completed frames (so 0 is the first frame)
        # update/draw components on each frame
        
        # check for quit (typically the Esc key)
        if endExpNow or defaultKeyboard.getKeys(keyList=["escape"]):
            core.quit()
        
        # check if all components have finished
        if not continueRoutine:  # a component has requested a forced-end of Routine
            break
        continueRoutine = False  # will revert to True if at least one component still running
        for thisComponent in complete_pending_nfbComponents:
            if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
                continueRoutine = True
                break  # at least one component has not yet finished
        
        # refresh the screen
        if continueRoutine:  # don't flip if this routine is over or we'll get a blank screen
            win.flip()
    
    # -------Ending Routine "complete_pending_nfb"-------
    for thisComponent in complete_pending_nfbComponents:
        if hasattr(thisComponent, "setAutoDraw"):
            thisComponent.setAutoDraw(False)
    # the Routine "complete_pending_nfb" was not non-slip safe, so reset the non-slip timer
    routineTimer.reset()
    
    # ------Prepare to start Routine "reset_screen"-------
    continueRoutine = True
    # update component parameters for each repeat
    core.wait(5) #to give some time for the experince to sink in
    nfb.reset()
    vol_idx = 0
    flag_proceed = False
    # keep track of which components have finished
    reset_screenComponents = []
    for thisComponent in reset_screenComponents:
        thisComponent.tStart = None
        thisComponent.tStop = None
        thisComponent.tStartRefresh = None
        thisComponent.tStopRefresh = None
        if hasattr(thisComponent, 'status'):
            thisComponent.status = NOT_STARTED
    # reset timers
    t = 0
    _timeToFirstFrame = win.getFutureFlipTime(clock="now")
    reset_screenClock.reset(-_timeToFirstFrame)  # t0 is time of first possible flip
    frameN = -1
    
    # -------Run Routine "reset_screen"-------
    while continueRoutine:
        # get current time
        t = reset_screenClock.getTime()
        tThisFlip = win.getFutureFlipTime(clock=reset_screenClock)
        tThisFlipGlobal = win.getFutureFlipTime(clock=None)
        frameN = frameN + 1  # number of completed frames (so 0 is the first frame)
        # update/draw components on each frame
        
        # check for quit (typically the Esc key)
        if endExpNow or defaultKeyboard.getKeys(keyList=["escape"]):
            core.quit()
        
        # check if all components have finished
        if not continueRoutine:  # a component has requested a forced-end of Routine
            break
        continueRoutine = False  # will revert to True if at least one component still running
        for thisComponent in reset_screenComponents:
            if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
                continueRoutine = True
                break  # at least one component has not yet finished
        
        # refresh the screen
        if continueRoutine:  # don't flip if this routine is over or we'll get a blank screen
            win.flip()
    
    # -------Ending Routine "reset_screen"-------
    for thisComponent in reset_screenComponents:
        if hasattr(thisComponent, "setAutoDraw"):
            thisComponent.setAutoDraw(False)
    # the Routine "reset_screen" was not non-slip safe, so reset the non-slip timer
    routineTimer.reset()
    thisExp.nextEntry()
    
# completed expInfo['runs'] repeats of 'runs'


# Flip one final time so any remaining win.callOnFlip() 
# and win.timeOnFlip() tasks get executed before quitting
win.flip()

# these shouldn't be strictly necessary (should auto-save)
thisExp.saveAsWideText(filename+'.csv', delim='auto')
thisExp.saveAsPickle(filename)
logging.flush()
# make sure everything is closed down
if eyetracker:
    eyetracker.setConnectionState(False)
thisExp.abort()  # or data files will save again on exit
win.close()
core.quit()
