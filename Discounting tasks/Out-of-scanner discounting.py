#!/usr/bin/env python

##
## Micky Koffarnus made this (March 2014)
##

import csv
import pygame
#import random
from random import choice, shuffle, random
from math import log
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
import os
import shutil
import win32com.client
objShell = win32com.client.Dispatch("WScript.Shell")
import psycopg2
import StringIO

NEW_BLOCK_TIME=5

print " "
print sys.argv[0]
print os.path.dirname(sys.argv[0])

if len(sys.argv)<8:
    print ' '
    sid = raw_input('Subject ID: ')
    exp = raw_input('Session: ')
    probability = int(raw_input('Delay [0] or probabilistic [1] discounting: '))    
    losses = int(raw_input('Gains [0] or losses [1]: '))
    if probability==0:
        past = int(raw_input('Future [0] or past [1] events: '))
    else:
        past = 0
    explicit0 = int(raw_input('Implicit [0] or explicit [1] zero: '))
    crosscommodity = raw_input('Cross-commodity discounting [y/n]? ')
    if crosscommodity == 'Y': crosscommodity = 'y'
    if crosscommodity == 'N': crosscommodity = 'n'    
    if crosscommodity == 'y': 
        commodityD = raw_input('Delayed or probabilistic commodity with unit (e.g., "g of cocaine"). \n     Just put $ for money: ')
        commodityI = raw_input('Immediate or certain commodity with unit (e.g., "g of cocaine"). \n     Just put $ for money: ')
        amountD = float(raw_input('Delayed or probabilistic amount: '))
        amountI = float(raw_input('Equivalence value for immediate/certain commodity: '))
    else:
        commodityD = raw_input('Commodity with unit (e.g., "g of cocaine"). \n     Just put $ for money: ')
        commodityI = commodityD
        amountD = float(raw_input('Delayed or probabilistic amount: '))
        amountI = amountD
    taskpause = raw_input('Stop at the end on the Task Complete screen [y/n]? ')
    customdelays = raw_input('Custom delays or probabilities [y/n]? ')
    if customdelays == 'Y': customdelays = 'y'
    if customdelays == 'N': customdelays = 'n'
    if probability==1:
        xx = []
        if customdelays == 'y':
            delays = eval(raw_input("Enter a series of probabilities (as percentages, but no '%') as you'd like them displayed, \n     surrounded by square brackets and separated by commas. \n     Like this: [90, 75, 33]: "))
        else:
            delays=[95, 90, 75, 50, 33, 10, 5]
    else:
        if customdelays == 'y':
            delays = eval(raw_input("Enter a series of delays in single quotes as you'd like them displayed, \n     surrounded by square brackets and separated by commas. \n     Like this: ['1 day', '1 week', '1 month']: "))
            xx = eval(raw_input("Enter the associated numerical in delays associated with those delays, \n     surrounded by square brackets and separated by commas. \n     Like this: [1, 7, 30.44]: "))
        else:
            delays=['1 day', '1 week', '1 month', '3 months', '1 year', '5 years', '25 years']
            xx = [1,7,30.44,91.32,365.25,1826.25,9131.25]
    directory = os.path.dirname(sys.argv[0])
else:
    sid = sys.argv[1]
    exp = sys.argv[2]
    probability = int(sys.argv[3])
    losses = int(sys.argv[4])
    past = int(sys.argv[5])
    explicit0 = int(sys.argv[6])
    commodityD = sys.argv[7]
    commodityI = sys.argv[8]
    amountD = float(sys.argv[9])
    amountI = float(sys.argv[10])
    directory = sys.argv[11]
    taskpause = sys.argv[12]
    customdelays = sys.argv[13]
    if customdelays == 'Y': customdelays = 'y'
    if customdelays == 'N': customdelays = 'n'
    if customdelays == 'y':
        delays = eval(sys.argv[14])
        if probability==1:
            xx=[]
        else: 
            xx = eval(sys.argv[15])
    else:
        delays=['1 day', '1 week', '1 month', '3 months', '1 year', '5 years', '25 years']
        if probability==0: xx = [1,7,30.44,91.32,365.25,1826.25,9131.25]
        
if taskpause == 'Y': taskpause = 'y'
if taskpause == 'N': taskpause = 'n'

tr_len = 2

x1=range(1,5,1)
x2=[f/2.0 for f in x1]
isi_array=[choice(x2) for i in range(1168)]

trs=1168*tr_len+sum(isi_array)*2 # up to 1168 questions
gn_sec_n=trs*tr_len # total time for presentation
gn_keystroke = 0
question=0
currenttask=0
sorteddelays=[]
for i,arr in enumerate(delays):
    sorteddelays.append(arr)
    if probability==1: xx.append(arr/(1-arr))
currentdelay=0
shuffle(delays)
numdelays=len(delays)
qIndex=1
screenText=['','']
screenText2=['','']
ip=0
ii=0
iv=0
subQ=-1
krow=0
blocknum=0
# log file name
if not os.path.exists(('%s\\data') % (directory)):
    os.makedirs(('%s\\data') % (directory))    
if not os.path.exists('%s\\data\\%s' % (directory, sid)):
    os.makedirs('%s\\data\\%s' % (directory, sid))
if not os.path.exists('%s\\EverythingDiscountingBackup' % (objShell.SpecialFolders("AppData"))):
    os.makedirs('%s\\EverythingDiscountingBackup' % (objShell.SpecialFolders("AppData")))
if not os.path.exists('%s\\EverythingDiscountingBackup\\%s' % (objShell.SpecialFolders("AppData"), sid)):
    os.makedirs('%s\\EverythingDiscountingBackup\\%s' % (objShell.SpecialFolders("AppData"), sid))
log_filename = '%s\\data\\%s\\AdjAmt_%s_%s_' % (directory, sid, sid, exp) + time.strftime ('%m-%d-%Y_%Hh-%Mm.csv')
backup_filename = '%s\\EverythingDiscountingBackup\\%s\\AdjAmt_%s_%s_' % (objShell.SpecialFolders("AppData"), sid, sid, exp) + time.strftime ('%m-%d-%Y_%Hh-%Mm.csv')
pickle_filename = '%s\\data\\%s\\AdjAmt_%s_%s.p' % (directory, sid, sid, exp)

shuffle(isi_array)
isi_array=[NEW_BLOCK_TIME]+isi_array 
isi = 0
isi_index=0
now=1
firsttime=0
response=0
stim_onset=0
fixon=0
newseton=1
taskendon=0
trialnum=0
goodrow = []
IPs = [0.0]*numdelays
amount=0.5
fontsize = 60
if len(commodityD)>15: fontsize=40
if len(commodityI)>15: fontsize=40
if len(commodityD)>25: fontsize=30
if len(commodityI)>25: fontsize=30
amtText=['','']
amtText0I=''
amtText0D=''

# Read/write data files
logfile=open(backup_filename,'w')
if probability==1:
    logfile.write("Date,Time,CommodityProb,CommodityCert,Amount,EquivAmt,Task type,Amount sign,Time sign,Zero\n")
else:
    logfile.write("Date,Time,CommodityDel,CommodityImm,Amount,EquivAmt,Task type,Amount sign,Time sign,Zero\n")
logfile.write(time.strftime ('%m-%d-%Y,%H:%M:%S') + ",%s,%s,%3.2f,%3.2f" % (commodityD, commodityI, amountD, amountI))
if probability==1: 
    logfile.write(",Probability disc")
else:
    logfile.write(",Delay disc")
if losses==1: 
    logfile.write(",Losses")
else:
    logfile.write(",Gains")
if past==1: 
    logfile.write(",Past")
elif probability==1:
    logfile.write(",Present")
else:
    logfile.write(",Future")
if explicit0==1: 
    logfile.write(",Explicit\n\n")
else:
    logfile.write(",Implicit\n\n")
if probability==1:
    logfile.write("Trial,Stim onset,Response time,Cert. Amount,Probability,Response [0P;1C],Imm Loc [0L;1R]\n")
else:
    logfile.write("Trial,Stim onset,Response time,Imm. Amount,Delay,Response [0D;1I],Imm Loc [0L;1R]\n")
    
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

newset = Text(text="Next delay: %s" % (delays[currentdelay]),
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

taskend = Text(text=' ',
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
    global qIndex, screenText, screenText2, ip, question, gn_keystroke, subQ, amountRow, delay, krow, blocknum, amount, amountD, amountI, currentdelay, trialnum
    global isi, isi_index, now, firsttime, response, stim_onset, newseton, goodRow, taskendon, fixon, customdelays, amtText, amtText0I, amtText0D, taskpause

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
            delay = delays[currentdelay]
            if commodityI=='$':
                amtText0I = "$0"
                if amountI<1000:
                    amtText[now] = "$%3.2f" % (float(amountI*amount))
                else:
                    amtText[now] = "$%s" % (group(int(amountI*amount))) 
            else:
                amtText0I = "0 %s" % (commodityI)
                if amountI<1:
                    amtText[now] = "%1.2f %s" % (float(amountI*amount), commodityI) 
                elif amountI<10:
                    amtText[now] = "%1.1f %s" % (float(amountI*amount), commodityI) 
                else:
                    amtText[now] = "%s %s" % (group(int(amountI*amount)), commodityI) 
            if commodityD=='$':
                amtText0D = "$0"
                if amountD<1000:
                    amtText[1-now] = "$%3.2f" % (amountD)
                else:
                    amtText[1-now] = "$%s" % (group(int(amountD)))
            else:
                amtText0D = "0 %s" % (commodityD)
                if amountD<1:
                    amtText[1-now] = "%1.2f %s" % (float(amountD), commodityD) 
                elif amountD<10:
                    amtText[1-now] = "%1.1f %s" % (float(amountD), commodityD) 
                else:
                    amtText[1-now] = "%s %s" % (group(int(amountD)), commodityD)
            if explicit0==0:
                screenText[now] = "%s" % (amtText[now])
                screenText[1-now] = "%s" % (amtText[1-now])
                if probability==1:
                    screenText2[now] = "for sure"
                    screenText2[1-now] = "with a %s%% chance" % (delay)
                elif past==1:
                    screenText2[now] = "1 hour ago"
                    screenText2[1-now] = "%s ago" % (delay)
                else:
                    screenText2[now] = "now"
                    screenText2[1-now] = "in %s" % (delay)
            else:
                if probability==1:
                    screenText[now] = "%s for sure and" % (amtText[now])
                    screenText2[now] = "%s with a %s%% chance" % (amtText0I, delay)
                    screenText[1-now] = "%s for sure and" % (amtText0D)
                    screenText2[1-now] = "%s with a %s%% chance" % (amtText[1-now], delay)
                elif past==1:
                    screenText[now] = "%s 1 hour ago and" % (amtText[now])
                    screenText2[now] = "%s %s ago" % (amtText0I, delay)
                    screenText[1-now] = "%s 1 hour ago and" % (amtText0D)
                    screenText2[1-now] = "%s %s ago" % (amtText[1-now], delay)
                else:
                    screenText[now] = "%s now and" % (amtText[now])
                    screenText2[now] = "%s in %s" % (amtText0I, delay)
                    screenText[1-now] = "%s now and" % (amtText0D)
                    screenText2[1-now] = "%s in %s" % (amtText[1-now], delay)
            if losses==1:
                screenText[now] = "lose " + screenText[now]
                screenText[1-now] = "lose " + screenText[1-now]
                if explicit0==1:
                    screenText2[now] = "lose " + screenText2[now]
                    screenText2[1-now] = "lose " + screenText2[1-now]
            else:
                screenText[now] = "gain " + screenText[now]
                screenText[1-now] = "gain " + screenText[1-now]
                if explicit0==1:
                    screenText2[now] = "gain " + screenText2[now]
                    screenText2[1-now] = "gain " + screenText2[1-now]
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
                screenText2[0] = ""
                screenText2[1] = ""
                logfile.write("%i,%f,%f,%f,%s,%i,%i\n" % (trialnum, stim_onset, t, amountI*amount, delays[currentdelay], response, now))
                trialnum = trialnum+1
                if response==losses:
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
                    if currentdelay==numdelays-1:
                        for i in range(numdelays):
                            logfile.write("%s," % (sorteddelays[i]))
                        logfile.write("\n")
                        for i in range(numdelays):
                            logfile.write("%f," % (IPs[i]))
                        logfile.write("\n")
                        JB1=0
                        for i in range(numdelays-1):
                            if IPs[i+1]-IPs[i]>0.2: JB1+=1
                        JB2=0
                        if IPs[0]-IPs[numdelays-1] < 0.1:
                            JB2=1
                        JBpass = "Yes"
                        if JB1 > 1: JBpass = "No"
                        if JB2 > 0: JBpass = "No"
                        logfile.write("JB Rule 1, %i\n" % (JB1))
                        logfile.write("JB Rule 2, %i\n" % (JB2))                        
                        xvalues = numpy.array(xx)
                        yvalues = numpy.array(IPs)
                        popt, pconv = curve_fit(func, xvalues, yvalues, p0 = 0.01)
                        screenText2[0] = "Consistency: %s" % (JBpass)
                        screenText[1] = "k value: %2.4f" % (float(popt))
                        screenText2[1] = "ln(k) value: %2.4f" % (float(log(popt)))
                        logfile.write("k value, %f\n" % float(popt))
                        logfile.write("ln(k) value, %f\n" % float(log(popt)))
                        IPs.append(popt)
                        IPs.append(JB1)
                        IPs.append(JB2)
                        pickle.dump(IPs, open(pickle_filename, "wb"))
                        taskendon=1
                        taskend.parameters.text = "Task Complete"
                        fixon=0
                        isi=t+1000
                        if taskpause=="n": p.parameters.go_duration = (0, 'frames')
                    else:
                        currentdelay=currentdelay+1  
                        isi=t+NEW_BLOCK_TIME
                        newseton=1
                        if probability==1:
                            newset.parameters.text = "Next probability: %s%%" % (delays[currentdelay])
                        else:
                            newset.parameters.text = "Next delay: %s" % (delays[currentdelay])
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
    
def replaceLeftText2(t):
    global screenText2
    return screenText2[0]

def replaceRightText2(t):
    global screenText2
    return screenText2[1]

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
        if event.key == pygame.locals.K_LEFT:
                                        gn_keystroke = 1
        if event.key == pygame.locals.K_RIGHT:
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
#trigger_in_controller2 = KeyboardTriggerInController(pygame.locals.K_KP5)
stimulus_on_controller = ConstantController(during_go_value=1,between_go_value=0)
stimulus_off_controller = ConstantController(during_go_value=0,between_go_value=1)
left_choice_controller = FunctionController(during_go_func=replaceLeftText)
right_choice_controller = FunctionController(during_go_func=replaceRightText)
left_choice2_controller = FunctionController(during_go_func=replaceLeftText2)
right_choice2_controller = FunctionController(during_go_func=replaceRightText2)
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
p.add_controller(left_choice2,'text',left_choice2_controller)
p.add_controller(right_choice,'text',right_choice_controller)
p.add_controller(right_choice2,'text',right_choice2_controller)
p.add_controller(fixation,'on',fixation_controller)
p.add_controller(newset,'on',newset_controller)
p.add_controller(taskend,'on',taskend_controller)
p.add_controller(p, 'trigger_go_if_armed', state_controller)

p.parameters.handle_event_callbacks = [(pygame.locals.KEYDOWN, keydown)]

p.go()
logfile.close()
shutil.copyfile(backup_filename, log_filename)
