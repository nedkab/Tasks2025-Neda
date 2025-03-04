# Auhtor: Neda Kaboodvand, neda.neuroscience@gmail.com

import os, sys, random
import numpy as np
from datetime import datetime
from psychopy import visual, core, event, data, gui, logging

from psychopy.hardware import keyboard
kb = keyboard.Keyboard()  # create a persistent keyboard object

# -------------------------------------------------------------------------
# --------------------------- PARAMETERS -----------------------------------
# -------------------------------------------------------------------------
maxResponseTime   = 1.25   # same as original
feedbackDuration  = 0.5    # per-trial feedback in practice
fixationSpan      = (0.25, 0.25)  # time range for fixation cross
ITIspan           = (0.5, 1.0)    # random ITI range
prepareBlockDur   = 2.0           # time before each block starts

# Stop-signal delays (SSD) logic
initialSSD    = 0.2
ssdIncrement  = 0.05
ssdDecrement  = 0.05

# Keys
leftKeys   = ['left','1','num_1']
rightKeys  = ['right','2','num_2']
downKeys   = ['down']
escapeKey  = ['escape']
allResp    = leftKeys + rightKeys + downKeys

# For data files
practiceConditionsFile = 'PracticeTrialConditions.csv'
mainConditionsFile     = 'MainTrialConditions.csv'

# Number of practice reps (4 if doPractice, else 0)
practiceReps = 4  

# Number of main blocks and repetitions within each block
nMainBlocks = 4  
blockReps   = 2  

# -------------------------------------------------------------------------
# --------------------------- DIALOG / SETUP -------------------------------
# -------------------------------------------------------------------------
_thisDir = os.path.dirname(os.path.abspath(__file__))
os.chdir(_thisDir)

expName = 'StopChangeTask'
from numpy.random import randint
expInfo = {
    'participant': f"{randint(0,999999):06d}",
    'session': '001',
    'doPractice': True  # set to False to skip practice
}
dlg = gui.DlgFromDict(dictionary=expInfo, sortKeys=False, title=expName)
if not dlg.OK:
    core.quit()

if isinstance(expInfo['doPractice'], str):
    expInfo['doPractice'] = (expInfo['doPractice'].lower() == 'true')

filename = os.path.join(_thisDir, 'data',
    f"{expInfo['participant']}_{expName}_{data.getDateStr()}")
thisExp = data.ExperimentHandler(name=expName,
                                 version='',
                                 extraInfo=expInfo,
                                 dataFileName=filename)
logging.console.setLevel(logging.WARNING)

# -------------------------------------------------------------------------
# --------------------------- WINDOW ---------------------------------------
# -------------------------------------------------------------------------
win = visual.Window(
    size=[1920, 1080], fullscr=True, screen=0,
    winType='pyglet', monitor='testMonitor',
    color=[-1, -1, -1], colorSpace='rgb',
    units='height'
)
win.mouseVisible = False

# -------------------------------------------------------------------------
# --------------------------- HELPER FUNCTIONS -----------------------------
# -------------------------------------------------------------------------
def check_for_esc():
    if 'escape' in event.getKeys():
        thisExp.saveAsWideText(filename+'.csv')
        thisExp.saveAsPickle(filename)
        win.close()
        core.quit()

def wait_for_space():
    event.clearEvents()
    while True:
        keys = event.getKeys(keyList=escapeKey+['space'])
        if keys:
            if 'escape' in keys:
                thisExp.saveAsWideText(filename+'.csv')
                thisExp.saveAsPickle(filename)
                win.close()
                core.quit()
            if 'space' in keys:
                break
        core.wait(0.01)

def log_on_flip(label):
    def callback():
        nowSec = core.getTime()
        nowStr = datetime.now().strftime('%Y-%m-%d_%H:%M:%S.%f')
        thisExp.addData(f"{label}_coreTime", nowSec)
        thisExp.addData(f"{label}_datetime", nowStr)
    return callback

# -------------------------------------------------------------------------
# --------------------------- STIMULI --------------------------------------
# -------------------------------------------------------------------------
planeStim = visual.ImageStim(
    win=win,
    image=None,  # will be set to PlaneLeft.png or PlaneRight.png
    pos=(0,0),
    size=(0.28,0.28)
)
planeLeftPath  = os.path.join(_thisDir, 'PlaneLeft.png')
planeRightPath = os.path.join(_thisDir, 'PlaneRight.png')

fuelStim = visual.ImageStim(
    win=win,
    image=os.path.join(_thisDir, 'fuel.png'),
    pos=(0,0),
    size=(0.15,0.15)
)

fixationCross = visual.TextStim(
    win=win,
    text='+',
    height=0.07,
    color='white'
)

instrText = visual.TextStim(
    win=win,
    text="",
    height=0.05, 
    color='white'
)

# Square trigger (as in KidFlanker_runner.py)
square_size=0.1
square_position=(0.8 - square_size/2, -0.5 + square_size/2)
blinkSquare = visual.Rect(
    win=win,
    width=square_size,
    height=square_size,
    fillColor='white',
    lineColor=None,
    pos=square_position
)

# Per-trial feedback (for practice)
feedback_correct   = visual.TextStim(win=win, text="Correct!",    color='lime', height=0.06)
feedback_incorrect = visual.TextStim(win=win, text="Incorrect",   color='red',  height=0.06)
feedback_timeout   = visual.TextStim(win=win, text="Respond faster!", color='white', height=0.06)

feedbackText = visual.TextStim(win=win, text="", height=0.05, color='white')
doneText     = visual.TextStim(win=win, text="Done!\nPress any key to exit.", height=0.05, color='white')

# Optional blink at start
def doBlink(num=4, onTime=0.2, offTime=0.2):
    for _ in range(num):
        blinkSquare.setAutoDraw(True)
        win.flip()
        core.wait(onTime)
        blinkSquare.setAutoDraw(False)
        win.flip()
        core.wait(offTime)

doBlink()

# -------------------------------------------------------------------------
# --------------------------- INSTRUCTIONS ---------------------------------
# -------------------------------------------------------------------------
if expInfo['doPractice']:
    instr = ("Stop-Change Task\n\n"
             "On each trial:\n"
             " - Plane points LEFT or RIGHT ⇒ press that arrow.\n"
             " - If 'fuel gauge' appears ⇒ press DOWN arrow *instead*.\n\n"
             "We'll do practice first (with feedback).\n\n"
             "Press SPACE to begin practice.")
else:
    instr = ("Stop-Change Task\n\n"
             "On each trial:\n"
             " - Plane points LEFT or RIGHT ⇒ press that arrow.\n"
             " - If 'fuel gauge' appears ⇒ press DOWN arrow *instead*.\n\n"
             "No practice. We'll go straight to main task.\n\n"
             "Press SPACE to begin.")
instrText.text = instr
instrText.draw()
win.flip()
wait_for_space()

# -------------------------------------------------------------------------
# --------------------------- PRACTICE TRIALS ------------------------------
# -------------------------------------------------------------------------
p_nReps = practiceReps if expInfo['doPractice'] else 0
if p_nReps > 0 and not os.path.exists(practiceConditionsFile):
    logging.warning(f"Practice file {practiceConditionsFile} not found! Skipping practice.")
    p_nReps = 0

practiceTrials = data.TrialHandler(
    nReps=p_nReps, 
    method='random',
    trialList=data.importConditions(practiceConditionsFile) if os.path.exists(practiceConditionsFile) else [],
    name='practiceTrials'
)
thisExp.addLoop(practiceTrials)
practiceSSD = initialSSD

p_goRTs       = []
p_numGoOmit   = 0
p_numGoResp   = 0
p_numGoTotal  = 0
p_numStop     = 0
p_numStopFail = 0

win.flip()
core.wait(prepareBlockDur)

for trial in practiceTrials:
    arrowDirRaw = trial['arrowDirection'].strip().lower()  # 'left' or 'right'
    stopGoRaw   = trial['stopOrGo'].strip().lower()         # 'go' or 'stop'

    # 1) Fixation
    fixDur = random.uniform(*fixationSpan)
    fixationCross.setAutoDraw(True)
    win.callOnFlip(log_on_flip("PracticeFix_onset"))
    win.flip()
    core.wait(fixDur)
    fixationCross.setAutoDraw(False)
    win.flip()
    check_for_esc()

    # 2) Show plane and trigger square; if STOP trial, later show fuel cue.
    if arrowDirRaw == 'left':
        planeStim.image = planeLeftPath
    else:
        planeStim.image = planeRightPath

    planeStim.setAutoDraw(True)
    blinkSquare.setAutoDraw(True)
    fuelStim.setAutoDraw(False)

    # Clear any leftover key events from the keyboard
    kb.clearEvents()

    clock = core.Clock()
    kb.clock.reset()  # reset the keyboard clock
    win.callOnFlip(log_on_flip("PracticeTrial_onset"))
    win.callOnFlip(clock.reset)
    win.flip()

    responded  = False
    wasCorrect = False
    rt         = None
    shownFuel  = False
    pressed    = None

    # Use a while loop that polls for key responses with an explicit keyList and time stamp.
    while clock.getTime() < maxResponseTime:
        check_for_esc()
        t = clock.getTime()
        # For STOP trials, show fuel cue after SSD delay
        if (stopGoRaw == 'stop') and (not shownFuel) and (t >= practiceSSD):
            fuelStim.setAutoDraw(True)
            win.callOnFlip(log_on_flip("PracticeFuel_onset"))
            win.flip()
            shownFuel = True

        keys = kb.getKeys(keyList=allResp+escapeKey, waitRelease=False)
        if keys:
            thisKey = keys[0]
            key = thisKey.name
            rt = thisKey.rt
            if key in escapeKey:
                thisExp.saveAsWideText(filename+'.csv')
                thisExp.saveAsPickle(filename)
                win.close()
                core.quit()
            else:
                responded = True
                pressed = key
                break
        win.flip()

    planeStim.setAutoDraw(False)
    blinkSquare.setAutoDraw(False)
    fuelStim.setAutoDraw(False)
    win.flip()

    # 3) Determine correctness
    if stopGoRaw == 'go':
        p_numGoTotal += 1
        if responded:
            if ((arrowDirRaw == 'left' and pressed in leftKeys) or 
                (arrowDirRaw == 'right' and pressed in rightKeys)):
                wasCorrect = True
            p_numGoResp += 1
            p_goRTs.append(rt)
        else:
            p_numGoOmit += 1
            p_goRTs.append(maxResponseTime)
    else:
        p_numStop += 1
        if responded and pressed in downKeys:
            wasCorrect = True
        if wasCorrect:
            practiceSSD += ssdIncrement
        else:
            practiceSSD = max(0, practiceSSD - ssdDecrement)
            if responded:
                p_numStopFail += 1

    # 4) Provide feedback (practice only)
    if wasCorrect:
        fbStim = feedback_correct
    else:
        fbStim = feedback_incorrect if responded else feedback_timeout

    fbStim.setAutoDraw(True)
    itidur = random.uniform(*ITIspan)
    win.callOnFlip(log_on_flip("PracticeITI_onset"))
    win.flip()
    core.wait(itidur)
    fbStim.setAutoDraw(False)
    win.flip()

    practiceTrials.addData('arrowDir', arrowDirRaw)
    practiceTrials.addData('stopOrGo', stopGoRaw)
    practiceTrials.addData('SSD_used', practiceSSD if stopGoRaw=='stop' else 0)
    practiceTrials.addData('response', pressed)
    practiceTrials.addData('rt', rt)
    practiceTrials.addData('correct', wasCorrect)
    thisExp.nextEntry()

if (p_nReps > 0) and (p_numGoTotal > 0):
    meanGo = np.mean(p_goRTs) * 1000
    pStopFailRate = (p_numStopFail / p_numStop) if (p_numStop > 0) else 0
    summ = (f"Practice done!\n\n"
            f"Mean GO RT = {meanGo:.1f} ms\n"
            f"GO omissions = {p_numGoOmit}\n"
            f"STOP failures = {p_numStopFail} (p={pStopFailRate:.2f})\n\n"
            "Press SPACE to continue.")
    feedbackText.text = summ
    feedbackText.setAutoDraw(True)
    win.flip()
    wait_for_space()
    feedbackText.setAutoDraw(False)
    win.flip()

# -------------------------------------------------------------------------
# --------------------------- MAIN BLOCKS ----------------------------------
# -------------------------------------------------------------------------
if not os.path.exists(mainConditionsFile):
    logging.error(f"Main conditions file {mainConditionsFile} not found! No main blocks.")
    nMainBlocks = 0

mainBlocks = data.TrialHandler(
    nReps=nMainBlocks, 
    method='sequential',
    trialList=[None],
    name='mainBlocks'
)
thisExp.addLoop(mainBlocks)
SSD = initialSSD  # track SSD for main task

blockIdx = 0
for block in mainBlocks:
    blockIdx += 1

    # Optional block instruction
    feedbackText.text = f"Prepare for Block {blockIdx}. Press SPACE to continue."
    feedbackText.setAutoDraw(True)
    win.flip()
    wait_for_space()
    feedbackText.setAutoDraw(False)
    win.flip()
    core.wait(prepareBlockDur)

    trials = data.TrialHandler(
        nReps=blockReps, 
        method='random',
        trialList=data.importConditions(mainConditionsFile) if os.path.exists(mainConditionsFile) else [],
        name='trialsBlock'
    )
    thisExp.addLoop(trials)

    # Block performance accumulators
    b_goRTs       = []
    b_numGoOmit   = 0
    b_numGoResp   = 0
    b_numGoTotal  = 0
    b_numStop     = 0
    b_numStopFail = 0

    for t in trials:
        arrowDirRaw = t['arrowDirection'].strip().lower()
        stopGoRaw   = t['stopOrGo'].strip().lower()

        # Fixation
        fixDur = random.uniform(*fixationSpan)
        fixationCross.setAutoDraw(True)
        win.callOnFlip(log_on_flip(f"Block{blockIdx}_Fix_onset"))
        win.flip()
        core.wait(fixDur)
        fixationCross.setAutoDraw(False)
        win.flip()
        check_for_esc()

        # Plane and square; display fuel cue for STOP trials after SSD delay
        if arrowDirRaw == 'left':
            planeStim.image = planeLeftPath
        else:
            planeStim.image = planeRightPath

        planeStim.setAutoDraw(True)
        blinkSquare.setAutoDraw(True)
        fuelStim.setAutoDraw(False)
        #event.clearEvents()
        # Clear any leftover key events from the keyboard
        kb.clearEvents()


        clock = core.Clock()
        kb.clock.reset()  # reset the keyboard clock
        lblStart = f"Block{blockIdx}_Trial_onset"
        win.callOnFlip(log_on_flip(lblStart))
        win.callOnFlip(clock.reset)
        win.flip()

        responded  = False
        wasCorrect = False
        rt         = None
        shownFuel  = False
        pressed    = None

        while clock.getTime() < maxResponseTime:
            check_for_esc()
            t_current = clock.getTime()
            if (stopGoRaw == 'stop') and (not shownFuel) and (t_current >= SSD):
                fuelStim.setAutoDraw(True)
                lblFuel = f"Block{blockIdx}_Fuel_onset"
                win.callOnFlip(log_on_flip(lblFuel))
                win.flip()
                shownFuel = True

            keys = kb.getKeys(keyList=allResp+escapeKey, waitRelease=False)
            if keys:
                thisKey = keys[0]
                key = thisKey.name
                rt = thisKey.rt
                if key in escapeKey:
                    thisExp.saveAsWideText(filename+'.csv')
                    thisExp.saveAsPickle(filename)
                    win.close()
                    core.quit()
                else:
                    responded = True
                    pressed = key
                    break
            win.flip()

        planeStim.setAutoDraw(False)
        blinkSquare.setAutoDraw(False)
        fuelStim.setAutoDraw(False)
        win.flip()

        # Determine correctness for main trials
        if stopGoRaw == 'go':
            b_numGoTotal += 1
            if responded:
                if ((arrowDirRaw == 'left' and pressed in leftKeys) or
                    (arrowDirRaw == 'right' and pressed in rightKeys)):
                    wasCorrect = True
                b_numGoResp += 1
                b_goRTs.append(rt)
            else:
                b_numGoOmit += 1
                b_goRTs.append(maxResponseTime)
        else:
            b_numStop += 1
            if responded and pressed in downKeys:
                wasCorrect = True
            if wasCorrect:
                SSD += ssdIncrement
            else:
                SSD = max(0, SSD - ssdDecrement)
                if responded:
                    b_numStopFail += 1

        itidur = random.uniform(*ITIspan)
        lblITI = f"Block{blockIdx}_ITI_onset"
        win.callOnFlip(log_on_flip(lblITI))
        win.flip()
        core.wait(itidur)
        win.flip()

        trials.addData('arrowDir', arrowDirRaw)
        trials.addData('stopOrGo', stopGoRaw)
        trials.addData('SSD_used', SSD if stopGoRaw=='stop' else 0)
        trials.addData('response', pressed)
        trials.addData('rt', rt)
        trials.addData('correct', wasCorrect)
        thisExp.nextEntry()

    # Optionally show block summary feedback here (if desired)
    block_goMean = np.mean(b_goRTs) * 1000 if b_goRTs else 0
    block_stopFailRate = (b_numStopFail / b_numStop) if b_numStop > 0 else 0
    blockMsg = (f"Block {blockIdx} finished!\n\n"
                f"Mean GO RT: {block_goMean:.1f} ms\n"
                f"GO omissions: {b_numGoOmit}\n"
                f"STOP failures: {b_numStopFail} (p={block_stopFailRate:.2f})\n\n"
                "Press SPACE to continue.")
    feedbackText.text = blockMsg
    feedbackText.setAutoDraw(True)
    win.flip()
    wait_for_space()
    feedbackText.setAutoDraw(False)
    win.flip()

# -------------------------------------------------------------------------
# --------------------------- DONE -----------------------------------------
# -------------------------------------------------------------------------
doneText.draw()
win.flip()
event.waitKeys()

thisExp.saveAsWideText(filename+'.csv')
thisExp.saveAsPickle(filename)
win.close()
core.quit()
