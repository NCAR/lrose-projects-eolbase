#!/usr/bin/env python

#===========================================================================
#
# Produce plots for ZDR bias
#
#===========================================================================

from __future__ import print_function

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
    parser.add_option('--cp_file',
                      dest='cpFilePath',
                      default='../data/pecan/spol_pecan_CP_analysis_20150524_000021.txt',
                      help='CP results file path')
    parser.add_option('--bias_file',
                      dest='biasFilePath',
                      default='../data/pecan/zdr_bias.kddc.txt',
                      help='File path for bias results')
    parser.add_option('--title',
                      dest='title',
                      default= \
                      'KDDC daily mean ZDRM bias in ice/snow',
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
                      default=301,
                      help='Len of moving mean filter')
    
    (options, args) = parser.parse_args()
    
    if (options.verbose == True):
        options.debug = True

    if (options.debug == True):
        print("Running %prog", file=sys.stderr)
        print("  cpFilePath: ", options.cpFilePath, file=sys.stderr)
        print("  biasFilePath: ", options.biasFilePath, file=sys.stderr)

    # read in column headers for bias results

    iret, biasHdrs, biasData = readColumnHeaders(options.biasFilePath)
    if (iret != 0):
        sys.exit(-1)

    # read in data for bias results

    biasData, biasTimes = readInputData(options.biasFilePath, biasHdrs, biasData)

    # read in column headers for CP results

    iret, cpHdrs, cpData = readColumnHeaders(options.cpFilePath)
    if (iret != 0):
        sys.exit(-1)

    # read in data for CP results

    cpData, cpTimes = readInputData(options.cpFilePath, cpHdrs, cpData)

    # render the plot
    
    doPlot(biasData, biasTimes, cpData, cpTimes)

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
            print("colHeaders: ", colHeaders, file=sys.stderr)
    else:
        print("ERROR - readColumnHeaders", file=sys.stderr)
        print("  First line does not start with #", file=sys.stderr)
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
                var == 'unix_time' or var == 'npts'):
                colData[var].append(int(data[index]))
            elif (var == 'fileName' or var.find('Time') >= 0):
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

def doPlot(biasData, biasTimes, cpData, cpTimes):

    widthIn = float(options.figWidthMm) / 25.4
    htIn = float(options.figHeightMm) / 25.4

    fig1 = plt.figure(1, (widthIn, htIn))
    ax1 = fig1.add_subplot(1,1,1,xmargin=0.0)
    ax1.plot(biasTimes, np.zeros(len(biasTimes)), linewidth=1, color = 'gray')
    
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

    rawBiasPerc20 = np.array(biasData["ZdrBiasPercentile20"]).astype(np.double)
    biasPercent20 = movingAverage(rawBiasPerc20, lenMeanFilter)

    biasPercent25 = np.array(biasData["ZdrBiasPercentile25"]).astype(np.double)
    biasPercent25 = movingAverage(biasPercent25, lenMeanFilter)

    biasPercent33 = np.array(biasData["ZdrBiasPercentile33"]).astype(np.double)
    biasPercent33 = movingAverage(biasPercent33, lenMeanFilter)

    validMean = np.isfinite(biasMean)
    validPercent15 = np.isfinite(biasPercent15)
    validRawPerc20 = np.isfinite(rawBiasPerc20)
    validPercent20 = np.isfinite(biasPercent20)
    validPercent25 = np.isfinite(biasPercent25)
    validPercent33 = np.isfinite(biasPercent33)

    # load up receiver gain etc - axis 4
    
    #(dailyBtimes20, dailyPerc20) = computeDailyStats(btimes[validRawPerc20], 
    #                                                 rawBiasPerc20[validRawPerc20])
    (dailyBtimes20, dailyPerc20) = computeDailyStats(btimes[validPercent20], 
                                                     biasPercent20[validPercent20])

    #ax1.plot(btimes[validMean], biasMean[validMean], \
    #         label = 'ZDR Bias mean', color='red')
    
    ax1.plot(btimes[validPercent15], biasPercent15[validPercent15], \
             label = 'ZDR Bias percentile 15', linewidth=1, color='red')

    ax1.plot(btimes[validPercent20], biasPercent20[validPercent20], \
             label = 'ZDR Bias percentile 20', linewidth=1, color='blue')

    ax1.plot(btimes[validPercent25], biasPercent25[validPercent25], \
             label = 'ZDR Bias percentile 25', linewidth=1, color='magenta')


    ax1.plot(dailyBtimes20, dailyPerc20, \
             label = 'Bias20%', linewidth=1, color='blue')
    ax1.plot(dailyBtimes20, dailyPerc20, \
             "^", label = 'Bias20%', color='blue', markersize=10)

    legend1 = ax1.legend(loc='upper right', ncol=7)
    for label in legend1.get_texts():
        label.set_fontsize('x-small')
    ax1.set_xlabel("Date")
    ax1.set_ylabel("KDDC ZDR Bias (dB)")
    ax1.grid(True)
    ax1.set_ylim([-0.4, +0.25])

    hfmt = dates.DateFormatter('%y/%m/%d')
    ax1.xaxis.set_major_locator(dates.DayLocator())
    ax1.xaxis.set_major_formatter(hfmt)

    for tick in ax1.xaxis.get_major_ticks():
        tick.label.set_fontsize(8) 

    fig1.suptitle(options.title)
    fig1.autofmt_xdate()
    plt.tight_layout()
    plt.subplots_adjust(top=0.96)
    plt.show()

########################################################################
# compute daily means for dbz bias

def computeDailyStats(times, vals):

    dailyTimes = []
    dailyMeans = []

    nptimes = np.array(times).astype(datetime.datetime)
    npvals = np.array(vals).astype(np.double)

    validFlag = np.isfinite(npvals)
    timesValid = nptimes[validFlag]
    valsValid = npvals[validFlag]
    
    startTime = nptimes[0]
    endTime = nptimes[-1]
    
    startDate = datetime.datetime(startTime.year, startTime.month, startTime.day, 0, 0, 0)
    endDate = datetime.datetime(endTime.year, endTime.month, endTime.day, 0, 0, 0)

    oneDay = datetime.timedelta(1)
    halfDay = datetime.timedelta(0.5)
    
    thisDate = startDate
    while (thisDate < endDate + oneDay):
        
        nextDate = thisDate + oneDay
        result = []
        
        sum = 0.0
        sumDeltaTime = datetime.timedelta(0)
        count = 0.0
        for ii, val in enumerate(valsValid, start=0):
            thisTime = timesValid[ii]
            if (thisTime >= thisDate and thisTime < nextDate):
                sum = sum + val
                deltaTime = thisTime - thisDate
                sumDeltaTime = sumDeltaTime + deltaTime
                count = count + 1
                result.append(val)
        if (count > 1):
            mean = sum / count
            meanDeltaTime = datetime.timedelta(0, sumDeltaTime.total_seconds() / count)
            dailyMeans.append(mean)
            dailyTimes.append(thisDate + meanDeltaTime)
            # print >>sys.stderr, " daily time, meanStrong: ", dailyTimes[-1], meanStrong
            result.sort()
            
        thisDate = thisDate + oneDay

    return (dailyTimes, dailyMeans)


########################################################################
# Run a command in a shell, wait for it to complete

def runCommand(cmd):

    if (options.debug == True):
        print("running cmd:",cmd, file=sys.stderr)
    
    try:
        retcode = subprocess.call(cmd, shell=True)
        if retcode < 0:
            print("Child was terminated by signal: ", -retcode, file=sys.stderr)
        else:
            if (options.debug == True):
                print("Child returned code: ", retcode, file=sys.stderr)
    except OSError as e:
        print("Execution failed:", e, file=sys.stderr)

########################################################################
# Run - entry point

if __name__ == "__main__":
   main()

