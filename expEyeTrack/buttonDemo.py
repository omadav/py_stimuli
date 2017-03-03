# -*- coding: utf-8 -*-
"""
Created on Thu Feb 16 16:49:07 2017

@author: root
"""

def buttonDemo( win, joystick, keyboard ):
    
    from psychopy import visual # core, 
#    from psychopy.iohub.client import launchHubServer
    
    # Force psychopy to use particular audio library
    from psychopy import prefs
    prefs.general['audioLib'] = ['pygame']
    from psychopy import sound
    
    import glob, gtk, time # , csv, datetime
    import numpy as np
    
    # Find movies matching wildcard search
    videopath = '/home/adam/Desktop/py_stimuli/JonesStimset/'
    videolist = glob.glob(videopath + '*rad_100_audVid.avi')
    videolist.sort()
    
     # Get current screen size (works for single monitor only)
    width = gtk.gdk.screen_width()
    height = gtk.gdk.screen_height()

    img_pos_list = np.array([[0,height/8],[height/6,0],[0,-height/8],[-height/6,0]])
    movie_pos_list = np.array([[0,height/3.5],[height/3.5,0],[0,-height/3.5],[-height/3.5,0]])
    
    # Choose which button image to show    
    #button_image = "buttonIcon_N64.png"
    button_image = "xbox_dpad.png"
    cue_image = "xbox_dpad_cue.png"
       
    img_list_button = [button_image]*4
    img_list_cue = [cue_image]*4
    
#    img_list_button = ["xbox_Y.png","xbox_B.png","xbox_A.png","xbox_X.png"]
#    img_list_cue = img_list_button
    
    start_image = "xbox_start.png"
    back_image = "xbox_back.png"
    wait_img_list = [start_image, back_image]
    
    # Create list of functions corresponding to each button used
    cmd_list = [lambda:joystick.dpadUp(),
                lambda:joystick.dpadRight(),
                lambda:joystick.dpadDown(),
                lambda:joystick.dpadLeft()]  
    
#    cmd_list = [lambda:joystick.Y(),
#                lambda:joystick.B(),
#                lambda:joystick.A(),
#                lambda:joystick.X()]  
    
    RECORD = 0
    
    train_rep = 0
    
    vid_play = True
    
    repeat_demo = True
    
    # Load images
    warn_img = visual.ImageStim(win=win, image="training_mode.png",
                                units="pix")
    warn_img.size *= .75  # Scale the image relative to initial size
    
    dec_img = visual.ImageStim(win=win,image="decision.png",
                               units="pix")
    dec_img.size *= .75  # Scale the image relative to initial size
    
    OldRange = (1.0 - 0)  
    NewRange = (1.0 - -1.0)  
    logDist = (np.logspace(0, 1.0, 200, endpoint=True) / 10)
    scaled_logDist = (((logDist * NewRange) / OldRange) + -1.0)*-1
        
    while repeat_demo:
                                           
        instr_text = visual.TextStim(win, text="...by pressing these buttons:",
                                   height=30,
                                   alignHoriz='center',
                                   wrapWidth = width,
                                   pos = [0, height/2 - 50]) 
                                   
        fin_text = visual.TextStim(win, text="<Press Start to skip>",
                                   height=35,
                                   alignHoriz='center',
                                   italic=True,
                                   wrapWidth = width,
                                   color = 'grey',
                                   pos=[0,-height/2 + 50])
                                   
        press_text = visual.TextStim(win, text="PRESS",
                                   height=25,
                                   alignHoriz='center',
                                   bold=True,
                                   wrapWidth = width,
                                   color = 'yellow') 
                         
        # Show warning and animate fade
        if train_rep==0:
            warn_img.contrast = 1
            for i in 1-(np.logspace(0.0, 1.0, 200) / 10):
                warn_img.contrast = i 
                warn_img.draw()    
                win.flip()
                if RECORD:
                    # Store an image of every upcoming screen refresh:
                    win.getMovieFrame(buffer='back')
        
        # Show 1st block of instructions        
        text = visual.TextStim(win,height=48,
                                   text="When you see this sign...",
                                   pos=[0,height/4],
                                   alignHoriz='center')
        # Animate
        for i in scaled_logDist:
            text.contrast = i 
            text.draw()
#            dec_img.contrast = i
            dec_img.draw()
            win.flip()
            if RECORD:
                # Store an image of every upcoming screen refresh:
                win.getMovieFrame(buffer='back')
            
            # Check keyboard for button presses
            keys = keyboard.getPresses()
            # Check joystick for button presses    
            if joystick.Start() or (' ' in keys):
                vid_play = False
                repeat_demo = False
                break
            
        if vid_play==False:
            break                         
                                      
        # Show 2nd block of instructions        
        text = visual.TextStim(win,height=48,
                                   text="Identify which of these 4 people\nyou see or hear...",
                                   alignHoriz='center')
    
        # Animate
        for i in scaled_logDist:
            text.contrast = i 
            text.draw()    
            win.flip()
            if RECORD:
                # Store an image of every upcoming screen refresh:
                win.getMovieFrame(buffer='back')
            
            # Check keyboard for button presses
            keys = keyboard.getPresses()
            # Check joystick for button presses    
            if joystick.Start() or (' ' in keys):
                vid_play = False
                repeat_demo = False
                break
            
        if vid_play==False:
            break
                
                
        for i in range(len(videolist)):
            
            img = visual.ImageStim(win=win, image=img_list_button[i], units="pix")
            img.size *= .75  # Scale the image relative to initial size
            img.ori += 90.0*i

            cue_img = visual.ImageStim(win=win, image=img_list_cue[i], units="pix")
            cue_img.size *= .75  # Scale the image relative to initial size
            cue_img.ori += 90.0*i
            
            # Create movie stim by loading movie from list
            mov = visual.MovieStim3(win, videolist[i]) 
            mov.size *= .75  # Scale the image relative to initial size
            mov.pos = movie_pos_list[i]
            
            # Start the movie stim by preparing it to play
            mov.play()
            
            # If boolean to finish current movie AND movie has not finished yet
            while mov.status != visual.FINISHED:
                
                # Draw movie stim again
                mov.draw()
                img.draw()
                instr_text.draw()
                fin_text.draw()
        
                # Display updated stim on screen
                win.flip()
                if RECORD:
                    # Store an image of every upcoming screen refresh:
                    win.getMovieFrame(buffer='back')
                
                # Check keyboard for button presses
                keys = keyboard.getPresses()
                # Check joystick for button presses    
                if joystick.Start() or (' ' in keys):
                    mov.status = visual.FINISHED
                    vid_play = False
                    repeat_demo = False
                    break
            
            if vid_play==False:
                break
            
            ## Cue button press
            press_text.pos = img_pos_list[i]                
            press_text.contrast = 1  
        
            # Instruct user to press 'Start' and wait on button press
            while cmd_list[i]()==0:
            
                time.sleep(.05)
                
                # Oscillate text contrast while we wait
                if press_text.contrast:
                    press_text.contrast = 0
                else:
                    press_text.contrast = 1
                
                cue_img.draw()
                mov.draw()
                instr_text.draw()
                fin_text.draw()
                press_text.draw()    
                win.flip()
                if RECORD:
                    # Store an image of every upcoming screen refresh:
                    win.getMovieFrame(buffer='back')
                 
                if joystick.Start() or (' ' in keys):
                    vid_play = False
                    break
            
#            # Iterate image orientation (rotation)
#            img.ori += 90.0
#            cue_img.ori += 90.0
            
            ## If trial break variable is set, break trial
            if vid_play==False:
                break
                
            # Current Trial is Done
            # Pause for 1 sec (while checking for button presses)    
            t_start = time.time()+1
            while time.time()<t_start:
                # Check keyboard for button presses
                keys = keyboard.getPresses()
                # Check joystick for button presses    
                if joystick.Start() or (' ' in keys):
                        vid_play = False
                        break
                    
        # Prompt user for response (repeat y/n?)
        color_list = ['yellow','grey']
        sw = 0
        curr_time = time.time()
        delay = 1

        while vid_play:
            
            if time.time()-curr_time > delay:
                # Flip switch                        
                sw = 1-sw
                curr_time = time.time()
                
            wait_img = visual.ImageStim(win=win, image=wait_img_list[sw], units="pix")
#            wait_img.size *= .75  # Scale the image relative to initial size
            wait_img.pos = [0, -height/4]
            
            # Text to repeat or proceed
            loop_text_rep = visual.TextStim(win, text="Repeat training?",
                                   height=40,
                                   color=color_list[1-sw],
                                   alignHoriz='center',
                                   wrapWidth = width,
                                   pos = [-width/5, height/4])
    
            loop_text_proc = visual.TextStim(win, text="Proceed to mission",
                                   height=40,
                                   color=color_list[sw],
                                   alignHoriz='center',
                                   wrapWidth = width,
                                   pos = [width/5, height/4]) 
                                   
            loop_text_rep.draw()    
            loop_text_proc.draw()
            wait_img.draw()
            
            win.flip()
            if RECORD:
                # Store an image of every upcoming screen refresh:
                win.getMovieFrame(buffer='back')
                                   
            if joystick.Back():
                break
            elif joystick.Start():
                repeat_demo = False
                break
            
        train_rep += 1
        
        ## If trial break variable is set, break trial
        if vid_play==False:
            break
        
    ## End 
