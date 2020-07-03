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
                      default='../data/dynamo/zdr_bias_ice.dynamo.txt',
                      help='File path for bias results')
    parser.add_option('--title',
                      dest='title',
                      default='DYNAMO ZDR BIAS FROM SNOW - MEASURED and CORRECTED',
                      help='Title for plot')
    parser.add_option('--width',
                      dest='figWidthMm',
                      default=300,
                      help='Width of figure in mm')
    parser.add_option('--height',
                      dest='figHeightMm',
                      default=300,
                      help='Height of figure in mm')
    parser.add_option('--lenMean',
                      dest='lenMean',
                      default=1,
                      help='Len of moving mean filter')
    parser.add_option('--start',
                      dest='startTime',
                      default='2011 10 01 00 00 00',
                      help='Start time for XY plot')
    parser.add_option('--end',
                      dest='endTime',
                      default='2012 01 16 00 00 00',
                      help='End time for XY plot')
    parser.add_option('--sur_only',
                      dest='surOnly', default=False,
                      action="store_true",
                      help='Only process surveillance scans')
    parser.add_option('--rhi_only',
                      dest='rhiOnly', default=False,
                      action="store_true",
                      help='Only process RHI scans')
    parser.add_option('--mean',
                      dest='plotMean', default=False,
                      action="store_true",
                      help='Plot the adjusted mean')
    parser.add_option('--adj',
                      dest='meanAdj',
                      default='-0.25',
                      help='Adjustment to mean for ZDR bias')
    parser.add_option('--perc',
                      dest='percentile',
                      default='5.0',
                      help='Histogram percentile value for ZDR bias')
    
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
        print("Running %prog", file=sys.stderr)
        print("  biasFilePath: ", options.biasFilePath, file=sys.stderr)
        print("  startTime: ", startTime, file=sys.stderr)
        print("  endTime: ", endTime, file=sys.stderr)
        print("  surOnly: ", options.surOnly, file=sys.stderr)
        print("  rhiOnly: ", options.rhiOnly, file=sys.stderr)
        print("  meanAdj: ", options.meanAdj, file=sys.stderr)
        print("  percentile: ", options.percentile, file=sys.stderr)

    # read in column headers for bias results

    iret, biasHdrs = readColumnHeaders(options.biasFilePath)
    if (iret != 0):
        sys.exit(-1)

    # read in data for bias results

    biasData, biasTimes = readInputData(options.biasFilePath, biasHdrs)

    # set the vert pointing results

    setVertPointResults()

    # prepare the data for plotting

    prepareData(biasData, biasTimes)

    # render the plot
    
    doPlot()

    sys.exit(0)
    
########################################################################
# Read columm headers for the data
# this is in the first line

def readColumnHeaders(filePath):

    colHeaders = []

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
    
    return 0, colHeaders

########################################################################
# Read in the data

def readInputData(filePath, colHeaders):

    # open file

    fp = open(filePath, 'r')
    lines = fp.readlines()

    obsTimes = []
    colData = {}
    for index, var in enumerate(colHeaders, start=0):
        colData[var] = []

    # read in a line at a time, set colData
    for line in lines:
        
        commentIndex = line.find("#")
        if (commentIndex >= 0):
            continue
            
        # data
        
        data = line.strip().split()
        if (len(data) != len(colHeaders)):
            if (options.debug == True):
                print("skipping line: ", line, file=sys.stderr)
            continue;

        values = {}
        for index, var in enumerate(colHeaders, start=0):
            if (var == 'count' or \
                var == 'year' or var == 'month' or var == 'day' or \
                var == 'hour' or var == 'min' or var == 'sec' or \
                var == 'unix_time'):
                values[var] = int(data[index])
            else:
                values[var] = float(data[index])

        # load observation times array

        year = values['year']
        month = values['month']
        day = values['day']
        hour = values['hour']
        minute = values['min']
        sec = values['sec']

        thisTime = datetime.datetime(year, month, day,
                                     hour, minute, sec)

        if (thisTime >= startTime and thisTime <= endTime):
            for index, var in enumerate(colHeaders, start=0):
                colData[var].append(values[var])
            obsTimes.append(thisTime)

    fp.close()

    return colData, obsTimes

########################################################################
# Moving average filter

def movingAverage(values, window):

    if (window < 2):
        return values

    weights = np.repeat(1.0, window)/window
    sma = np.convolve(values, weights, 'same')
    return sma

########################################################################
# Set the vert pointing results

def setVertPointResults():

    global vertTimes, vertData
    vertTimes = []
    vertData = []

    # obsTime = datetime.datetime(2011, 9, 30, 6, 0, 0)
    # vertTimes.append(obsTime)
    # vertData.append(0.237)

    obsTime = datetime.datetime(2011, 10, 4, 11, 45, 0)
    vertTimes.append(obsTime)
    vertData.append(0.284)

    obsTime = datetime.datetime(2011, 10, 10, 9, 48, 0)
    vertTimes.append(obsTime)
    vertData.append(0.276)

    obsTime = datetime.datetime(2011, 10, 16, 6, 12, 0)
    vertTimes.append(obsTime)
    vertData.append(0.284)

    obsTime = datetime.datetime(2011, 10, 24, 8, 42, 0)
    vertTimes.append(obsTime)
    vertData.append(0.289)

    obsTime = datetime.datetime(2011, 11, 2, 11, 28, 0)
    vertTimes.append(obsTime)
    vertData.append(0.362)

    obsTime = datetime.datetime(2011, 11, 11, 5, 50, 0)
    vertTimes.append(obsTime)
    vertData.append(0.315)

    obsTime = datetime.datetime(2011, 11, 14, 6, 48, 0)
    vertTimes.append(obsTime)
    vertData.append(0.275)

    obsTime = datetime.datetime(2011, 12, 2, 9, 26, 0)
    vertTimes.append(obsTime)
    vertData.append(0.293)

    obsTime = datetime.datetime(2011, 12, 8, 13, 8, 0)
    vertTimes.append(obsTime)
    vertData.append(0.289)

    obsTime = datetime.datetime(2011, 12, 9, 13, 7, 0)
    vertTimes.append(obsTime)
    vertData.append(0.273)

    obsTime = datetime.datetime(2012, 1, 15, 0, 25, 0)
    vertTimes.append(obsTime)
    vertData.append(0.307)

    return

########################################################################
# Prepare data sets for plotting

def prepareData(biasData, biasTimes):

    lenMeanFilter = int(options.lenMean)

    # set up arrays for ZDR bias

    global btimes, vtimes
    btimes = np.array(biasTimes).astype(datetime.datetime)
    vtimes = np.array(vertTimes).astype(datetime.datetime)
    
    isRhi = np.array(biasData["IsRhi"]).astype(np.int)
    
    global validMean
    zdrMean = np.array(biasData["ZdrmInIceMean"]).astype(np.double)
    zdrMean = movingAverage(zdrMean, lenMeanFilter)
    validMean = np.isfinite(zdrMean)

    percVal = float(options.percentile)
    percStr = 'ZdrInIcePerc' + '{:05.2f}'.format(percVal)
    if (options.debug):
        print("=>> using: ", percStr, file=sys.stderr)

    biasIce = np.array(biasData[percStr]).astype(np.double)
    biasIce = movingAverage(biasIce, lenMeanFilter)
    validIce = np.isfinite(biasIce)
    
    percmStr = 'ZdrmInIcePerc' + '{:05.2f}'.format(percVal)
    if (options.debug):
        print("=>> using: ", percmStr, file=sys.stderr)
    biasIceM = np.array(biasData[percmStr]).astype(np.double)
    biasIceM = movingAverage(biasIceM, lenMeanFilter)
    validIceM = np.isfinite(biasIceM)
    
    if (options.rhiOnly):
        validMean = (np.isfinite(zdrMean) & (isRhi == 1))
        validIce = (np.isfinite(biasIce) & (isRhi == 1))
        validIceM = (np.isfinite(biasIceM) & (isRhi == 1))
    if (options.surOnly):
        validMean = (np.isfinite(zdrMean) & (isRhi == 0))
        validIce = (np.isfinite(biasIce) & (isRhi == 0))
        validIceM = (np.isfinite(biasIceM) & (isRhi == 0))

    global adjMean, validMeanBtimes, validMeanVals
    validMeanBtimes = btimes[validMean]
    validMeanVals = zdrMean[validMean]
    adjMean = np.array(validMeanVals).astype(float) + float(options.meanAdj)

    global validIceBtimes, validIceVals
    validIceBtimes = btimes[validIce]
    validIceVals = biasIce[validIce]

    global validIceMBtimes, validIceMVals
    validIceMBtimes = btimes[validIceM]
    validIceMVals = biasIceM[validIceM]

    # daily stats
    
    global dailyTimeMean, dailyValMean, dailyAdjMean
    (dailyTimeMean, dailyValMean) = computeDailyStats(validMeanBtimes, validMeanVals)
    dailyAdjMean = np.array(dailyValMean).astype(float) + float(options.meanAdj)

    global dailyTimeIce, dailyValIce
    (dailyTimeIce, dailyValIce) = computeDailyStats(validIceBtimes, validIceVals)

    global dailyTimeIceM, dailyValIceM
    (dailyTimeIceM, dailyValIceM) = computeDailyStats(validIceMBtimes, validIceMVals)

########################################################################
# Plot

def doPlot():

    fileName = options.biasFilePath
    titleStr = "File: " + fileName
    hfmt = dates.DateFormatter('%y/%m/%d')

    percVal = float(options.percentile)
    percStr = '{:g}'.format(percVal) + 'th%'

    # set up plots

    widthIn = float(options.figWidthMm) / 25.4
    htIn = float(options.figHeightMm) / 25.4

    fig1 = plt.figure(1, (widthIn, htIn))
    fig1.suptitle(options.title, fontsize=18)

    ax1a = fig1.add_subplot(2,1,1,xmargin=0.0)
    ax1b = fig1.add_subplot(2,1,2,xmargin=0.0)

    oneDay = datetime.timedelta(1.0)
    ax1a.set_xlim([btimes[0] - oneDay, btimes[-1] + oneDay])
    ax1a.set_title("ZDR bias, compared with VERT (dB)")
    ax1b.set_xlim([btimes[0] - oneDay, btimes[-1] + oneDay])
    ax1b.set_title("Daily ZDR bias, compared with VERT (dB)")

    # volume by volume

    if (options.plotMean):
        ax1a.plot(validMeanBtimes, adjMean,
                  "o", label = 'Measured ZDR Mean + ' + options.meanAdj,
                  color='lightblue')
    else:
        ax1a.plot(validIceBtimes, validIceVals, \
                  "o", label = 'Corrected ZDR Bias', color='red')
    #ax1a.plot(validIceBtimes, validIceVals, \
    #          label = 'ZDR Bias In Ice', linewidth=1, color='red')

    ax1a.plot(validIceMBtimes, validIceMVals, \
              "o", label = 'Measured ZDR Bias ' + percStr, color='blue')
    #ax1a.plot(validIceMBtimes, validIceMVals, \
    #          label = 'ZDRM Bias In Ice', linewidth=1, color='blue')
    
    ax1a.plot(vtimes, vertData, \
              "^", label = 'Vert Bias', linewidth=1, color='yellow', markersize=10)

    # daily

    if (options.plotMean):
        ax1b.plot(dailyTimeMean, dailyAdjMean,
                  label = 'Meas ZDR Mean + ' + options.meanAdj, 
                  linewidth=1, color='lightblue')
        ax1b.plot(dailyTimeMean, dailyAdjMean,
                  "^", label = 'Meas ZDR Mean + ' + options.meanAdj,
                  color='lightblue', markersize=10)
    else:
        ax1b.plot(dailyTimeIce, dailyValIce, \
                  label = 'Corrected ZDR Bias', linewidth=1, color='red')
        ax1b.plot(dailyTimeIce, dailyValIce, \
                  "^", label = 'Corrected ZDR Bias', color='red', markersize=10)

    ax1b.plot(dailyTimeIceM, dailyValIceM, \
              label = 'Meas Daily ZDR Bias ' + percStr, linewidth=1, color='blue')
    ax1b.plot(dailyTimeIceM, dailyValIceM, \
              "^", label = 'Meas Daily ZDR Bias ' + percStr, color='blue', markersize=10)

    #ax1b.plot(vtimes, vertData, \
    #          label = 'Vert Bias', linewidth=1, color='yellow')
    ax1b.plot(vtimes, vertData, \
              "^", label = 'Vert Results', linewidth=1, color='yellow', markersize=10)

    configDateAxis(ax1a, -0.3, 0.7, "ZDR Bias (dB)", 'upper right')
    configDateAxis(ax1b, -0.3, 0.7, "ZDR Bias (dB)", 'upper right')

    fig1.autofmt_xdate()
    fig1.tight_layout()
    fig1.subplots_adjust(bottom=0.10, left=0.10, right=0.95, top=0.9)
    plt.show()

########################################################################
# initialize legends etc

def configDateAxis(ax, miny, maxy, ylabel, legendLoc):
    
    legend = ax.legend(loc=legendLoc, ncol=3)
    for label in legend.get_texts():
        label.set_fontsize('x-small')
    ax.set_xlabel("Date")
    ax.set_ylabel(ylabel)
    ax.grid(True)
    if (miny > -9990 and maxy > -9990):
        ax.set_ylim([miny, maxy])
    hfmt = dates.DateFormatter('%Y/%m/%d')
    ax.xaxis.set_major_locator(dates.AutoDateLocator())
    ax.xaxis.set_major_formatter(hfmt)
    for tick in ax.xaxis.get_major_ticks():
        tick.label.set_fontsize(8) 

########################################################################
# compute daily stats for a variable

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
        if (count > 5):
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

