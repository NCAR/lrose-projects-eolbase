#!/usr/bin/env python

#===========================================================================
#
# Produce plots for ZDR bias by volume - paper
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
                      default='../data/pecan/zdr_bias.kddc.txt',
                      help='File path for bias results')
    parser.add_option('--title',
                      dest='title',
                      default='ZDR BIAS FROM ICE AND BRAGG',
                      help='Title for plot')
    parser.add_option('--width',
                      dest='figWidthMm',
                      default=400,
                      help='Width of figure in mm')
    parser.add_option('--height',
                      dest='figHeightMm',
                      default=200,
                      help='Height of figure in mm')
    parser.add_option('--lenMean',
                      dest='lenMean',
                      default=1,
                      help='Len of moving mean filter')
    parser.add_option('--start',
                      dest='startTime',
                      default='2015 05 28 00 00 00',
                      help='Start time for XY plot')
    parser.add_option('--end',
                      dest='endTime',
                      default='2015 07 17 00 00 00',
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

    # prepare the data for plotting

    prepareData(biasData, biasTimes)

    # render the plot
    
    doPlot()

    # done

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
            print >>sys.stderr, "Reading file: ", filePath
            for icol, var in enumerate(colHeaders, start=0):
                print >>sys.stderr, "colHeader[", icol, "] = ", colHeaders[icol]
    else:
        print >>sys.stderr, "ERROR - readColumnHeaders"
        print >>sys.stderr, "  First line does not start with #"
        return -1, colHeaders, colData
    
    for icol, var in enumerate(colHeaders, start=0):
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
        if (len(data) != len(colHeaders)):
            if (options.debug == True):
                print >>sys.stderr, "skipping line: ", line
            continue;

        for index, var in enumerate(colHeaders, start=0):
            # print >>sys.stderr, "index, data[index]: ", index, ", ", data[index]
            if (var == 'count' or var == 'year' or var == 'month' or var == 'day' or \
                var == 'hour' or var == 'min' or var == 'sec' or \
                var == 'unix_time'):
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

    obsTimes = []
    for ii, var in enumerate(year, start=0):
        thisTime = datetime.datetime(year[ii], month[ii], day[ii],
                                     hour[ii], minute[ii], sec[ii])
        obsTimes.append(thisTime)

    if (options.verbose == True):
        print >>sys.stderr, "Read in file: ", filePath
        for itime, obsTime in enumerate(obsTimes, start=0):
            sys.stdout.write('===>> ')
            sys.stdout.write(str(obsTime))
            sys.stdout.write(': ')
            for icol, var in enumerate(colHeaders, start=0):
                sys.stdout.write(colHeaders[icol] + ':')
                sys.stdout.write(str(colData[var][itime]))
                sys.stdout.write('  ')
            sys.stdout.write('\n')

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
# Prepare data sets for plotting

def prepareData(biasData, biasTimes):

    lenMeanFilter = int(options.lenMean)

    # set up arrays for ZDR bias

    global btimes
    btimes = np.array(biasTimes).astype(datetime.datetime)
    
    biasIce = np.array(biasData["ZdrInIcePerc25.00"]).astype(np.double)
    biasIce = movingAverage(biasIce, lenMeanFilter)
    validIce = (np.isfinite(biasIce) & (btimes >= startTime) & (btimes <= endTime))
    
    biasBragg = np.array(biasData["ZdrInBraggPerc32.00"]).astype(np.double)
    biasBragg = movingAverage(biasBragg, lenMeanFilter)
    validBragg = (np.isfinite(biasBragg) & (btimes >= startTime) & (btimes <= endTime))

    validIce = np.isfinite(biasIce)
    validBragg = np.isfinite(biasBragg)

    global validIceBtimes, validIceVals
    validIceBtimes = btimes[validIce]
    validIceVals = biasIce[validIce]

    global validBraggBtimes, validBraggVals
    validBraggBtimes = btimes[validBragg]
    validBraggVals = biasBragg[validBragg]

    # load up receiver gain etc - axis 4
    
    (dailyTimeIce, dailyValIce) = computeDailyStats(validIceBtimes, validIceVals)
    (dailyTimeBragg, dailyValBragg) = computeDailyStats(validBraggBtimes, validBraggVals)

    # site temp

    global tempSite, validTempSite
    tempSite = np.array(biasData["TempSite"]).astype(np.double)
    validTempSite = np.isfinite(tempSite)
    
    # ZDR bias vs temp

    global tempTimes, tempIceVals, tempIceBias
    tempTimes = []
    tempIceVals = []
    tempIceBias = []

    for ii, biasVal in enumerate(validIceVals, start=0):
        btime = validIceBtimes[ii]
        tempTime, tempVal = getClosestTemp(btime, btimes, tempSite)
        tempTimes.append(tempTime)
        tempIceVals.append(tempVal)
        tempIceBias.append(biasVal)
        if (options.verbose):
            print >>sys.stderr, "==>> biasTime, biasVal, tempTime, tempVal:", \
                btime, biasVal, tempTime, tempVal

    global tempMean, tempSdev, tempNorm
    tempMean = np.mean(tempSite)
    tempSdev = np.std(tempSite)
    if (options.debug):
        print >>sys.stderr, "==>> tempMean, tempSdev: ", tempMean, tempSdev
    tempNorm = (tempSite - tempMean) / (tempSdev * 10.0)

    # linear regression for bias vs temp
    # obtain the fit, ww[0] is slope, ww[1] is intercept

    global AA, ww, tempRegrX, tempRegrY, minTemp, maxTemp

    AA = array([tempIceVals, ones(len(tempIceVals))])
    ww = linalg.lstsq(AA.T, tempIceBias)[0]
    minTemp = min(tempIceVals)
    maxTemp = max(tempIceVals)

    tempRegrX = []
    tempRegrY = []
    tempRegrX.append(minTemp)
    tempRegrX.append(maxTemp)
    tempRegrY.append(ww[0] * minTemp + ww[1])
    tempRegrY.append(ww[0] * maxTemp + ww[1])

    # correct bias for linear regression

    slope = ww[0]
    intercept = ww[1]

    global tempCorrBias
    tempCorrBias = []
    for ii, rtime in enumerate(tempTimes, start=0):
        tempC = tempIceVals[ii]
        biasDb = tempIceBias[ii]
        tempCorr = intercept + tempC * slope
        corrBias = biasDb - tempCorr
        tempCorrBias.append(corrBias)

########################################################################
# Plot

def doPlot():

    fileName = options.biasFilePath
    titleStr = "File: " + fileName
    hfmt = dates.DateFormatter('%y/%m/%d')

    lenMeanFilter = int(options.lenMean)

    # set up plots
    
    widthIn = float(options.figWidthMm) / 25.4
    htIn = float(options.figHeightMm) / 25.4
    
    fig1 = plt.figure(1, (widthIn, htIn))
    ax1a = fig1.add_subplot(1,1,1,xmargin=0.0)

    fig2 = plt.figure(2, (widthIn/2, htIn))
    ax2a = fig2.add_subplot(1,1,1,xmargin=1.0, ymargin=1.0)

    oneDay = datetime.timedelta(1.0)
    timeRange = endTime - startTime
    timeRangeMargin = timeRange / 50
    #ax1a.set_xlim(startTime - timeRangeMargin, endTime + timeRangeMargin)
    ax1a.set_xlim(startTime - oneDay, endTime + oneDay)
    title = "KDDC ZDR bias in ice and Bragg"
    ax1a.set_title(title)

    ax1a.plot(validBraggBtimes, validBraggVals, \
              "o", label = 'ZDR Bias In Bragg', color='blue')
    #ax1a.plot(validBraggBtimes, validBraggVals, \
    #          label = 'ZDR Bias In Bragg', linewidth=1, color='blue')
    
    ax1a.plot(validIceBtimes, validIceVals, \
              "o", label = 'ZDR Bias In Ice', color='green')
    #ax1a.plot(validIceBtimes, validIceVals, \
    #          label = 'ZDR Bias In Ice', linewidth=1, color='green')
    
    #ax1a.plot(tempTimes, tempNorm, \
    #          label = 'Norm-temps', color='orange', linewidth=1)
    ax1a.plot(btimes, tempNorm, \
              label = 'Norm-temps', color='orange', linewidth=1)
    
    configDateAxis(ax1a, -9999, 9999, "ZDR Bias (dB)", 'upper right')

    # ZDR vs temp

    label2a = "KDDC ZDR Bias In Ice = " + ("%.5f" % ww[0]) + " * temp + " + ("%.3f" % ww[1])
    ax2a.plot(tempIceVals, tempIceBias, 
              "x", label = label2a, color = 'blue')
    ax2a.plot(tempRegrX, tempRegrY, linewidth=3, color = 'blue')
    
    legend2a = ax2a.legend(loc="upper left", ncol=4)
    for label2a in legend2a.get_texts():
        label2a.set_fontsize(12)
        ax2a.set_xlabel("Site temperature (C)")
        ax2a.set_ylabel("ZDR Bias (dB)")
        ax2a.grid(True)
        ax2a.set_ylim([-0.5, 0.5])
        ax2a.set_xlim([minTemp - 1, maxTemp + 1])
        title2a = "KDDC ZDR Bias In Ice Vs Temp\n" + str(startTime) + " - " + str(endTime)
        #title2a = "KDDC ZDR Bias In Ice Vs Temp"
        ax2a.set_title(title2a)

    fig1.autofmt_xdate()
    fig1.tight_layout()
    fig1.subplots_adjust(bottom=0.08, left=0.06, right=0.97, top=0.96)
    plt.show()

########################################################################
# initialize legends etc

def configDateAxis(ax, miny, maxy, ylabel, legendLoc):
    
    legend = ax.legend(loc=legendLoc, ncol=4)
    for label in legend.get_texts():
        label.set_fontsize('x-small')
    ax.set_xlabel("Date")
    ax.set_ylabel(ylabel)
    ax.grid(True)
    if (miny > -9990 and maxy > -9990):
        ax.set_ylim([miny, maxy])
    hfmt = dates.DateFormatter('%y/%m/%d')
    #hfmt = dates.DateFormatter('%y/%m/%d-%H:%M:%S')
    ax.xaxis.set_major_locator(dates.DayLocator())
    #ax.xaxis.set_major_locator(dates.HourLocator())
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

    minDeltaTime = 1.0e99
    ttime = searchTimes[0]
    temp = searchTemps[0]
    for ii, temptime in enumerate(searchTimes, start=0):
        if (np.isfinite(searchTemps[ii])):
            ttemp = searchTemps[ii]
            deltaTime = math.fabs((temptime - biasTime).total_seconds())
            if (deltaTime < minDeltaTime):
                minDeltaTime = deltaTime
                temp = ttemp
                ttime = temptime

    return (ttime, temp)

########################################################################
# get tx power ratio closest in time to the search time

def getClosestRatio(biasTime, powerTimes, obsTemps, txPwrH, txPwrV):

    twoHours = datetime.timedelta(0.0, 7200.0)

    validTimes = ((powerTimes > (biasTime - twoHours)) & \
                  (powerTimes < (biasTime + twoHours)))
    
    if (len(validTimes) < 1):
        return (biasTime, float('NaN'))
    
    searchTimes = powerTimes[validTimes]
    searchTemps = obsTemps[validTimes]
    searchTxPwrH = txPwrH[validTimes]
    searchTxPwrV = txPwrV[validTimes]

    if (len(searchTimes) < 1 or len(searchTxPwrH) < 1):
        return (biasTime, float('NaN'))

    minDeltaTime = 1.0e99
    rtime = searchTimes[0]
    ratio = searchTxPwrH[0] - searchTxPwrV[0]
    temp = searchTemps[0]
    for ii, pwrtime in enumerate(searchTimes, start=0):
        if (np.isfinite(searchTemps[ii]) &
            np.isfinite(searchTxPwrH[ii]) &
            np.isfinite(searchTxPwrV[ii])):
            ttemp = searchTemps[ii]
            tratio = searchTxPwrH[ii] - searchTxPwrV[ii]
            deltaTime = math.fabs((pwrtime - biasTime).total_seconds())
            if (deltaTime < minDeltaTime):
                minDeltaTime = deltaTime
                ratio = tratio
                rtime = pwrtime
                temp = ttemp

    return (rtime, temp, ratio)

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

    if (len(nptimes) < 1):
        return (dailyTimes, dailyMeans)
    
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

