#!/usr/bin/env python

##
## Micky Koffarnus made this
## Shorter discounting task with not-now trials (in scanner)
##

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
import os
import shutil
import win32com.client
objShell = win32com.client.Dispatch("WScript.Shell")
import psycopg2
import StringIO
from VisionEgg.WrappedText import WrappedText

NEW_BLOCK_TIME=10

print " "

if len(sys.argv)<5:
    sid = raw_input('Subject ID? ')
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
    fast="y"
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
    fast = sys.argv[13]

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

if os.path.isfile(pickle_filename):
    S1data = pickle.load(open(pickle_filename, "rb"))
else:
    print " "
    print "No session 1 file found"
    raw_input("Press enter to exit")
    sys.exit
    
if S1data[7] > 0.03542:
    if probability==1:
        delays=[95, 90, 75, 50]
        sorteddelays=[95, 90, 75, 50]    
    else:
        delays=['1 day', '1 week', '1 month', '3 months']
        sorteddelays=['1 day', '1 week', '1 month', '3 months']
    IPindex = 0
elif S1data[7] > 0.0098:
    if probability==1:
        delays=[90, 75, 50, 33]
        sorteddelays=[90, 75, 50, 33]    
    else:
        delays=['1 week', '1 month', '3 months', '1 year']
        sorteddelays=['1 week', '1 month', '3 months', '1 year']
    IPindex = 1
elif S1data[7] > 0.002813:
    if probability==1:
        delays=[75, 50, 33, 10]
        sorteddelays=[75, 50, 33, 10]    
    else:
        delays=['1 month', '3 months', '1 year', '5 years']
        sorteddelays=['1 month', '3 months', '1 year', '5 years']
    IPindex = 2
else:
    if probability==1:
        delays=[50, 33, 10, 5]
        sorteddelays=[50, 33, 10, 5]    
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
screenText2=['XXXXXXX','XXXXXXX']
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
if len(commodityD)>15: fontsize=40
if len(commodityI)>15: fontsize=40
if len(commodityD)>25: fontsize=30
if len(commodityI)>25: fontsize=30
amtText=['','']
amtText0I=''
amtText0D=''
delText=['','']

# Read/write data files
logfile=open(backup_filename,'w')
# log session info and column headers
logfile.write("Subject ID,%s\n" % (sid))
logfile.write("Experiment,%s\n" % (exp))
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
    logfile.write("Trial number,Stimulus onset,Response time,SS amount,LL amount,SS delay,LL delay,Response [-1O;0C;1P],Cert loc [0L;1R]\n")
else:
    logfile.write("Trial number,Stimulus onset,Response time,SS amount,LL amount,SS delay,LL delay,Response [-1O;0I;1D],Now loc [0L;1R]\n")

# Viewport parameters
import ctypes
user32 = ctypes.windll.user32
if user32.GetSystemMetrics(0) < 1024:
    print " "
    print "Horizontal screen resolution needs to be at least 1024."
    raw_input("Press enter to exit")
    sys.exit()    
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
        
title2 = Text(text=' ',
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
    global amtText, amtText0I, amtText0D, delText, screenText2

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
                for i in range(12, 17):
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
                if probability==1:
                    delText[now]="for sure"
                    delText[1-now]="for sure"
                elif past==1:
                    delText[now]="1 hour ago"
                    delText[1-now]="1 hour ago"
                else:
                    delText[now]="now"
                    delText[1-now]="now"
                amounts[question]=choice(noncontrolamounts)
            elif "notnow" in str(amounts[question]):
                otherdelay=int(amounts[question][6])
                amounts[question]=choice(noncontrolamounts)
                if sorteddelays.index(delays[otherdelay])<sorteddelays.index(delays[currentdelay]):
                    if probability==1:
                        delText[now] = "with a %s%% chance" % (delays[otherdelay])
                        delText[1-now] = "with a %s%% chance" % (delays[currentdelay])
                    elif past==1:
                        delText[now] = "%s ago"  % (delays[otherdelay])
                        delText[1-now] = "%s ago" % (delays[currentdelay])
                    else:
                        delText[now] = "in %s" % (delays[otherdelay])
                        delText[1-now] = "in %s" % (delays[currentdelay])
                else:
                    if probability==1:
                        delText[now] = "with a %s%% chance" % (delays[currentdelay])
                        delText[1-now] = "with a %s%% chance" % (delays[otherdelay])
                    elif past==1:
                        delText[now] = "%s ago"  % (delays[currentdelay])
                        delText[1-now] = "%s ago" % (delays[otherdelay])
                    else:
                        delText[now] = "in %s" % (delays[currentdelay])
                        delText[1-now] = "in %s" % (delays[otherdelay])
            else:
                if probability==1:
                    delText[now] = "for sure"
                    delText[1-now] = "with a %s%% chance" % (delays[currentdelay])
                elif past==1:
                    delText[now] = "1 hour ago"
                    delText[1-now] = "%s ago"  % (delays[currentdelay])
                else:
                    delText[now] = "now"
                    delText[1-now] = "in %s" % (delays[currentdelay])
            if commodityI=='$':
                amtText0I = "$0"
                if amountI<1000:
                    amtText[now] = "$%3.2f" % (float(amountI*amounts[question]))
                else:
                    amtText[now] = "$%s" % (group(round(amountI*amounts[question],0))) 
            else:
                amtText0I = "0 %s" % (commodityI)
                if amountI<1:
                    amtText[now] = "%1.2f %s" % (float(amountI*amounts[question]), commodityI) 
                elif amountI<10:
                    amtText[now] = "%1.1f %s" % (float(amountI*amounts[question]), commodityI) 
                else:
                    amtText[now] = "%s %s" % (group(round(amountI*amounts[question],0)), commodityI) 
            if commodityD=='$':
                amtText0D = "$0"
                if amountD<1000:
                    amtText[1-now] = "$%3.2f" % (amountD)
                else:
                    amtText[1-now] = "$%s" % (group(round(amountD,0)))
            else:
                amtText0D = "0 %s" % (commodityD)
                if amountD<1:
                    amtText[1-now] = "%1.2f %s" % (float(amountD), commodityD) 
                elif amountD<10:
                    amtText[1-now] = "%1.1f %s" % (float(amountD), commodityD) 
                else:
                    amtText[1-now] = "%s %s" % (group(round(amountD,0)), commodityD)
            if explicit0==0:
                screenText[now] = "%s" % (amtText[now])
                screenText[1-now] = "%s" % (amtText[1-now])
                screenText2[now] = "%s" % (delText[now])
                screenText2[1-now] = "%s" % (delText[1-now])
            else:
                screenText[now] = "%s %s and" % (amtText[now], delText[now])
                screenText2[now] = "%s %s" % (amtText0I, delText[1-now])
                screenText[1-now] = "%s %s and" % (amtText[1-now], delText[1-now])
                screenText2[1-now] = "%s %s" % (amtText0D, delText[now])
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
        if question < 50:
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
                logfile.write('%i,%f,%f,"%s","%s",%s,%s,%i,%i\n' % (trialnum, stim_onset, t, screenText[now], screenText[1-now], screenText2[now], screenText2[1-now], response, now))
                screenText[0] = "XXXXXXX"
                screenText[1] = "XXXXXXX"   
                screenText2[0] = "XXXXXXX"
                screenText2[1] = "XXXXXXX"    
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
p.add_controller(taskend,'on',stimulus_on_controller)
p.add_controller(p, 'trigger_go_if_armed', state_controller)

p.parameters.handle_event_callbacks = [(pygame.locals.KEYDOWN, keydown)]

p.go()
logfile.close()
shutil.copyfile(backup_filename, log_filename)
