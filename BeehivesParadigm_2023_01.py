"""
Optimized version of the Beehives Paradigm

- The goal is to manipulated decision confidence to assess a causal link with sequential effects (repetition bias with previous high confidence, alternation bias with previous low confidence)
- by showing additional dots after response (post-decisional evidence).

- For example, if left evidence is shown, left is responded, then presenting weaker evidence (relevatively right) evidence compared to the earlier evidence
  should decrease confidence compared to when no additional dots are shown, or relatively more left evidence is presented
- We will manipulate the mean of the generative distribution of the post-decisional evidence, making the evidence "weaker" or "stronger"

- Post-decisional evidence also in practice rounds, but with the same generative mean as the pre-decisional evidence (if not in practice rounds this is a bit suspicious)
- Discrete confidence scale instead of continuous scale (circle), such that the scale is clear to everybody
- Responses and confidence ratings will be given by keyboard instead of mouse
- Calculate average evidence (x coordinates of all dots shown in a trial) for feedback on accuracy in between blocks
- Drop one-back counterbalancing: this doesn't work.
  The idea was to control that each instance A is preceeded an equal number of times by B, C, D...
  So we had 4 difficulty levels, 2 sides (left,right). These 8 combinations were one-back counterbalanced.
  But since the dots are drawn from a distribution is was possible that on a left trial mostly right evidence was drawn.
  Thus, the one-back counterbalancing was not correct anymore. 
- So now a more simple way of generating trial sequence:
  There are 4 difficulty levels, 2 sides (left, right), and 2 confidence manipulations (weaker, stronger) so 4x2x2 = 16 combinations
  Repeat these 16 combinations by a factor to get the number of trials in a block, and then shuffle.
"""


pilot = False # if True: number of trials each block = number of trials training block
conf_only = False # if True: only do blocks with confidence


from psychopy import visual, event, monitors, core, gui, data
import numpy as np
import random  
import statistics
from win32api import GetSystemMetrics
import os 
import os.path
from time import sleep


# GUI
if pilot:
    sub = 0;age = 30;gender = 'M';handedness = 'R'
    delay_instructions = 0
    
else:
    info        = {'sub': 0,'gender':['V','M','X'],'age': 0,'handedness':['R','L']}
    myDlg       = gui.DlgFromDict(dictionary = info, title = "Beehives task",show=True)
    sub = info['sub'];age = info['age'];gender = info['gender'];handedness = info['handedness'];
    file_name   = "Data\BeehivesTask_sub%d" %(sub) + ".csv" 
    if os.path.isfile(file_name):
        print('This subject number already exists!')
        core.quit()
    delay_instructions = 1.5 # prevents participant to skip instructions by accident



# Parameters
# Note: timing duration stimuli depends on refresh rate (should be 60 Hz -> this is checked later in script)

# For prediction confidence:
#   Three last blocks with confidence: 3 x 64 = 192 trials

shift       = [10,20,30,40,50,60]; np.random.shuffle(shift) # shift in generative mean for post-decisional evidence
width_add   = 30  # width of generative distribution post-decisional evidence
add_dots    = 5   # additional dots shown after a response is given ~ post-decisional evidence



nb_training_blocks      = 1                      
nb_training_trials      = 10        

nb_main_blocks          = 6 if conf_only else 7     
nb_main_trials_block    = 64                        # number of trials per block. Has to be a factor of 16!
                   
nb_total_blocks         = nb_training_blocks + nb_main_blocks
nb_conf_blocks          = 6                         # last blocks confidence will be asked

max_dots                = 50                        # response deadline is 100ms * max_dots 
dif_lvl                 = [1,6,18,80]               # distance mean generative model from center in pixels
width                   = 70                        # width sampling distribution dots

duration_fixationcross  = 45                        # expressed in number of frames so 750 ms (45*16.67) 
duration_beehives       = 45                        # 750 ms
duration_each_dot       = 6                         # 100 ms


if nb_main_trials_block%16 != 0:
    print("Number of trials per block is not dividable by 16!")
    core.quit()

# Definitions
def divide_chunks(l, n):
    # looping till length l
    for i in range(0, len(l), n): 
        yield l[i:i + n]



# Create a data folder if it doesn't exist yet 
my_directory  = os.getcwd()
if os.path.isdir('Data') == False:
    os.mkdir('Data')
  
  
  
# Window     
screen_width    = GetSystemMetrics(0) 
screen_height   = GetSystemMetrics(1)
winSize         = (screen_width,screen_height)
mon             = monitors.Monitor('testMonitor')

window          = visual.Window(size=winSize, winType='pyglet', fullscr = True, monitor = mon, units="pix", color="black")
refresh_rate    = visual.getMsPerFrame(myWin=window, nFrames = 60, showVisual=False, msg='', msDelay=0.0)



## Timing stimuli is based on 60 Hz --> 60 frames per second --> 16.67 ms per frame 
if round(refresh_rate[0],0) != 17: # check refresh rate is ~ 17 Hz
    print("Refresh rate not okay!")
    core.quit()



# Stimuli  

fcross              = visual.TextStim(window, text="+", height = 50, color='gray')
beehive_left        = visual.Circle(window, size = 18, pos = (-max(dif_lvl),0), fillColor = "yellow")  #fixed position (on max difficulty lvl)
beehive_right       = visual.Circle(window, size = 18, pos = (max(dif_lvl),0), fillColor = "yellow") 
bee                 = visual.Circle(window, size = 10, fillColor = "white")
good                = visual.TextStim(window, text="Correct!", height = 40, color='green')
bad                 = visual.TextStim(window, text="Incorrect...", height = 40, color='red')
end                 = visual.TextStim(window,text='The end! Thank you for your participation!  \n\n Please remain seated until everybody is finished.', pos=(0,0), height=30, wrapWidth=5000)
conf_text           = visual.TextStim(window,text='How confident are you that you made the correct choice?', pos = (0,300), height=30, wrapWidth=5000)



if sub%2 < 1: # counterbalance the order between participants
    conf_labels     = visual.TextStim(window,text='Definitely correct       Probably correct        Guess correct               Guess wrong         Probably error      Definitely wrong', height=30, wrapWidth=5000)
else:
    conf_labels     = visual.TextStim(window,text='Definitely wrong         Probably error      Guess wrong                Guess correct        Probably correct        Definitely correct', height=30, wrapWidth=5000)


choice_keys         = ['c','n'] # left, right
cj_keys             = ['1','2','3','8','9','0']



# Create trial sequence
trial_list  = []

target_side = ["left","right"]
post_evi    = ["stronger","weaker"]

for difficulty in dif_lvl: # 16 trial types
    for target in target_side:
        for postdecisionevi in post_evi:
                trial_info = {'difficulty': difficulty,'target': target, 'postDecisionEvi': postdecisionevi} # dictionary is used to read in stimulus information during experiment
                for rep in range(int(nb_main_trials_block/16)): # repeat some times to obtain number of trials in a block
                    trial_list.append(trial_info)  

main_trial_list = []

for block in range(nb_main_blocks): # shuffle order and add to list to obtain sequence over all blocks
    random.shuffle(trial_list)
    main_trial_list.append(trial_list)



# create list with trials for practice blocks
practice_trial_list = []

for i in range(nb_training_trials):
    practice_trial = {'difficulty': random.choice(dif_lvl[1:4]),'target': random.choice(['left','right']), 'postDecisionEvi' : random.choice(["stronger","weaker"])} # only the three easiest conditions
    practice_trial_list.append(practice_trial)



# create list for easier testing (with less trials in block)
testing_trials = [] 
for i in range(nb_training_trials*nb_main_blocks):
    testing_trials.append(random.choice(trial_list))

testing_trial_list = list(divide_chunks(testing_trials, nb_training_trials)) 




        
# TrialHandler: make a data file
file_name = "Data\DotsTask_sub%d" %(sub)
info           = {"sub": sub,"age": age, "gender": gender, "handedness": handedness}
thisExp = data.ExperimentHandler(dataFileName = file_name,extraInfo=info)


# Instruction images
imagepath = my_directory + '\Instructions\Slide'
image = []
for number_image in range(15):
    image_id = imagepath + str(number_image+1) + '.JPG' #import image 
    image.append(visual.ImageStim(window, image_id)) #convert as 'Image Stimulus'


# Initialization variables for feedback on performance in between blocks
prev_feedback_acc = []
prev_feedback_rt = []


##############
# Experiment #
##############

mouse = event.Mouse(visible = False) 
clock = core.Clock()

for image_number in range(7): # present instructions
    image[image_number].draw()
    window.flip()
    event.clearEvents('keyboard')
    sleep(delay_instructions) 
    event.waitKeys(keyList = ['space'])

for block in range(nb_total_blocks):
    if block == 0:
        running = "practice"
        which_trial_list = practice_trial_list
        
        
    if block == 1: # indicates end of practice trials and start of main experiment (see if statement below)
        for image_number in range(8,10): # present instructions
            image[image_number].draw()
            window.flip()
            event.clearEvents('keyboard')
            sleep(delay_instructions)
            event.waitKeys(keyList = ['space'])
        
    if block >= nb_training_blocks:
        if block == nb_total_blocks - nb_conf_blocks: # give confidence instructions
            if sub%2 < 1: # show different confidence instructions depending on order labels
                which_image = (11,12,14)
            else:
                which_image = (11,13,14)


            print("confidence blocks start")
            for image_number in which_image: # present instructions
                image[image_number].draw()
                window.flip()
                event.clearEvents('keyboard')
                sleep(delay_instructions)
                event.waitKeys(keyList = ['space'])
            
        running = "main"
        if pilot: # trials come from a shorter list (so experiment is over more quickly)
            which_trial_list = testing_trial_list[block-1]
        else:
            which_trial_list = main_trial_list[block-1] # already 1 practice block so block = 1 and argument [] has to start with 0
    
    ##################
    # Within a block #
    ##################
    
    feedback_acc    = []
    feedback_rt     = []

    
    trial_number = 0 
    
    for trial in which_trial_list: 
        
        ##################
        # Within a trial #
        ##################
        
        trial_number += 1
        
        for frameN in range(duration_fixationcross): # 750 ms (fixation cross)
            fcross.draw()
            window.flip()
        
        for frameN in range(duration_beehives): # 750 ms (beehives)
            fcross.draw()
            beehive_left.draw()
            beehive_right.draw()
            window.flip()
        
        
        location_dots = [] # to save coordinates of dots
        location_add_dots = [] # to save coordinates of post-decisional dots

        
        # Configuration generative distribution for bee positions
        # Dot locations are sampled from a bivariate normal distribution with a generative mean (which is varied to determine trial difficulty), a fixed variance and 0 covariance
        if trial['target'] == 'left':
            mean = [-trial['difficulty'],0]
            
        else:
            mean = [trial['difficulty'],0]
            
        cov = [[width**2, 0],[0, width**2]] # see Park (2016)
        
        
        resp = []
        event.clearEvents('keyboard') 
        clock.reset() 
        
        
        # Present dots until response is given
        for number in range(max_dots):
            
            # Sample bee location from bivariate normal distribution
            x,y     = np.random.multivariate_normal(mean,cov) 
            bee.pos = (x,y)
            location_dots.append((x,y)) # save dot location
                    
            # timing response relative last clock.reset()
            resp = event.getKeys(keyList = choice_keys, timeStamped = clock) #output eg: [['n', 2.22]] 
            

            # stop stimulus presentation when response is given (does not work if placed in for-loop below)
            # if checked after for-loop below then 1 additional dot is presented
            
            if len(resp) > 0:  # if response is given show post-decisional evidence 
            
                response_given = 1
                
                mean_dots = np.mean([x_dot[0] for x_dot in location_dots]) # extract x coordinate each dot and take mean
                mean_add_dots = mean_dots
                
                # in training blocks post-decisional evidence is drawn from distribution with mean the average x coordinates of previous dots
                # in the main experiment, we'll manipulate this mean by adding or substracting a constant
                # to increase the evidence strength (leading to higher confidence), or decrease (leading to lower confidence)
                
                if block <= 1: # training block and first experiment block (without confidence)
                    shft = 0
                else:
                    shft = shift[block - 2]

                
                if block >= nb_training_blocks:
                    if ((mean_add_dots > 0 and trial['postDecisionEvi'] == 'stronger') or (mean_add_dots <= 0 and trial['postDecisionEvi'] == 'weaker')):
                        mean_add_dots += shft 
                    else:
                        mean_add_dots -= shft

                for number in range(add_dots):
                    x,y     = np.random.multivariate_normal([mean_add_dots,0],[[width_add**2, 0],[0, width**2]])
                    bee.pos = (x,y)
                    location_add_dots.append((x,y))
                    
                    for frameN in range(duration_each_dot): # each dot 100 ms 
                        fcross.draw()
                        beehive_left.draw()
                        beehive_right.draw()
                        bee.draw()
                        window.flip()
                        
                mean_add_dots = np.mean([x_dot_add[0] for x_dot_add in location_add_dots]) # extract x coordinate each dot and take mean

                
                break # here we break out of the dot presentation loop
            
            else: # we need this variable to present an additional instruction ("be faster") after a timed-out trial
                response_given = 0
            

            # Present one dot
            for frameN in range(duration_each_dot): # each dot 100 ms 
                fcross.draw()
                beehive_left.draw()
                beehive_right.draw()
                bee.draw()
                window.flip()
                
                
        
        # Save some data and 
        distance           = mean[0]
        diff               = trial['difficulty']
        targ               = trial['target'] 
        shift_post_dots    = trial['postDecisionEvi']
        shift_value        = shft

        
                

        if response_given == 1:

            response    = resp[0][0]
            rt          = resp[0][1]
            
            #accuracy
            if ((mean_dots < 0 and resp[0][0] == choice_keys[0]) or (mean_dots >= 0 and resp[0][0] == choice_keys[1])):
                ACC = 1
            elif ((mean_dots < 0 and resp[0][0] == choice_keys[1]) or (mean_dots >= 0 and resp[0][0] == choice_keys[0])):
                ACC = 0
  

            # add to list to calculate average over block for performance feedback
            feedback_acc.append(ACC)
            feedback_rt.append(rt)
            
        # Show instruction 'try to be faster' if timed-out
        if response_given == 0:
                        
            response = 'timed-out'
            rt = -99
            ACC = -99
            RTconf = -99
            cj = -99
            image[10].draw()
            window.flip()
            event.clearEvents('keyboard')
            event.waitKeys(keyList = ['space'])
                      
              
        for frameN in range(30): # 500ms 
            window.flip()
             
        # Feedback is given in first practice block  
        if block == 0 and response_given == 1: 
            for frameN in range(60):
                if ACC == 1:
                    good.draw()
                    window.flip()
                else:
                    bad.draw()
                    window.flip()
            
            # no confidence is asked yet but otherwise problem with data saving
            RTconf      = -99
            cj          = -99
                            

            
        # Ask for CONFIDENCE about the choice the last X blocks
        if block >= nb_total_blocks - nb_conf_blocks and response_given == 1:
            conf_text.draw()
            conf_labels.draw()
            window.flip()
            clock.reset()
            event.clearEvents()
            conf_press = event.waitKeys(keyList = cj_keys)
            RTconf = clock.getTime()

            #Convert conf_press into numeric value from 1 (sure error) to 6
            for temp in range(0,6):
                if conf_press[0] == cj_keys[temp]:
                    cj = temp+1
                    
            #reverse order for half
            if sub%2 < 1:
                cj = 7-cj
                        
        else:
            conf_press = 'none'
            cj = -99
            RTconf = -99
        
        
        for frameN in range(15): # 250ms ITI
            window.flip()
            
            
        # Save data of current trial        
        thisExp.addData("block", block)
        thisExp.addData("trial", trial_number)
        thisExp.addData("running", running) #practice or main
        thisExp.addData("difficulty", diff) #absolute distance from the center
        thisExp.addData("distance", distance) #signed distance from the center
        thisExp.addData("target", targ)
        thisExp.addData("response", response)
        thisExp.addData("accuracy", ACC)
        thisExp.addData("rt", rt)
        thisExp.addData("cj", cj)
        thisExp.addData("RTconf", RTconf)
        thisExp.addData("pre_dots_location", location_dots) # coordinates each dots
        thisExp.addData("pre_dots_location_mean", mean_dots) # mean x coordinates all dots
        thisExp.addData("post_dots_location", location_add_dots)
        thisExp.addData("post_dots_location_mean", mean_add_dots)
        thisExp.addData("shift_post_dots", shift_post_dots)
        thisExp.addData("shift", shift_value)

        

        # Proceed to next trial
        thisExp.nextEntry()
        
        window.flip()
        if event.getKeys(keyList = ['escape']):
            window.close()
            core.quit()


    # End of block: pause and performance feedback
    if running == "main" and block < (nb_total_blocks-1): # pause should not be presented after last block
        
        # Calculate some performance stats
        mean_rt = round(statistics.mean(feedback_rt)*1000,0) # in ms
        
        percentage_acc = round(statistics.mean(feedback_acc) * 100,0)
        

        # Present break + performance stats
        break1 = visual.TextStim(window,text='Break :)  \n\n Blocks remaining: ' + str(nb_total_blocks - (block+1)) + '\n\n\n\n Press SPACE to see performance summary', pos=(0,0),height=30, wrapWidth=5000)

        if block == 1: # in first block after practice no prev performance stats available 
            break2 = visual.TextStim(window,text='Average response time: ' + str(mean_rt) + ' ms \n\n Average accuracy: ' + str(percentage_acc) + '% \n\n\n\n\n Try to improve these scores by responding faster and more accurately! \n\n\n\n\n\n\n Press SPACE to continue the experiment.', pos=(0,0),height=25, wrapWidth=5000)
        else: # first performance stats and those of previous round
            break2 = visual.TextStim(window,text='Average response time: ' + str(mean_rt) + ' ms   (previous block: ' + str(prev_feedback_rt) + ' ms)\n\n Average accuracy: ' + str(percentage_acc) + '%   (previous block: ' + str(prev_feedback_acc) + '%) \n\n\n\n\n Try to improve these scores by responding faster and more accurately! \n\n\n\n\n\n\n Press SPACE to continue the experiment.', pos=(0,0),height=25, wrapWidth=5000)
        
        break1.draw()
        window.flip()
        event.waitKeys(keyList = 'space')
        
        break2.draw()
        window.flip()
        event.waitKeys(keyList = 'space')
        
        # Save stats to present after next block as 'your feedback in the previous block'
        prev_feedback_acc = percentage_acc
        prev_feedback_rt = mean_rt
        
        
end.draw()
window.flip()

# Data will be written when Python is closed
event.waitKeys(keyList = 'space')
window.close()
                
                
                
                
        
        
        
