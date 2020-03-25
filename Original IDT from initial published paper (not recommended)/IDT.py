#!/usr/bin/env python

"""
IDT: Individualized Discounting Task


Copyright 2017  Mikhail Koffarnus. 

Licensed under the Educational Community License, Version 2.0 (the "License");
you may not use this file except in compliance with the License. You may
obtain a copy of the License at: http://www.osedu.org/licenses/ECL-2.0

Unless required by applicable law or agreed to in writing,
software distributed under the License is distributed on an "AS IS"
BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express
or implied. See the License for the specific language governing
permissions and limitations under the License.
"""

import csv
import pygame
#import random
from random import choice, shuffle, random
import VisionEgg
VisionEgg.start_default_logging(); VisionEgg.watch_exceptions()
from VisionEgg.Core import *
from VisionEgg.FlowControl import Presentation, Controller, FunctionController
from VisionEgg.MoreStimuli import *
from VisionEgg.Textures import *
import pygame
import OpenGL.GL as gl
from VisionEgg.DaqKeyboard import *
from VisionEgg.Text import *
from VisionEgg.Textures import *
import Image, ImageDraw # Python Imaging Library (PIL)
import sys
import numpy
from scipy.optimize import curve_fit
#import pickle
import os

NEW_BLOCK_TIME=10

print " "

if len(sys.argv)<3:
    sid = raw_input('Subject ID? ')
    #fast = raw_input('Fast procedure? [y/n] ')
    fast="y"
    #exp = raw_input('Experiment name? ')
    #delamount = int(raw_input('Delayed amount? '))
    #commodity = raw_input('Commodity with unit (e.g., "g of cocaine"). Just put $ for money: ')
else:
    sid = sys.argv[1]
    fast = sys.argv[2]
    #exp = sys.argv[2]
    #delamount = int(sys.argv[3])
    #commodity = sys.argv[4]

exp = "IDT"
delamount = 1000
commodity = "USD"

tr_len = 2

if (fast=="y") or (fast=="Y"):
    fast="y"
    x1=range(2,21,1)
    x2=[f/2.0 for f in x1]
elif fast=="superfast":
    x2=[0,0]
    fast="y"
    NEW_BLOCK_TIME=1
else:
    x2=[1,1.25,1.5,1.75,2,2.25,2.75,3.4,4.1,5,7,9,11]
isi_array=[choice(x2) for i in range(168)]
shuffle(isi_array)
isi = NEW_BLOCK_TIME+0
isi_index=0

# log file name
if not os.path.exists('data'):
    os.makedirs('data')    
if not os.path.exists(os.path.join('data', sid)):
    os.makedirs(os.path.join('data', sid))

filename='DiscScan_%s_%s_%d_%s_%s' % (str(sid), str(exp), int(delamount), str(commodity), time.strftime('%m-%d-%Y_%Hh-%Mm.csv'))
log_filename = os.path.join('data', sid, filename)

filename='AdjAmt_%s_OutOfScanner.p' % (sid)
pickle_filename = os.path.join('data', sid, filename)

if os.path.isfile(pickle_filename):
    S1data = pickle.load(open(pickle_filename, "rb"))
else:
    print " "
    print "No session 1 file found"
    raw_input("Press enter to exit")
    sys.exit(1)
    
if S1data[7] > 0.03542:
    delays=['1 day', '1 week', '1 month', '3 months']
    sorteddelays=['1 day', '1 week', '1 month', '3 months']
    IPindex = 0
elif S1data[7] > 0.0098:
    delays=['1 week', '1 month', '3 months', '1 year']
    sorteddelays=['1 week', '1 month', '3 months', '1 year']
    IPindex = 1
elif S1data[7] > 0.002813:
    delays=['1 month', '3 months', '1 year', '5 years']
    sorteddelays=['1 month', '3 months', '1 year', '5 years']
    IPindex = 2
else:
    delays=['3 months', '1 year', '5 years', '25 years']
    sorteddelays=['3 months', '1 year', '5 years', '25 years']
    IPindex = 3

nothing=0
gn_keystroke = 0
question=0
currentdelay=0
otherdelay=0
shuffle(delays)
qIndex=1
screenText=['XXXXXXX','XXXXXXX']
ip=0
ii=0
iv=0
subQ=-1
krow=0
blocknum=0
now=1
firsttime=0
response=0
stim_onset=0
fixon=0
newseton=1
taskendon=0
trialnum=0
goodrow = []
IPs = [0.0]*7
amount=0.5
fontsize = 60
if len(commodity)>15: fontsize=40
if len(commodity)>25: fontsize=30

# Read/write data files
logfile=open(log_filename,'w')
# log session info and column headers
logfile.write("Subject ID,%s\n" % (sid))
logfile.write("Experiment,%s\n" % (exp))
logfile.write("Delayed amount,%i\n" % (delamount))
logfile.write("Commodity,%s\n" % (commodity))
logfile.write("Trial number,Stimulus onset,Response time,Immediate amount,Left delay,Right delay,Response [-1O;0I;1D],Now loc [0L;1R]\n")

# Viewport parameters
import ctypes
user32 = ctypes.windll.user32
if user32.GetSystemMetrics(0) < 1024:
    print " "
    print "Horizontal screen resolution needs to be at least 1024."
    raw_input("Press enter to exit")
    sys.exit(1)    

screen=VisionEgg.Core.Screen(size=(user32.GetSystemMetrics(0),user32.GetSystemMetrics(1)),fullscreen=True)
#screen=VisionEgg.Core.Screen(size=(1024,768),fullscreen=False)
screen.parameters.bgcolor = (0.0,0.0,0.0,0.0)
d_screen_half_x = screen.size[0]/2
d_screen_half_y = screen.size[1]/2

# Vision Egg objects

title = Text(text='Please choose the option you prefer in each case',
        color=(1.0,1.0,1.0),
        position=(d_screen_half_x,d_screen_half_y+160),
        font_size=fontsize,
        anchor='center')
        
title2 = Text(text='C',
        color=(1.0,1.0,1.0),
        position=(d_screen_half_x,d_screen_half_y-160),
        font_size=30,
        anchor='center')

newset = Text(text='Next delay: %s' % (delays[currentdelay]),
        color=(1.0,1.0,1.0),
        position=(d_screen_half_x,d_screen_half_y+160),
        font_size=fontsize,
        anchor='center')

left_choice = Text(text='XXXXXXX',
              color=(1.0,1.0,1.0),
              position=(d_screen_half_x*0.6,d_screen_half_y+fontsize),
              font_size=fontsize,
              anchor='center')

left_choice2 = Text(text='XXXXXXX',
              color=(1.0,1.0,1.0),
              position=(d_screen_half_x*0.6,d_screen_half_y),
              font_size=fontsize,
              anchor='center')


right_choice = Text(text='XXXXXXX',
              color=(1.0,1.0,1.0),
              position=(d_screen_half_x*1.4,d_screen_half_y+fontsize),
              font_size=fontsize,
              anchor='center')
              
right_choice2 = Text(text='XXXXXXX',
              color=(1.0,1.0,1.0),
              position=(d_screen_half_x*1.4,d_screen_half_y),
              font_size=fontsize,
              anchor='center')

fixation = FixationCross(on = False, position=(d_screen_half_x, d_screen_half_y),size=(64,64))

taskend = Text(text='or',
          color=(1.0,1.0,1.0),
          position=(d_screen_half_x,d_screen_half_y+(fontsize/2)),
          font_size=fontsize,
          anchor='center')
        
viewportIntro = Viewport(screen=screen)
viewport = Viewport(screen=screen, stimuli=[title, title2, left_choice, right_choice, left_choice2, right_choice2, newset, taskend, fixation]) 

p = Presentation(
    go_duration = (2000,'seconds'), # run for longer than needed
    trigger_go_if_armed = 0, #wait for trigger
    viewports = [viewport,viewportIntro])

def getState(t):
    global qIndex, screenText, ip, question, gn_keystroke, subQ, amountRow, delay, krow, blocknum, amount, currentdelay, trialnum
    global isi, isi_index, now, firsttime, response, stim_onset, newseton, goodRow, taskendon, fixon, indiff, amounts, amountlist, noncontrolamounts

    if (t > isi):
        #newseton=0
        #fixon=0
        taskendon=1
        if firsttime: 
            now = int(round(random()))
            stim_onset=t
            newset.parameters.text = "Which would you rather have?"
            firsttime=0
            if question == 0:
                indiff = S1data[IPindex + sorteddelays.index(delays[currentdelay])]
                amounts = [1.0, 0.95, 0.85, 0.75, 0.65, 0.55, 0.45, 0.35, 0.25, 0.15, 0.05, 0.0]
                noncontrolamounts = [0.95, 0.85, 0.75, 0.65, 0.55, 0.45, 0.35, 0.25, 0.15, 0.05]
                amounts.append(indiff)
                amounts.append(indiff + 0.04)
                amounts.append(indiff + 0.08)
                amounts.append(indiff - 0.04)
                amounts.append(indiff - 0.08)
                for i in range(17):
                    if amounts[i] > 1: amounts[i] -= 0.1
                    if amounts[i] < 0: amounts[i] += 0.1
                amounts.append("now")
                amounts.append("now")
                amounts.append("now")
                if currentdelay==0: 
                    amounts.append("notnow1")
                    amounts.append("notnow2")
                    amounts.append("notnow3")
                    amounts.append("notnow1")
                    amounts.append("notnow3")
                if currentdelay==1: 
                    amounts.append("notnow0")
                    amounts.append("notnow2")
                    amounts.append("notnow3")
                    amounts.append("notnow2")
                if currentdelay==2: 
                    amounts.append("notnow0")
                    amounts.append("notnow1")
                    amounts.append("notnow3")
                    amounts.append("notnow0")
                if currentdelay==3: 
                    amounts.append("notnow0")
                    amounts.append("notnow1")
                    amounts.append("notnow2")
                    amounts.append("notnow1")
                    amounts.append("notnow2")
                shuffle(amounts)
            if amounts[question] == "now":
                left_choice2.parameters.text = "now"
                right_choice2.parameters.text = "now"
                amounts[question]=choice(noncontrolamounts)
            elif "notnow" in str(amounts[question]):
                otherdelay=int(amounts[question][6])
                amounts[question]=choice(noncontrolamounts)
                if ((now==0) and (sorteddelays.index(delays[otherdelay])<sorteddelays.index(delays[currentdelay]))) or ((now==1) and (sorteddelays.index(delays[otherdelay])>sorteddelays.index(delays[currentdelay]))):
                    left_choice2.parameters.text = "in %s" % (delays[otherdelay])
                    right_choice2.parameters.text = "in %s" % (delays[currentdelay])
                else:
                    left_choice2.parameters.text = "in %s" % (delays[currentdelay])    
                    right_choice2.parameters.text = "in %s" % (delays[otherdelay])
            else:
                if now==0:
                    left_choice2.parameters.text = "now"
                    right_choice2.parameters.text = "in %s" % (delays[currentdelay])
                else:
                    left_choice2.parameters.text = "in %s" % (delays[currentdelay])    
                    right_choice2.parameters.text = "now"
        if question < 50:
            if commodity=='$':
                if delamount<1000:
                    screenText[now] = "$%3.2f" % (float(amounts[question]*delamount)) 
                    screenText[1-now] = "$%3.2f" % (delamount)
                else:
                    screenText[now] = "$%s" % (group(int(amounts[question]*delamount))) 
                    screenText[1-now] = "$%s" % (group(delamount))
            else:
                if amounts[question]*delamount < 1:
                    screenText[now] = "%1.2f %s" % (float(amounts[question]*delamount), commodity) 
                elif amounts[question]*delamount < 10:
                    screenText[now] = "%1.1f %s" % (float(amounts[question]*delamount), commodity) 
                else:
                    screenText[now] = "%s %s" % (group(round(amounts[question]*delamount,0)), commodity) 
                if delamount < 1:
                    screenText[1-now] = "%1.2f %s" % (float(delamount), commodity) 
                elif delamount < 10:
                    screenText[1-now] = "%1.1f %s" % (float(delamount), commodity) 
                else:
                    screenText[1-now] = "%s %s" % (group(round(delamount,0)), commodity)
            if (gn_keystroke > 0) or ((fast!="y") and (t-stim_onset>6)):
                firsttime=1
                #fixon = 1
                if (gn_keystroke == 1) & (now == 0):
                    response=0
                elif (gn_keystroke == 3) & (now == 1):
                    response=0
                else:
                    response=1
                if (fast!="y") and (t-stim_onset>6): 
                    response=-1
                isi_index=isi_index+1
                if fast=="y":
                    isi=t+isi_array[isi_index]
                else:
                    isi=t+isi_array[isi_index]+6-(t-stim_onset)
                if (left_choice2.parameters.text == "now") and (right_choice2.parameters.text == "now"):
                    thisdelay = "now"
                else:
                    thisdelay = delays[currentdelay] 
                logfile.write("%i,%f,%f,%i,%s,%s,%i,%i\n" % (trialnum, stim_onset, t, int(amounts[question]*delamount), left_choice2.parameters.text, right_choice2.parameters.text, response, now))
                screenText[0] = "XXXXXXX"
                screenText[1] = "XXXXXXX"   
                left_choice2.parameters.text = "XXXXXXX"
                right_choice2.parameters.text = "XXXXXXX"      
                trialnum = trialnum+1
                if question<len(amounts)-1:
                    question=question+1
                else:
                    gn_keystroke = 0
                    if currentdelay==3:
                        question=99
                        firsttime=0
                    else:
                        question=0
                        currentdelay=currentdelay+1  
                        isi=t+NEW_BLOCK_TIME
                        newset.parameters.text = 'Next delay: %s' % (delays[currentdelay])
                        newseton=1
                        #taskendon=0
                        fixon=0
        else:     
            newset.parameters.text = 'Task Complete'
            taskend.parameters.text = " "
            screenText[0] = " "
            screenText[1] = " "   
            left_choice2.parameters.text = " "
            right_choice2.parameters.text = " "      
            newseton=1
            fixon=0
            isi=t+1000
            #p.parameters.go_duration = (0, 'frames')  
    else:
        if question < 50: firsttime=1

    gn_keystroke = 0
    return 1 

def replaceLeftText(t):
    global screenText
    return screenText[0]

def replaceRightText(t):
    global screenText
    return screenText[1]

def controlFix(t):
    global fixon
    if fixon:
        return 1
    else:
        return 0

def showNewSet(t):
    global newseton
    if newseton == 1:
        return 1
    else:
        return 0

def showTaskEnd(t):
    global taskendon
    if taskendon == 1:
        return 1
    else:
        return 0

def hideStim():  # only used before p starts
    return 0

def keydown(event):
        global gn_keystroke
        if event.key == pygame.locals.K_1:
                                        gn_keystroke = 1
        if event.key == pygame.locals.K_6:
                                        gn_keystroke = 3
        if event.key == pygame.locals.K_ESCAPE:
                                        p.parameters.go_duration = (0, 'frames')
                                        # Quit presentation 'p' with esc press

def group(number):
    s = '%d' % number
    groups = []
    while s and s[-1].isdigit():
        groups.append(s[-3:])
        s = s[:-3]
    return s + ','.join(reversed(groups))

def func(xvalues, k):
    return 1/(1+(xvalues*k))

### CONTROLLERS

trigger_in_controller = KeyboardTriggerInController(pygame.locals.K_5)
stimulus_on_controller = ConstantController(during_go_value=1,between_go_value=0)
stimulus_off_controller = ConstantController(during_go_value=0,between_go_value=1)
left_choice_controller = FunctionController(during_go_func=replaceLeftText)
right_choice_controller = FunctionController(during_go_func=replaceRightText)
state_controller = FunctionController(during_go_func=getState)
fixation_controller = FunctionController(during_go_func=controlFix, between_go_func=hideStim)
newset_controller = FunctionController(during_go_func=showNewSet, between_go_func=hideStim)
taskend_controller = FunctionController(during_go_func=showTaskEnd)

p.add_controller(p,'trigger_go_if_armed',trigger_in_controller)
p.add_controller(title,'on', stimulus_off_controller)
p.add_controller(title2,'on', stimulus_off_controller)
p.add_controller(left_choice,'on',stimulus_on_controller)
p.add_controller(right_choice,'on',stimulus_on_controller)
p.add_controller(left_choice2,'on',stimulus_on_controller)
p.add_controller(right_choice2,'on',stimulus_on_controller)
p.add_controller(left_choice,'text',left_choice_controller)
p.add_controller(right_choice,'text',right_choice_controller)
p.add_controller(fixation,'on',fixation_controller)
p.add_controller(newset,'on',newset_controller)
p.add_controller(taskend,'on',stimulus_on_controller)
p.add_controller(p, 'trigger_go_if_armed', state_controller)

p.parameters.handle_event_callbacks = [(pygame.locals.KEYDOWN, keydown)]

p.go()
logfile.close()
