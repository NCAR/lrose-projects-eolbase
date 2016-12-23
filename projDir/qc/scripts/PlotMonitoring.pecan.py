#!/usr/bin/env python

#===========================================================================
#
# Produce plots for monitored variables in PECAN
#
#===========================================================================

import os
import sys
import subprocess
from optparse import OptionParser
import numpy as np
from numpy import convolve
import matplotlib.pyplot as plt
from matplotlib import dates
import math
import datetime

def main():

#   globals

    global options
    global debug
    global meanFilterLen

    global varIndex
    varIndex = 8    # starting variable
    
    global colHeaders
    colHeaders = []

    global colIndex
    colIndex = {}

    global colData
    colData = {}

    global obsTimes
    obsTimes = []

# parse the command line

    usage = "usage: %prog [options]"
    parser = OptionParser(usage)
    parser.add_option('--debug',
                      dest='debug', default=False,
                      action="store_true",
                      help='Set debugging on')
    parser.add_option('--verbose',
                      dest='verbose', default=False,
                      action="store_true",
                      help='Set verbose debugging on')
    parser.add_option('--file',
                      dest='inputFilePath',
                      default='../data/pecan/spol_pecan_CP_analysis_20150524_000021.txt',
                      help='Input file path')
    parser.add_option('--title',
                      dest='title',
                      default='SPOL monitoring - PECAN',
                      help='Title for plot')
    parser.add_option('--width',
                      dest='figWidthMm',
                      default=400,
                      help='Width of figure in mm')
    parser.add_option('--height',
                      dest='figHeightMm',
                      default=250,
                      help='Height of figure in mm')
    parser.add_option('--meanLen',
                      dest='meanLen',
                      default=1,
                      help='Len of moving mean filter')
    
    (options, args) = parser.parse_args()
    
    if (options.verbose == True):
        options.debug = True

    if (options.debug == True):
        print >>sys.stderr, "Running PlotCpRatio:"
        print >>sys.stderr, "  inputFilePath: ", options.inputFilePath

    meanFilterLen = int(options.meanLen)

    # read in column headers

    if (readColumnHeaders() != 0):
        sys.exit(-1)

    # read in file

    readInputData()

    # perform plotting
    
    doPlot()

    sys.exit(0)
    
########################################################################
# Read columm headers for the data
# this is in the fist line

def readColumnHeaders():

    global colHeaders
    global colIndex
    global colData

    fp = open(options.inputFilePath, 'r')
    line = fp.readline()
    fp.close()
    
    commentIndex = line.find("#")
    if (commentIndex == 0):
        # header
        colHeaders = line.lstrip("# ").rstrip("\n").split()
        if (options.debug == True):
            print >>sys.stderr, "colHeaders: ", colHeaders
    else:
        print >>sys.stderr, "ERROR - readColumnHeaders"
        print >>sys.stderr, "  First line does not start with #"
        return -1
    
    for index, var in enumerate(colHeaders, start=0):
        colIndex[var] = index
        colData[var] = []
        
    if (options.debug == True):
        print >>sys.stderr, "colIndex: ", colIndex

    return 0

########################################################################
# Read in the data

def readInputData():

    global colData
    global obsTimes

    # open file

    fp = open(options.inputFilePath, 'r')
    lines = fp.readlines()

    # read in a line at a time, set colData
    for line in lines:
        
        commentIndex = line.find("#")
        if (commentIndex >= 0):
            continue
            
        # data
        
        data = line.strip().split()

        for index, var in enumerate(colHeaders, start=0):
            if (var == 'obsNum' or var == 'year' or var == 'month' or var == 'day' or \
                var == 'hour' or var == 'min' or var == 'sec' or \
                var == 'nPairsClut' or var == 'nPairsWx'):
                colData[var].append(int(data[index]))
            else:
                colData[var].append(float(data[index]))

    fp.close()

    # load observation times array

    year = colData['year']
    month = colData['month']
    day = colData['day']
    hour = colData['hour']
    minute = colData['min']
    sec = colData['sec']

    for ii, var in enumerate(year, start=0):
        thisTime = datetime.datetime(year[ii], month[ii], day[ii],
                                     hour[ii], minute[ii], sec[ii])
        obsTimes.append(thisTime)

########################################################################
# Moving average filter

def movingAverage(values, window):

    weights = np.repeat(1.0, window)/window
    sma = np.convolve(values, weights, 'same')
    return sma

########################################################################
# Plot

def doPlot():

    widthIn = float(options.figWidthMm) / 25.4
    htIn = float(options.figHeightMm) / 25.4

    fig1 = plt.figure(1, (widthIn, htIn))
    
    ax1 = fig1.add_subplot(3,1,1,xmargin=0.0)
    ax2 = fig1.add_subplot(3,1,2,xmargin=0.0)
    ax3 = fig1.add_subplot(3,1,3,xmargin=0.0)

    fileName = options.inputFilePath
    titleStr = "File: " + fileName
    hfmt = dates.DateFormatter('%y/%m/%d')

    #   set up np arrays

    times = np.array(obsTimes).astype(datetime.datetime)

    # ax1 - XMIT power

    timeStart1us = datetime.datetime(2015, 6, 8, 0, 0, 0)
    pwrCorrFlag = times < timeStart1us
    pwrCorr = np.zeros(len(times))
    pwrCorr[times < timeStart1us] = -1.76

    ax1.plot(times, np.zeros(len(times)), linewidth=1, color = 'black')

    CalTxPwrH = np.array(colData["calTxPwrH"]).astype(np.double)
    validCalTxPwrH = np.isfinite(CalTxPwrH)
    ax1.plot(times[validCalTxPwrH], CalTxPwrH[validCalTxPwrH], \
             linewidth=1, label = 'CalTxPwrH', color = 'red')

    CalTxPwrV = np.array(colData["calTxPwrV"]).astype(np.double)
    validCalTxPwrV = np.isfinite(CalTxPwrV)
    ax1.plot(times[validCalTxPwrV], CalTxPwrV[validCalTxPwrV], \
             linewidth=1, label = 'CalTxPwrV', color = 'orange')

    TxPwrH = np.array(colData["TxPwrH"]).astype(np.double)
    TxPwrH = movingAverage(TxPwrH, meanFilterLen)
    TxPwrH = TxPwrH + pwrCorr
    validTxPwrH = np.isfinite(TxPwrH)
    ax1.plot(times[validTxPwrH], TxPwrH[validTxPwrH], \
             linewidth=1, label = 'TxPwrH', color = 'blue')

    TxPwrV = np.array(colData["TxPwrV"]).astype(np.double)
    TxPwrV = movingAverage(TxPwrV, meanFilterLen)
    TxPwrV = TxPwrV + pwrCorr
    validTxPwrV = np.isfinite(TxPwrV)
    ax1.plot(times[validTxPwrV], TxPwrV[validTxPwrV], \
             linewidth=1, label = 'TxPwrV', color = 'cyan')
    
    legend1 = ax1.legend(loc='upper right', ncol=5)
    for label in legend1.get_texts():
        label.set_fontsize('x-small')
    ax1.set_xlabel("Date")
    ax1.set_ylabel("Tx Power (dBm)")
    ax1.grid(True)
    ax1.set_ylim([84.5, 89])

    ax1.xaxis.set_major_locator(dates.DayLocator())
    ax1.xaxis.set_major_formatter(hfmt)

    # ax2 - inside temperatures

    tempRear = np.array(colData["TempRear"]).astype(np.double)
    tempFront = np.array(colData["TempFront"]).astype(np.double) + 10.0
    tempKlystron = np.array(colData["TempKlystron"]).astype(np.double)
    tempLnaV = np.array(colData["TempLnaV"]).astype(np.double) + 10.0
    tempLnaH = np.array(colData["TempLnaH"]).astype(np.double) + 10.0

    validTempRear = np.isfinite(tempRear)
    validTempFront = np.isfinite(tempFront)
    validTempKlystron = np.isfinite(tempKlystron)
    validTempLnaV = np.isfinite(tempLnaV)
    validTempLnaH = np.isfinite(tempLnaH)

    ax2.plot(times, np.zeros(len(times)), linewidth=0, color = 'black')

    ax2.plot(times[validTempRear], tempRear[validTempRear], \
             linewidth=1, label = 'Rear Temp', color = 'orange')
    ax2.plot(times[validTempKlystron], tempKlystron[validTempKlystron], \
             linewidth=1, label = 'Klystron Temp', color = 'green')
    ax2.plot(times[validTempFront], tempFront[validTempFront], \
             linewidth=1, label = 'Front Temp', color = 'magenta')
    ax2.plot(times[validTempLnaH], tempLnaH[validTempLnaH], \
             linewidth=1, label = 'LnaH Temp', color = 'blue')
    ax2.plot(times[validTempLnaV], tempLnaV[validTempLnaV], \
             linewidth=1, label = 'LnaV Temp', color = 'cyan')
    
    legend2 = ax2.legend(loc='upper right', ncol=6)
    for label in legend2.get_texts():
        label.set_fontsize('x-small')
    ax2.set_xlabel("Date")
    ax2.set_ylabel("Inside temps (C)")
    ax2.grid(True)

    ax2.xaxis.set_major_locator(dates.DayLocator())
    ax2.xaxis.set_major_formatter(hfmt)
    ax2.set_ylim([20, 60])

    for tick in ax2.xaxis.get_major_ticks():
        tick.label.set_fontsize(8) 

    # ax3 - ambient (outside) temperature

    tempSite = np.array(colData["TempSite"]).astype(np.double)
    validTempSite = np.isfinite(tempSite)

    ax3.plot(times, np.zeros(len(times)), linewidth=0, color = 'black')
    
    ax3.plot(times[validTempSite], tempSite[validTempSite], \
             linewidth=1, label = 'Site Temp', color = 'red')

    legend3 = ax3.legend(loc='upper right', ncol=6)
    for label in legend3.get_texts():
        label.set_fontsize('x-small')
    ax3.set_xlabel("Date")
    ax3.set_ylabel("Ambient temp (C)")
    ax3.grid(True)

    ax3.xaxis.set_major_locator(dates.DayLocator())
    ax3.xaxis.set_major_formatter(hfmt)
    ax3.set_ylim([10, 45])

    for tick in ax3.xaxis.get_major_ticks():
        tick.label.set_fontsize(8) 

    fig1.suptitle("MONITORING ANALYSIS FOR SPOL - PECAN")
    fig1.autofmt_xdate()

    plt.tight_layout()
    plt.subplots_adjust(top=0.96)
    plt.show()

    return

########################################################################
# Run a command in a shell, wait for it to complete

def runCommand(cmd):

    if (options.debug == True):
        print >>sys.stderr, "running cmd:",cmd
    
    try:
        retcode = subprocess.call(cmd, shell=True)
        if retcode < 0:
            print >>sys.stderr, "Child was terminated by signal: ", -retcode
        else:
            if (options.debug == True):
                print >>sys.stderr, "Child returned code: ", retcode
    except OSError, e:
        print >>sys.stderr, "Execution failed:", e

########################################################################
# Run - entry point

if __name__ == "__main__":
   main()

