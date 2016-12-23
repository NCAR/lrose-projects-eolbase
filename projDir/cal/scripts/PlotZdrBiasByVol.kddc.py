#!/usr/bin/env python

#===========================================================================
#
# Produce plots for ZDR bias by volume
#
#===========================================================================

import os
import sys
import subprocess
from optparse import OptionParser
import numpy as np
from numpy import convolve
from numpy import linalg, array, ones
import matplotlib.pyplot as plt
from matplotlib import dates
import math
import datetime
import contextlib

def main():

#   globals

    global options
    global debug
    global startTime
    global endTime

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
    parser.add_option('--bias_file',
                      dest='biasFilePath',
                      default='../data/pecan/kddc_zdr_bias_in_snow.txt',
                      help='File path for bias results')
    parser.add_option('--title',
                      dest='title',
                      default='ZDR BIAS FROM ICE',
                      help='Title for plot')
    parser.add_option('--width',
                      dest='figWidthMm',
                      default=400,
                      help='Width of figure in mm')
    parser.add_option('--height',
                      dest='figHeightMm',
                      default=320,
                      help='Height of figure in mm')
    parser.add_option('--lenMean',
                      dest='lenMean',
                      default=1,
                      help='Len of moving mean filter')
    parser.add_option('--start',
                      dest='startTime',
                      default='2015 06 26 00 00 00',
                      help='Start time for XY plot')
    parser.add_option('--end',
                      dest='endTime',
                      default='2015 06 27 00 00 00',
                      help='End time for XY plot')
    
    (options, args) = parser.parse_args()
    
    if (options.verbose == True):
        options.debug = True

    year, month, day, hour, minute, sec = options.startTime.split()
    startTime = datetime.datetime(int(year), int(month), int(day),
                                  int(hour), int(minute), int(sec))

    year, month, day, hour, minute, sec = options.endTime.split()
    endTime = datetime.datetime(int(year), int(month), int(day),
                                int(hour), int(minute), int(sec))

    if (options.debug == True):
        print >>sys.stderr, "Running %prog"
        print >>sys.stderr, "  biasFilePath: ", options.biasFilePath
        print >>sys.stderr, "  startTime: ", startTime
        print >>sys.stderr, "  endTime: ", endTime

    # read in column headers for bias results

    iret, biasHdrs, biasData = readColumnHeaders(options.biasFilePath)
    if (iret != 0):
        sys.exit(-1)

    # read in data for bias results

    biasData, biasTimes = readInputData(options.biasFilePath, biasHdrs, biasData)

    # render the plot
    
    doPlot(biasData, biasTimes)

    sys.exit(0)
    
########################################################################
# Read columm headers for the data
# this is in the first line

def readColumnHeaders(filePath):

    colHeaders = []
    colData = {}

    fp = open(filePath, 'r')
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
        return -1, colHeaders, colData
    
    for index, var in enumerate(colHeaders, start=0):
        colData[var] = []
        
    return 0, colHeaders, colData

########################################################################
# Read in the data

def readInputData(filePath, colHeaders, colData):

    # open file

    fp = open(filePath, 'r')
    lines = fp.readlines()

    # read in a line at a time, set colData
    for line in lines:
        
        commentIndex = line.find("#")
        if (commentIndex >= 0):
            continue
            
        # data
        
        data = line.strip().split()

        for index, var in enumerate(colHeaders, start=0):
            if (var == 'count' or var == 'year' or var == 'month' or var == 'day' or \
                var == 'hour' or var == 'min' or var == 'sec' or \
                var == 'unix_time'):
                colData[var].append(int(data[index]))
            elif (var == 'TempTime'):
                colData[var].append(data[index])
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

    obsTimes = []
    for ii, var in enumerate(year, start=0):
        thisTime = datetime.datetime(year[ii], month[ii], day[ii],
                                     hour[ii], minute[ii], sec[ii])
        obsTimes.append(thisTime)

    return colData, obsTimes

########################################################################
# Moving average filter

def movingAverage(values, window):

    weights = np.repeat(1.0, window)/window
    sma = np.convolve(values, weights, 'same')
    return sma

########################################################################
# Plot

def doPlot(biasData, biasTimes):

    fileName = options.biasFilePath
    titleStr = "File: " + fileName
    hfmt = dates.DateFormatter('%y/%m/%d')

    lenMeanFilter = int(options.lenMean)

    #   set up np arrays

    btimes = np.array(biasTimes).astype(datetime.datetime)

    biasMean = np.array(biasData["ZdrBiasMean"]).astype(np.double)
    biasMean = movingAverage(biasMean, lenMeanFilter)

    biasPercent15 = np.array(biasData["ZdrBiasPercentile15"]).astype(np.double)
    biasPercent15 = movingAverage(biasPercent15, lenMeanFilter)

    biasPercent20 = np.array(biasData["ZdrBiasPercentile20"]).astype(np.double)
    biasPercent20 = movingAverage(biasPercent20, lenMeanFilter)

    biasPercent25 = np.array(biasData["ZdrBiasPercentile25"]).astype(np.double)
    biasPercent25 = movingAverage(biasPercent25, lenMeanFilter)

    biasPercent33 = np.array(biasData["ZdrBiasPercentile33"]).astype(np.double)
    biasPercent33 = movingAverage(biasPercent33, lenMeanFilter)

    validMean = np.isfinite(biasMean)
    validPercent15 = np.isfinite(biasPercent15)
    validPercent20 = np.isfinite(biasPercent20)
    validPercent25 = np.isfinite(biasPercent25)
    validPercent33 = np.isfinite(biasPercent33)

    # Site Temperature

    tempSite = np.array(biasData["TempSite"]).astype(np.double)
    validTempSite = np.isfinite(tempSite)

    validBtimes = btimes[validPercent20]
    validBiases = biasPercent20[validPercent20]
    
    tempVals = []
    biasVals = []

    for ii, biasVal in enumerate(validBiases, start=0):
        btime = validBtimes[ii]
        if (btime >= startTime and btime <= endTime):
            tempTime, tempVal = getClosestTemp(btime, btimes, tempSite)
            if (np.isfinite(tempVal)):
                tempVals.append(tempVal)
                biasVals.append(biasVal)
                if (options.verbose):
                    print >>sys.stderr, "==>> biasTime, biasVal, tempTime, tempVal:", \
                        btime, biasVal, tempTime, tempVal

    # linear regression bias vs temp

    A = array([tempVals, ones(len(tempVals))])
    ww = linalg.lstsq(A.T, biasVals)[0] # obtaining the fit, ww[0] is slope, ww[1] is intercept
    regrX = []
    regrY = []
    minTemp = min(tempVals)
    maxTemp = max(tempVals)
    regrX.append(minTemp)
    regrX.append(maxTemp)
    regrY.append(ww[0] * minTemp + ww[1])
    regrY.append(ww[0] * maxTemp + ww[1])
    
    # set up plots

    widthIn = float(options.figWidthMm) / 25.4
    htIn = float(options.figHeightMm) / 25.4

    fig1 = plt.figure(1, (widthIn, htIn))
    fig2 = plt.figure(2, (widthIn/2, htIn/2))

    ax1 = fig1.add_subplot(2,1,1,xmargin=0.0)
    ax2 = fig1.add_subplot(2,1,2,xmargin=0.0)

    ax3 = fig2.add_subplot(1,1,1,xmargin=1.0, ymargin=1.0)
    #ax3 = fig2.add_subplot(1,1,1,xmargin=0.0)

    oneDay = datetime.timedelta(1.0)
    ax1.set_xlim([btimes[0] - oneDay, btimes[-1] + oneDay])
    ax1.set_title("ZDR bias")
    ax2.set_xlim([btimes[0] - oneDay, btimes[-1] + oneDay])
    ax2.set_title("Site temperature (C)")

    ax1.plot(btimes[validPercent20], biasPercent20[validPercent20], \
             "ro", label = 'ZDR Bias percentile 20', linewidth=1)

    ax1.plot(btimes[validPercent20], biasPercent20[validPercent20], \
             label = 'ZDR Bias percentile 20', linewidth=1, color='red')

    ax2.plot(btimes[validTempSite], tempSite[validTempSite], \
             linewidth=1, label = 'Site Temp', color = 'blue')

    configDateAxis(ax1, -9999, 9999, "ZDR Bias (dB)", 'upper right')
    configDateAxis(ax2, -9999, 9999, "Temp (C)", 'upper right')
    label3 = "ZDR Bias = " + ("%.3f" % ww[0]) + " * temp + " + ("%.3f" % ww[1])
    ax3.plot(tempVals, biasVals, 
             "x", label = label3, color = 'blue')
    ax3.plot(regrX, regrY, linewidth=3, color = 'blue')
    
    legend3 = ax3.legend(loc="upper left", ncol=2)
    for label3 in legend3.get_texts():
        label3.set_fontsize(12)
    ax3.set_xlabel("Site temperature (C)")
    ax3.set_ylabel("ZDR Bias (dB)")
    ax3.grid(True)
    ax3.set_ylim([-0.5, 0.5])
    ax3.set_xlim([minTemp - 1, maxTemp + 1])
    title3 = "ZDR bias Vs Temp: " + str(startTime) + " - " + str(endTime)
    ax3.set_title(title3)

    fig1.autofmt_xdate()

    fig1.tight_layout()
    fig1.subplots_adjust(bottom=0.03, left=0.06, right=0.97, top=0.97)
    #plt.subplots_adjust(top=0.96)
    plt.show()

########################################################################
# initialize legends etc

def configDateAxis(ax, miny, maxy, ylabel, legendLoc):
    
    legend = ax.legend(loc=legendLoc, ncol=6)
    for label in legend.get_texts():
        label.set_fontsize('x-small')
    ax.set_xlabel("Date")
    ax.set_ylabel(ylabel)
    ax.grid(True)
    if (miny > -9990 and maxy > -9990):
        ax.set_ylim([miny, maxy])
    hfmt = dates.DateFormatter('%y/%m/%d')
    ax.xaxis.set_major_locator(dates.DayLocator())
    ax.xaxis.set_major_formatter(hfmt)
    for tick in ax.xaxis.get_major_ticks():
        tick.label.set_fontsize(8) 

########################################################################
# get temp closest in time to the search time

def getClosestTemp(biasTime, tempTimes, obsTemps):

    twoHours = datetime.timedelta(0.0, 7200.0)

    validTimes = ((tempTimes > (biasTime - twoHours)) & \
                  (tempTimes < (biasTime + twoHours)))

    if (len(validTimes) < 1):
        return (biasTime, float('NaN'))
    
    searchTimes = tempTimes[validTimes]
    searchTemps = obsTemps[validTimes]

    if (len(searchTimes) < 1 or len(searchTemps) < 1):
        return (biasTime, float('NaN'))

    searchTimes = tempTimes[validTimes]
    searchTemps = obsTemps[validTimes]

    minDeltaTime = 1.0e99
    ttime = searchTimes[0]
    temp = searchTemps[0]
    for ii, temptime in enumerate(searchTimes, start=0):
        deltaTime = math.fabs((temptime - biasTime).total_seconds())
        if (deltaTime < minDeltaTime):
            minDeltaTime = deltaTime
            temp = searchTemps[ii]
            ttime = temptime

    return (ttime, temp)

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

