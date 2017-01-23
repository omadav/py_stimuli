'''
Simple iohub eye tracker movie player. Presentation of movies is contingent on
central fixation.
No iohub config .yaml files are used.
Setup for an EyeLink(C) 1000 Desktop System. 
To to use a different eye tracker implementation, change the 
iohub_tracker_class_path and eyetracker_config dict script variables.
Currently loading raw (uncompressed) videos, 
future versions should read compressed movies-
    video: H.264 compressed,
    audio: Linear PCM
'''
from psychopy import core, visual
from psychopy.iohub.client import launchHubServer

import glob, time
import numpy as np

# Find movies matching wildcard search
videopath = '/home/adam/Desktop/virtBox_share/JonesStimset/identity1/'
videolist = glob.glob(videopath + '*100_audVid.avi')

# Number of trials of each stimulus to run
BLOCK_REPS = 1
TRIAL_COUNT = len(videolist) * BLOCK_REPS

# Set-up screen
SCREEN_SIZE = np.array([1280, 1024])
PHOTO_SIZE = 100
PHOTO_POS = (SCREEN_SIZE - PHOTO_SIZE)/2 * [1, -1]

# toggle for presence of tracker
EYE_TRACKER = 0; # 1: yes, 0: no
# toggle to simulate tracker activity with mouse
SIMULATE = 1; # 1: yes, 0: no
    
if EYE_TRACKER:
    # Set-up tracker configuration dict
    iohub_tracker_class_path = 'eyetracker.hw.sr_research.eyelink.EyeTracker'
    eyetracker_config = dict()
    eyetracker_config['name'] = 'tracker'
    if SIMULATE:
        eyetracker_config['simulation_mode'] = True
    else:
        eyetracker_config['model_name'] = 'EYELINK 1000 DESKTOP'
        eyetracker_config['runtime_settings'] = dict(sampling_rate=1000, 
            track_eyes='RIGHT')

    # Since no experiment or session code is given, no iohub hdf5 file
    # will be saved, but device events are still available at runtime
    io = launchHubServer(**{iohub_tracker_class_path: eyetracker_config})
    # Get iohub device for tracker
    tracker = io.devices.tracker
else:
    io = launchHubServer()
    
# Get iohub devices for future access
keyboard = io.devices.keyboard
display = io.devices.display

if EYE_TRACKER:
    # Run eyetracker calibration
    r = tracker.runSetupProcedure()
    
win = visual.Window(SCREEN_SIZE.tolist(),
                    units='pix',
                    fullscr=True,
                    allowGUI=False,
                    color='black'
                    )

# Define window objects
gaze_ok_region = visual.Circle(win, radius=200, units='pix')
gaze_dot = visual.GratingStim(win, tex=None, mask='gauss', pos=(0, 0),
                              size=(66, 66), color='green', units='pix')
photodiode = visual.GratingStim(win, tex=None, mask='none', pos=PHOTO_POS.tolist(),
                                size=100)

text_stim_str = 'Eye Position: %.2f, %.2f. In Region: %s\n'
text_stim_str += 'Trial #: %d\n'
text_stim_str += 'Press space key to skip trial.'

missing_gpos_str = 'Eye Position: MISSING. In Region: No\n'
missing_gpos_str += 'Press space key to skip trial.'
text_stim = visual.TextStim(win, text=text_stim_str,
                            pos=[0, int((-win.size[1]/2)*0.8)], height=24,
                                 color='white',
                                 alignHoriz='center',
                                 alignVert='center', 
                                 wrapWidth=win.size[0] * .9)
                                 
globalClock = core.Clock()  # to track the time since experiment started

# Run blocks.....
for block in range(BLOCK_REPS):
             
    t = 1         
    # Run Trials.....
    for vidPath in videolist:
    
        # Create movie stim by loading movie from list
        mov = visual.MovieStim3(win, vidPath, size=(366, 332), fps = 30,
                                flipVert=False, flipHoriz=False, loop=False) 
    
        io.clearEvents()
        if EYE_TRACKER:
            tracker.setRecordingState(True)
        run_trial = True
#        tstart_time = core.getTime()
        
        # Start the movie stim by preparing it to play
        shouldflip = mov.play()
        
        while (run_trial is True)&(mov.status != visual.FINISHED):
                
            # if tracker is on, test whether subject is fixating
            if EYE_TRACKER:
                # Get the latest gaze position in display coord space
                gpos = tracker.getLastGazePosition()
        
                # Update stim based on gaze position
                valid_gaze_pos = isinstance(gpos, (tuple, list))
                gaze_in_region = valid_gaze_pos and gaze_ok_region.contains(gpos)
            else: # else ignore
                valid_gaze_pos = True
                gaze_in_region = True
                
            if valid_gaze_pos:
                # If we have a gaze position from the tracker, update gc stim
                # and text stim
                if gaze_in_region:
                    gaze_in_region = 'Yes'
                    
                    # Only flip when a new frame should be displayed
                    if shouldflip:
                        # Movie has already been drawn, so just draw text stim and flip
                        text.draw()
                        win.flip()
                    else:
                        # Give the OS a break if a flip is not needed
                        time.sleep(0.001)
                        
                    # Draw movie stim again
                    shouldflip = mov.draw()
                    photodiode.draw()
                else:
                    gaze_in_region = 'No'
                    mov.status = visual.FINISHED
                        
                TRIAL_N = t + block * len(videolist)
                # Update text
                if EYE_TRACKER:
                    text_stim.text = text_stim_str % (gpos[0], gpos[1], gaze_in_region, TRIAL_N)
                    gaze_dot.setPos(gpos)
                else:
                    text_stim.text = missing_gpos_str
            else:
                # Otherwise just update text stim
                text_stim.text = missing_gpos_str
        
            # Redraw stim
            gaze_ok_region.draw()
            text_stim.draw()
            if valid_gaze_pos:
                if EYE_TRACKER:
                gaze_dot.draw()
        
            # Display updated stim on screen
            flip_time = win.flip()
        
            # Check any new keyboard char events for a space key
            # If one is found, set the trial end variable
            if ' ' in keyboard.getPresses() or mov.status == visual.FINISHED:
                run_trial = False
    
        # Current Trial is Done
    
        # Redraw stim
        gaze_ok_region.draw()
        text_stim.draw()
        # Display updated stim on screen
        flip_time = win.flip(clearBuffer=True)
        
        if EYE_TRACKER:
            # Stop eye data recording
            tracker.setRecordingState(False)
        
        t += 1        
        time.sleep(.5)

# All Trials are done
# End experiment
win.close()
if EYE_TRACKER:
    tracker.setConnectionState(False)
io.quit()
core.quit()
