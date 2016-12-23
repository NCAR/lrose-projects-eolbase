#!/usr/bin/env python

#===========================================================================
#
# Produce plots for cov_to_mom output
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
    parser.add_option('--c2m_file',
                      dest='c2mFilePath',
                      default='../data/pecan/cov_to_mom.spol.qc.txt',
                      help='File path for bias results')
    parser.add_option('--cp_file',
                      dest='cpFilePath',
                      default='../data/pecan/cp_analysis.spol.txt',
                      help='CP results file path')
    parser.add_option('--title',
                      dest='title',
                      default='COV_TO_MOM status',
                      help='Title for plot')
    parser.add_option('--width',
                      dest='figWidthMm',
                      default=400,
                      help='Width of figure in mm')
    parser.add_option('--height',
                      dest='figHeightMm',
                      default=250,
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
        print >>sys.stderr, "  c2mFilePath: ", options.c2mFilePath
        print >>sys.stderr, "  cpFilePath: ", options.cpFilePath
        print >>sys.stderr, "  startTime: ", startTime
        print >>sys.stderr, "  endTime: ", endTime

    # read in column headers for c2m results

    iret, c2mHdrs, c2mData = readColumnHeaders(options.c2mFilePath)
    if (iret != 0):
        sys.exit(-1)

    # read in data for c2m results

    c2mData, c2mTimes = readInputData(options.c2mFilePath, c2mHdrs, c2mData)

    # read in column headers for CP results

    iret, cpHdrs, cpData = readColumnHeaders(options.cpFilePath)
    if (iret != 0):
        sys.exit(-1)

    # read in data for CP results

    cpData, cpTimes = readInputData(options.cpFilePath, cpHdrs, cpData)

    # render the plot
    
    doPlot(c2mData, c2mTimes, cpData, cpTimes)

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
        if (len(data) == len(colHeaders)):
            for index, var in enumerate(colHeaders, start=0):
                if (var == 'count' or var == 'year' \
                    or var == 'month' or var == 'day' or \
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

def doPlot(c2mData, c2mTimes, cpData, cpTimes):

    fileName = options.c2mFilePath
    titleStr = "File: " + fileName
    hfmt = dates.DateFormatter('%y/%m/%d')

    lenMeanFilter = int(options.lenMean)

    # set up arrays for c2m

    c2mtimes = np.array(c2mTimes).astype(datetime.datetime)
    
    noiseHc = np.array(c2mData["meanNoiseDbmHc"]).astype(np.double)
    noiseHc = movingAverage(noiseHc, lenMeanFilter)
    noiseHcValid = np.isfinite(noiseHc)
    
    noiseVc = np.array(c2mData["meanNoiseDbmVc"]).astype(np.double)
    noiseVc = movingAverage(noiseVc, lenMeanFilter)
    noiseVcValid = np.isfinite(noiseVc)
    
    noiseHx = np.array(c2mData["meanNoiseDbmHx"]).astype(np.double)
    noiseHx = movingAverage(noiseHx, lenMeanFilter)
    noiseHxValid = np.isfinite(noiseHx)
    
    noiseVx = np.array(c2mData["meanNoiseDbmVx"]).astype(np.double)
    noiseVx = movingAverage(noiseVx, lenMeanFilter)
    noiseVxValid = np.isfinite(noiseVx)
    
    validNoiseHcTimes = c2mtimes[noiseHcValid]
    validNoiseHcVals = noiseHc[noiseHcValid]
    
    validNoiseVcTimes = c2mtimes[noiseVcValid]
    validNoiseVcVals = noiseVc[noiseVcValid]
    
    validNoiseHxTimes = c2mtimes[noiseHxValid]
    validNoiseHxVals = noiseHx[noiseHxValid]
    
    validNoiseVxTimes = c2mtimes[noiseVxValid]
    validNoiseVxVals = noiseVx[noiseVxValid]
    
    # daily stats
    
    (dailyTimeNoiseHc, dailyValNoiseHc) = computeDailyStats(validNoiseHcTimes, validNoiseHcVals)
    (dailyTimeNoiseVc, dailyValNoiseVc) = computeDailyStats(validNoiseVcTimes, validNoiseVcVals)
    (dailyTimeNoiseHx, dailyValNoiseHx) = computeDailyStats(validNoiseHxTimes, validNoiseHxVals)
    (dailyTimeNoiseVx, dailyValNoiseVx) = computeDailyStats(validNoiseVxTimes, validNoiseVxVals)

    # site temp, vert pointing and sun scan results

    ctimes = np.array(cpTimes).astype(datetime.datetime)
    ZdrmVert = np.array(cpData["ZdrmVert"]).astype(np.double)
    validZdrmVert = np.isfinite(ZdrmVert)
    
    SunscanZdrm = np.array(cpData["SunscanZdrm"]).astype(np.double)
    validSunscanZdrm = np.isfinite(SunscanZdrm)

    cptimes = np.array(cpTimes).astype(datetime.datetime)
    tempSite = np.array(cpData["TempSite"]).astype(np.double)
    validTempSite = np.isfinite(tempSite)

    # set up plots

    widthIn = float(options.figWidthMm) / 25.4
    htIn = float(options.figHeightMm) / 25.4

    fig1 = plt.figure(1, (widthIn, htIn))

    ax1a = fig1.add_subplot(2,1,1,xmargin=0.0)
    ax1b = fig1.add_subplot(2,1,2,xmargin=0.0)
    #ax1c = fig1.add_subplot(3,1,3,xmargin=0.0)

    oneDay = datetime.timedelta(1.0)
    ax1a.set_xlim([c2mtimes[0] - oneDay, c2mtimes[-1] + oneDay])
    ax1a.set_title("Noise Hc and Vc (dBm)")
    ax1b.set_xlim([c2mtimes[0] - oneDay, c2mtimes[-1] + oneDay])
    ax1b.set_title("Daily noise (dBm)")
    #ax1c.set_xlim([c2mtimes[0] - oneDay, c2mtimes[-1] + oneDay])
    #ax1c.set_title("Site temperature (C)")
    
    ax1a.plot(validNoiseHcTimes, validNoiseHcVals, \
              "o", label = 'NoiseHc (dBm)', color='blue')
    
    ax1a.plot(validNoiseHcTimes, validNoiseHcVals, \
              label = 'NoiseHc', linewidth=1, color='blue')
    
    ax1a.plot(validNoiseVcTimes, validNoiseVcVals, \
              "o", label = 'NoiseVc (dBm)', color='red')
    
    ax1a.plot(validNoiseVcTimes, validNoiseVcVals, \
              label = 'NoiseVc', linewidth=1, color='red')
    
    #ax1a.plot(ctimes[validSunscanZdrm], SunscanZdrm[validSunscanZdrm], \
    #          linewidth=2, label = 'Zdrm Sun/CP (dB)', color = 'green')
    
    #ax1a.plot(ctimes[validZdrmVert], ZdrmVert[validZdrmVert], \
    #          "^", markersize=10, linewidth=1, label = 'Zdrm Vert (dB)', \
    #          color = 'orange')

    ax1b.plot(dailyTimeNoiseHc, dailyValNoiseHc, \
              label = 'NoiseHc Daily', linewidth=1, color='blue')
    ax1b.plot(dailyTimeNoiseHc, dailyValNoiseHc, \
              "^", label = 'NoiseHc Daily', color='blue', markersize=10)

    ax1b.plot(dailyTimeNoiseVc, dailyValNoiseVc, \
              label = 'NoiseVc Daily', linewidth=1, color='red')
    ax1b.plot(dailyTimeNoiseVc, dailyValNoiseVc, \
              "^", label = 'NoiseVc Daily', color='red', markersize=10)

    ax1b.plot(dailyTimeNoiseHx, dailyValNoiseHx, \
              label = 'NoiseHx Daily', linewidth=1, color='cyan')
    ax1b.plot(dailyTimeNoiseHx, dailyValNoiseHx, \
              "^", label = 'NoiseHx Daily', color='cyan', markersize=10)

    ax1b.plot(dailyTimeNoiseVx, dailyValNoiseVx, \
              label = 'NoiseVx Daily', linewidth=1, color='green')
    ax1b.plot(dailyTimeNoiseVx, dailyValNoiseVx, \
              "^", label = 'NoiseVx Daily', color='green', markersize=10)

    #ax1c.plot(cptimes[validTempSite], tempSite[validTempSite], \
    # linewidth=1, label = 'Site Temp', color = 'red')
    
    #configDateAxis(ax1a, -9999, 9999, "ZDR C2m (dB)", 'upper right')
    configDateAxis(ax1a, -9999, -9999, "Noise", 'upper right')
    configDateAxis(ax1b, -9999, -9999, "Daily noise (dBm)", 'lower right')
    #configDateAxis(ax1c, -9999, 9999, "Temp (C)", 'upper right')

    fig1.autofmt_xdate()
    fig1.tight_layout()
    fig1.subplots_adjust(bottom=0.03, left=0.06, right=0.97, top=0.97)
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

