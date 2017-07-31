#!/usr/bin/env python
"""
IDT: Individualized (Monetary) Discounting Task

Copyright (C) 2017 - 2017 Mikhail Koffarnus (mickyk@vtc.vt.edu)

Distributed under the terms of the GNU Lesser General Public License
(LGPL). See LICENSE.TXT that came with this file.
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
import pickle

NEW_BLOCK_TIME=5

if len(sys.argv)<2:
    sid = raw_input('Subject ID? ')
    #exp = raw_input('Experiment name? ')
    #delamount = int(raw_input('Delayed amount? '))
    #commodity = raw_input('Commodity with unit (e.g., "g of cocaine"). Just put $ for money: ')
else:
    sid = sys.argv[1]
    #exp = sys.argv[2]
    #delamount = int(sys.argv[3])
    #commodity = sys.argv[4]

exp = "OutOfScanner"
delamount = 1000
commodity = "$"

tr_len = 2

x1=range(1,5,1)
x2=[f/2.0 for f in x1]
isi_array=[choice(x2) for i in range(168)]

trs=168*tr_len+sum(isi_array)*2 # 168 questions
gn_sec_n=trs*tr_len # total time for presentation
gn_keystroke = 0

question=0
currenttask=0
delays=['1 day', '1 week', '1 month', '3 months', '1 year', '5 years', '25 years']
currentdelay=0
shuffle(delays)
sorteddelays=['1 day', '1 week', '1 month', '3 months', '1 year', '5 years', '25 years']
qIndex=1
screenText=['','']
ip=0
ii=0
iv=0
subQ=-1
krow=0
blocknum=0
# log file name
if not os.path.exists('data'):
    os.makedirs('data')    
if not os.path.exists('data\%s' % (sid)):
    os.makedirs('data\%s' % (sid))
log_filename = 'data\%s\AdjAmt_%s_%s_%i_%s_' % (sid, exp, sid, delamount, commodity) + time.strftime ('%m-%d-%Y_%Hh-%Mm.csv')
pickle_filename = 'data\%s\AdjAmt_%s_%s.p' % (sid, sid, exp)
shuffle(isi_array)
isi_array=[0]+isi_array # no delay before first question
isi = 0
isi_index=0
now=1
firsttime=0
response=0
stim_onset=0
fixon=0
newseton=0
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
logfile.write("Trial number,Stimulus onset,Response time,Immediate amount,Delay,Response [0I;1D],Now loc [0L;1R]\n")

# Viewport parameters
import ctypes
user32 = ctypes.windll.user32
if user32.GetSystemMetrics(0) < 1024:
    print " "
    print "Horizontal screen resolution needs to be at least 1024."
    raw_input("Press enter to exit")
    sys.exit()    
screen=VisionEgg.Core.Screen(size=(user32.GetSystemMetrics(0),user32.GetSystemMetrics(1)),fullscreen=True)
screen.parameters.bgcolor = (0.0,0.0,0.0,0.0)
d_screen_half_x = screen.size[0]/2
d_screen_half_y = screen.size[1]/2

# Vision Egg objects

title = Text(text='Please choose the amount and delay combination you prefer between',
        color=(1.0,1.0,1.0),
        position=(d_screen_half_x,d_screen_half_y+120),
        font_size=40,
        anchor='center')
		
title2 = Text(text='each pair of options. Press 5 to continue.',
        color=(1.0,1.0,1.0),
        position=(d_screen_half_x,d_screen_half_y+80),
        font_size=40,
        anchor='center')

newset = Text(text='New delay',
        color=(1.0,1.0,1.0),
        position=(d_screen_half_x,d_screen_half_y+120),
        font_size=60,
        anchor='center')

left_choice = Text(text=' ',
              color=(1.0,1.0,1.0),
              position=(d_screen_half_x/2,d_screen_half_y+fontsize),
              font_size=fontsize,
              anchor='center')

left_choice2 = Text(text=' ',
              color=(1.0,1.0,1.0),
              position=(d_screen_half_x/2,d_screen_half_y),
              font_size=fontsize,
              anchor='center')


right_choice = Text(text=' ',
              color=(1.0,1.0,1.0),
              position=(d_screen_half_x+(d_screen_half_x/2),d_screen_half_y+fontsize),
              font_size=fontsize,
              anchor='center')
              
right_choice2 = Text(text=' ',
              color=(1.0,1.0,1.0),
              position=(d_screen_half_x+(d_screen_half_x/2),d_screen_half_y),
              font_size=fontsize,
              anchor='center')

fixation = FixationCross(on = True, position=(d_screen_half_x, d_screen_half_y),size=(64,64))

taskend = Text(text='Task Complete',
          color=(1.0,1.0,1.0),
          position=(d_screen_half_x,d_screen_half_y+160),
          font_size=60,
          anchor='center')
        
viewportIntro = Viewport(screen=screen)
viewport = Viewport(screen=screen, stimuli=[title, title2, left_choice, right_choice, left_choice2, right_choice2, newset, taskend, fixation]) 

p = Presentation(
    go_duration = (2000,'seconds'), # run for longer than needed
    trigger_go_if_armed = 0, #wait for trigger
    viewports = [viewport,viewportIntro])

def getState(t):
    global qIndex, screenText, ip, question, gn_keystroke, subQ, amountRow, delay, krow, blocknum, amount, currentdelay, trialnum
    global isi, isi_index, now, firsttime, response, stim_onset, newseton, goodRow, taskendon, fixon

#    if (t > isi+isi_array[isi_index]*tr_len):
    if (t > isi+isi_array[isi_index]):
        newseton=0
        fixon=0
        taskendon=0
        if firsttime: 
            now = int(round(random()))
            stim_onset=t
            firsttime=0
        
        #### Ask 6 questions
        if question < 6:
            if commodity=='$':
                if delamount<1000:
                    screenText[now] = "$%3.2f" % (float(amount*delamount)) 
                    screenText[1-now] = "$%3.2f" % (delamount)
                else:
                    screenText[now] = "$%s" % (group(int(amount*delamount))) 
                    screenText[1-now] = "$%s" % (group(delamount))
            else:
                if amount*delamount < 1:
                    screenText[now] = "%1.2f %s" % (float(amount*delamount), commodity) 
                elif amount*delamount < 10:
                    screenText[now] = "%1.1f %s" % (float(amount*delamount), commodity) 
                else:
                    screenText[now] = "%s %s" % (group(round(amount*delamount,0)), commodity) 
                if delamount < 1:
                    screenText[1-now] = "%1.2f %s" % (float(delamount), commodity) 
                elif delamount < 10:
                    screenText[1-now] = "%1.1f %s" % (float(delamount), commodity) 
                else:
                    screenText[1-now] = "%s %s" % (group(round(delamount,0)), commodity)
            if now==0:
                left_choice2.parameters.text = "now"
                right_choice2.parameters.text = "in %s" % (delays[currentdelay])
            else:
                left_choice2.parameters.text = "in %s" % (delays[currentdelay])    
                right_choice2.parameters.text = "now"
            if gn_keystroke > 0:
                firsttime=1
                fixon = 1
                if (gn_keystroke == 1) & (now == 0):
                    response=0
                elif (gn_keystroke == 3) & (now == 1):
                    response=0
                else:
                    response=1
                isi=t
                isi_index=isi_index+1
                screenText[0] = ""
                screenText[1] = ""   
                left_choice2.parameters.text = " "
                right_choice2.parameters.text = " "       
                logfile.write("%i,%f,%f,%i,%s,%i,%i\n" % (trialnum, stim_onset, t, int(amount*delamount), delays[currentdelay], response, now))
                trialnum = trialnum+1
                if response==0:
                    amount=amount-(0.5**(question+2))
                else:                        
                    amount=amount+(0.5**(question+2))
                if question<5:
                    question=question+1
                else:
                    print amount
                    IPs[sorteddelays.index(delays[currentdelay])] = amount
                    print IPs
                    question=0
                    amount=0.5
                    gn_keystroke = 0
                    if currentdelay==6:
                        for i in range(7):
                            logfile.write("%s," % (sorteddelays[i]))
                        logfile.write("\n")
                        for i in range(7):
                            logfile.write("%f," % (IPs[i]))
                        logfile.write("\n")
                        JB1=0
                        for i in range(6):
                            if IPs[i+1]-IPs[i]>0.2: JB1+=1
                        JB2=0
                        if IPs[0]-IPs[6] < 0.1:
                            JB2=1
                        xx = [1,7,30.44,91.32,365.25,1826.25,9131.25]
                        JBpass = "Y"
                        if JB1 > 1: JBpass = "N"
                        if JB2 > 0: JBpass = "N"
                        logfile.write("JB Rule 1: %i\n" % (JB1))
                        logfile.write("JB Rule 2: %i\n" % (JB2))                        
                        xvalues = numpy.array(xx)
                        yvalues = numpy.array(IPs)
                        popt, pconv = curve_fit(func, xvalues, yvalues, p0 = 0.01)
                        left_choice2.parameters.text = "%s" % (JBpass)
                        right_choice2.parameters.text = "k value: %2.6f" % (float(popt))
                        logfile.write("k value: %f\n" % float(popt))
                        IPs.append(popt)
                        IPs.append(JB1)
                        IPs.append(JB2)
                        pickle.dump(IPs, open(pickle_filename, "wb"))
                        taskendon=1
                        fixon=0
                        isi=t+1000
                        #p.parameters.go_duration = (0, 'frames')
                    else:
                        currentdelay=currentdelay+1  
                        isi=t+NEW_BLOCK_TIME
                        newseton=1
                        fixon=0
                
    else:
        firsttime=1

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
taskend_controller = FunctionController(during_go_func=showTaskEnd, between_go_func=hideStim)

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
p.add_controller(taskend,'on',taskend_controller)
p.add_controller(p, 'trigger_go_if_armed', state_controller)

p.parameters.handle_event_callbacks = [(pygame.locals.KEYDOWN, keydown)]

p.go()
logfile.close()
