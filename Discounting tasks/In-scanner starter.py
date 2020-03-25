#!/usr/bin/env python

##
## Micky Koffarnus made this (Jan 2017)
##

import os
import sys
from subprocess import call
from random import shuffle
from VisionEgg import *
VisionEgg.start_default_logging(); VisionEgg.watch_exceptions()
import time
print "\n\n"

## These lines will prompt the user for subject ID and session name ##
sid = raw_input('Subject ID: ')
exp = raw_input('Session: ')

## These lines will set the different task parameters without prompting the user.    ##
## All of the values entered here should be in quotation marks after the equal sign. ##
# Put a "0" here for delay discounting and a "1" for probability discounting
probability = "0" 
# Put a "0" for gains and a "1" for losses
losses = "0" 
# Put a "0" for future and a "1" for past. This should be "0" for probability discounting.
past = "0" 
# Put a "0" for implicit zero and a "1" for explicit zero
explicit0 = "0" 
# Delayed or probabilistic commodity with unit (e.g., "g of cocaine"). Just put $ for money.
commodityD = "$" 
# Immediate or certain commodity with unit (e.g., "g of cocaine"). Just put $ for money. For single-commodity discounting, this should be the same as the delayed commodity.
commodityI = "$" 
# Delayed or probabilistic amount in quotation marks
amountD = "1000" 
# Equivalence value for the immediate/certain commodity. For single-commodity discounting, this should be the same amount as the delayed amount.
amountI = "1000" 
# Stop at the end on the Task Complete screen [y/n]
taskpause = "n" 

## This line starts the task with the settings from above. Don't edit this unless you know what you're doing. ##
call(['python', 'In-scanner discounting.py', sid, exp, probability, losses, past, explicit0, commodityD, commodityI, amountD, amountI, os.path.dirname(sys.argv[0]), taskpause, 'y']) 
