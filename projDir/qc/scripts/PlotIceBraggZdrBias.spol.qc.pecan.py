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
                      default='../data/pecan/zdr_bias.spol.qc.txt',
                      help='File path for bias results')
    parser.add_option('--cp_file',
                      dest='cpFilePath',
                      default='../data/pecan/spol_pecan_CP_analysis_20150528_000553.txt',
                      help='CP results file path')
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
                      default='1970 01 01 00 00 00',
                      help='Start time for XY plot')
    parser.add_option('--end',
                      dest='endTime',
                      default='1970 01 01 01 00 00',
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
        print >>sys.stderr, "  cpFilePath: ", options.cpFilePath
        print >>sys.stderr, "  biasFilePath: ", options.biasFilePath
        print >>sys.stderr, "  startTime: ", startTime
        print >>sys.stderr, "  endTime: ", endTime

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
# Plot

def doPlot(biasData, biasTimes, cpData, cpTimes):

    fileName = options.biasFilePath
    titleStr = "File: " + fileName
    hfmt = dates.DateFormatter('%y/%m/%d')

    lenMeanFilter = int(options.lenMean)

    # set up arrays for ZDR bias

    btimes = np.array(biasTimes).astype(datetime.datetime)
    
    # biasIce = np.array(biasData["ZdrInIceMean"]).astype(np.double)
    # biasIce = movingAverage(biasIce, lenMeanFilter)

    biasIce = np.array(biasData["ZdrInIcePerc25.00"]).astype(np.double)
    biasIce = movingAverage(biasIce, lenMeanFilter)
    validIce = np.isfinite(biasIce)
    
    biasIceM = np.array(biasData["ZdrmInIcePerc25.00"]).astype(np.double)
    biasIceM = movingAverage(biasIceM, lenMeanFilter)
    validIceM = np.isfinite(biasIceM)
    
    # biasBragg = np.array(biasData["ZdrInBraggMean"]).astype(np.double)
    # biasBragg = movingAverage(biasBragg, lenMeanFilter)

    biasBragg = np.array(biasData["ZdrInBraggPerc32.00"]).astype(np.double)
    biasBragg = movingAverage(biasBragg, lenMeanFilter)
    validBragg = np.isfinite(biasBragg)

    biasBraggM = np.array(biasData["ZdrmInBraggPerc25.00"]).astype(np.double)
    biasBraggM = movingAverage(biasBraggM, lenMeanFilter)
    validBraggM = np.isfinite(biasBraggM)
    
    validIceBtimes = btimes[validIce]
    validIceVals = biasIce[validIce]
    
    validIceMBtimes = btimes[validIceM]
    validIceMVals = biasIce[validIceM]
    
    validBraggBtimes = btimes[validBragg]
    validBraggVals = biasBragg[validBragg]
    
    validBraggMBtimes = btimes[validBraggM]
    validBraggMVals = biasBragg[validBraggM]
    
    # load up receiver gain etc - axis 4
    
    (dailyTimeIce, dailyValIce) = computeDailyStats(validIceBtimes, validIceVals)
    (dailyTimeBragg, dailyValBragg) = computeDailyStats(validBraggBtimes, validBraggVals)

    (dailyTimeIceM, dailyValIceM) = computeDailyStats(validIceMBtimes, validIceMVals)
    (dailyTimeBraggM, dailyValBraggM) = computeDailyStats(validBraggMBtimes, validBraggMVals)

    # site temp, vert pointing and sun scan results

    ctimes = np.array(cpTimes).astype(datetime.datetime)
    ZdrmVert = np.array(cpData["ZdrmVert"]).astype(np.double)
    validZdrmVert = np.isfinite(ZdrmVert)
    
    SunscanZdrm = np.array(cpData["SunscanZdrm"]).astype(np.double)
    validSunscanZdrm = np.isfinite(SunscanZdrm)

    cptimes = np.array(cpTimes).astype(datetime.datetime)
    tempSite = np.array(cpData["TempSite"]).astype(np.double)
    validTempSite = np.isfinite(tempSite)

    tempIceVals = []
    biasIceVals = []

    for ii, biasVal in enumerate(validIceVals, start=0):
        btime = validIceBtimes[ii]
        if (btime >= startTime and btime <= endTime):
            tempTime, tempVal = getClosestTemp(btime, cptimes, tempSite)
            if (np.isfinite(tempVal)):
                tempIceVals.append(tempVal)
                biasIceVals.append(biasVal)
                if (options.verbose):
                    print >>sys.stderr, "==>> biasTime, biasVal, tempTime, tempVal:", \
                        btime, biasVal, tempTime, tempVal

    # linear regression for bias vs temp

    A = array([tempIceVals, ones(len(tempIceVals))])

    if (len(tempIceVals) > 1):
        # obtain the fit, ww[0] is slope, ww[1] is intercept
        ww = linalg.lstsq(A.T, biasIceVals)[0]
        minTemp = min(tempIceVals)
        maxTemp = max(tempIceVals)
        haveTemps = True
    else:
        ww = (1.0, 0.0)
        minTemp = 0.0
        maxTemp = 40.0
        haveTemps = False
        print >>sys.stderr, "NOTE - no valid temp vs ZDR data for period"
        print >>sys.stderr, "  startTime: ", startTime
        print >>sys.stderr, "  endTime  : ", endTime
        
    regrX = []
    regrY = []
    regrX.append(minTemp)
    regrX.append(maxTemp)
    regrY.append(ww[0] * minTemp + ww[1])
    regrY.append(ww[0] * maxTemp + ww[1])
    
    # set up plots

    widthIn = float(options.figWidthMm) / 25.4
    htIn = float(options.figHeightMm) / 25.4

    fig1 = plt.figure(1, (widthIn, htIn))

    ax1a = fig1.add_subplot(2,1,1,xmargin=0.0)
    ax1b = fig1.add_subplot(2,1,2,xmargin=0.0)
    #ax1c = fig1.add_subplot(3,1,3,xmargin=0.0)

    if (haveTemps):
        fig2 = plt.figure(2, (widthIn/2, htIn/2))
        ax2a = fig2.add_subplot(1,1,1,xmargin=1.0, ymargin=1.0)

    oneDay = datetime.timedelta(1.0)
    ax1a.set_xlim([btimes[0] - oneDay, btimes[-1] + oneDay])
    ax1a.set_title("Residual ZDR bias in ice and Bragg, compared with VERT and CP results (dB)")
    ax1b.set_xlim([btimes[0] - oneDay, btimes[-1] + oneDay])
    ax1b.set_title("Daily mean ZDR bias in ice and Bragg (dB)")
    #ax1c.set_xlim([btimes[0] - oneDay, btimes[-1] + oneDay])
    #ax1c.set_title("Site temperature (C)")

    ax1a.plot(validBraggBtimes, validBraggVals, \
              "o", label = 'ZDR Bias In Bragg', color='blue')
    ax1a.plot(validBraggBtimes, validBraggVals, \
              label = 'ZDR Bias In Bragg', linewidth=1, color='blue')
    
    ax1a.plot(validIceBtimes, validIceVals, \
              "o", label = 'ZDR Bias In Ice', color='red')
    ax1a.plot(validIceBtimes, validIceVals, \
              label = 'ZDR Bias In Ice', linewidth=1, color='red')

    ax1a.plot(validBraggMBtimes, validBraggMVals, \
              "o", label = 'ZDRM Bias In Bragg', color='blue')
    ax1a.plot(validBraggMBtimes, validBraggMVals, \
              label = 'ZDRM Bias In Bragg', linewidth=1, color='blue')
    
    ax1a.plot(validIceMBtimes, validIceMVals, \
              "o", label = 'ZDRM Bias In Ice', color='red')
    ax1a.plot(validIceMBtimes, validIceMVals, \
              label = 'ZDRM Bias In Ice', linewidth=1, color='red')
    
    #ax1a.plot(ctimes[validSunscanZdrm], SunscanZdrm[validSunscanZdrm], \
    #          linewidth=2, label = 'Zdrm Sun/CP (dB)', color = 'green')
    
    #ax1a.plot(ctimes[validZdrmVert], ZdrmVert[validZdrmVert], \
    #          "^", markersize=10, linewidth=1, label = 'Zdrm Vert (dB)', color = 'orange')

    ax1b.plot(dailyTimeBragg, dailyValBragg, \
              label = 'Daily Bias Bragg', linewidth=1, color='blue')
    ax1b.plot(dailyTimeBragg, dailyValBragg, \
              "^", label = 'Daily Bias Bragg', color='blue', markersize=10)

    ax1b.plot(dailyTimeIce, dailyValIce, \
              label = 'Daily Bias Ice', linewidth=1, color='red')
    ax1b.plot(dailyTimeIce, dailyValIce, \
              "^", label = 'Daily Bias Ice', color='red', markersize=10)

    #ax1c.plot(cptimes[validTempSite], tempSite[validTempSite], \
    #          linewidth=1, label = 'Site Temp', color = 'blue')
    
    #configDateAxis(ax1a, -9999, 9999, "ZDR Bias (dB)", 'upper right')
    configDateAxis(ax1a, -0.3, 0.7, "ZDR Bias (dB)", 'upper right')
    configDateAxis(ax1b, -0.5, 0.5, "ZDR Bias (dB)", 'upper right')
    #configDateAxis(ax1c, -9999, 9999, "Temp (C)", 'upper right')

    if (haveTemps):
        label3 = "ZDR Bias In Ice = " + ("%.5f" % ww[0]) + " * temp + " + ("%.3f" % ww[1])
        ax2a.plot(tempIceVals, biasIceVals, 
                 "x", label = label3, color = 'blue')
        ax2a.plot(regrX, regrY, linewidth=3, color = 'blue')
    
        legend3 = ax2a.legend(loc="upper left", ncol=2)
        for label3 in legend3.get_texts():
            label3.set_fontsize(12)
            ax2a.set_xlabel("Site temperature (C)")
            ax2a.set_ylabel("ZDR Bias (dB)")
            ax2a.grid(True)
            ax2a.set_ylim([-0.5, 0.5])
            ax2a.set_xlim([minTemp - 1, maxTemp + 1])
            title3 = "ZDR Bias In Ice Vs Temp: " + str(startTime) + " - " + str(endTime)
            ax2a.set_title(title3)

    fig1.autofmt_xdate()
    fig1.tight_layout()
    fig1.subplots_adjust(bottom=0.08, left=0.06, right=0.97, top=0.96)
    plt.show()

########################################################################
# initialize legends etc

def configDateAxis(ax, miny, maxy, ylabel, legendLoc):
    
    legend = ax.legend(loc=legendLoc, ncol=5)
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

