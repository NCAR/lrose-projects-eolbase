#!/usr/bin/env python

#===========================================================================
#
# Produce plots for ZDR stats by volume
#
#===========================================================================

from __future__ import print_function

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

    usage = "usage: " + __file__ + " [options]"
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
                      default='/home/mdtest/git/lrose-projects-eolbase/projDir/qc/data/pecan/spol_pecan_CP_analysis_20150524_000021.txt',
                      help='CP results file path')
    parser.add_option('--stats_file',
                      dest='statsFilePath',
                      default='/home/mdtest/data/PidZdrStats/pecan_sur/zdr_stats_table.txt',
                      help='File path for stats results')
    parser.add_option('--percentile',
                      dest='percentile',
                      default=50.0,
                      help='Percentile to use for plotting')
    parser.add_option('--title',
                      dest='title',
                      default='ZDR STATS',
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
                      default='2015 06 15 00 00 00',
                      help='Start time for XY plot')
    parser.add_option('--end',
                      dest='endTime',
                      default='2015 07 17 00 00 00',
                      help='End time for XY plot')
    parser.add_option('--scanMode',
                      dest='scanMode',
                      default='both',
                      help='Scan mode: sur, rhi or both')
    parser.add_option('--setZdrRange',
                      dest='setZdrRange', default=False,
                      action="store_true",
                      help= \
                      'Set the ZDR range to plot from minZdr to maxZdr. ' + \
                      'If false, plot all data')
    parser.add_option('--minZdr',
                      dest='minZdr',
                      default='-1.0',
                      help='Min val on ZDR data axis')
    parser.add_option('--maxZdr',
                      dest='maxZdr',
                      default='1.0',
                      help='Max val on ZDR axis')
    parser.add_option('--normalize',
                      dest='normalize', default=False,
                      action="store_true",
                      help='Normalize stats before plotting')
    
    (options, args) = parser.parse_args()
    
    if (options.verbose):
        options.debug = True

    year, month, day, hour, minute, sec = options.startTime.split()
    startTime = datetime.datetime(int(year), int(month), int(day),
                                  int(hour), int(minute), int(sec))

    year, month, day, hour, minute, sec = options.endTime.split()
    endTime = datetime.datetime(int(year), int(month), int(day),
                                int(hour), int(minute), int(sec))

    if (options.debug):
        print("Running ", __file__, file=sys.stderr)
        print("  cpFilePath: ", options.cpFilePath, file=sys.stderr)
        print("  statsFilePath: ", options.statsFilePath, file=sys.stderr)
        print("  startTime: ", startTime, file=sys.stderr)
        print("  endTime: ", endTime, file=sys.stderr)
        print("  scanMode: ", options.scanMode, file=sys.stderr)
        
    if (options.scanMode != 'both' and \
        options.scanMode != 'sur' and \
        options.scanMode != 'rhi'):
        print("ERROR - scan mode: ", options.scanMode, file=sys.stderr)
        print("  Must be: sur, rhi or both", file=sys.stderr)
        sys.exit(-1)

    # read in column headers for stats results

    iret, statsHdrs, statsData = readColumnHeaders(options.statsFilePath)
    if (iret != 0):
        sys.exit(-1)

    # read in data for stats results

    statsData, statsTimes = readInputData(options.statsFilePath, statsHdrs, statsData)

    # read in column headers for CP results

    iret, cpHdrs, cpData = readColumnHeaders(options.cpFilePath)
    if (iret != 0):
        sys.exit(-1)

    # read in data for CP results

    cpData, cpTimes = readInputData(options.cpFilePath, cpHdrs, cpData)

    # render the plot
    
    doPlot(statsData, statsTimes, cpData, cpTimes)

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

        # check scan mode
        
        process = False
        rhiFlag = 0
        for index, var in enumerate(colHeaders, start=0):
            if (var == 'IsRhi'):
                rhiFlag = int(data[index])
                break
        if (options.scanMode == 'both'):
            process = True
        elif (options.scanMode == 'sur' and rhiFlag == 0):
            process = True
        elif (options.scanMode == 'rhi' and rhiFlag == 1):
            process = True

        if (process == False):
            continue

        for index, var in enumerate(colHeaders, start=0):
            if (var == 'count' or var == 'year' or var == 'month' or var == 'day' or \
                var == 'hour' or var == 'min' or var == 'sec' or \
                var == 'unix_time'):
                colData[var].append(int(data[index]))
            elif (var == 'PidLabel' or var == 'TempTime' or \
                  var == 'HistCounts' or var == 'HistX'):
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

def doPlot(statsData, statsTimes, cpData, cpTimes):

    fileName = options.statsFilePath
    titleStr = "File: " + fileName
    hfmt = dates.DateFormatter('%y/%m/%d')
    label = statsData["PidLabel"][0]

    lenMeanFilter = int(options.lenMean)

    #   set up np arrays

    stimes = np.array(statsTimes).astype(datetime.datetime)

    statsMean = np.array(statsData["ZdrmMean"]).astype(np.double)
    statsMean = movingAverage(statsMean, lenMeanFilter)

    statsSdev = np.array(statsData["ZdrmSdev"]).astype(np.double)
    statsSdev = movingAverage(statsSdev, lenMeanFilter)

    meanMinusSdev = statsMean - 0.3 * statsSdev

    perc = np.array(computePercentile(statsData, float(options.percentile))).astype(np.double)
    if (options.normalize):
        perc = (perc - statsMean) / statsSdev

    histMedian = np.array(statsData["HistMedian"]).astype(np.double)
    histMedian = movingAverage(histMedian, lenMeanFilter)

    tempSite = np.array(statsData["TempSite"]).astype(np.double)
    tempSite = movingAverage(tempSite, lenMeanFilter)

    validMean = np.isfinite(statsMean)
    validSdev = np.isfinite(statsSdev)
    validTempSite = np.isfinite(tempSite)

    ctimes = np.array(cpTimes).astype(datetime.datetime)
    ZdrmVert = np.array(cpData["ZdrmVert"]).astype(np.double)
    validZdrmVert = np.isfinite(ZdrmVert)
    
    SunscanZdrm = np.array(cpData["SunscanZdrm"]).astype(np.double)
    validSunscanZdrm = np.isfinite(SunscanZdrm)

    validStimes = stimes[validMean]
    validStats = statsMean[validMean]
    
    tempVals = []
    statsVals = []

    for ii, statsVal in enumerate(perc, start=0):
        stime = validStimes[ii]
        tempVal = tempSite[ii]
        if (stime >= startTime and stime <= endTime):
            tempVals.append(tempVal)
            statsVals.append(statsVal)

    # linear regression stats vs temp

    A = array([tempVals, ones(len(tempVals))])
    ww = linalg.lstsq(A.T, statsVals)[0] # obtaining the fit, ww[0] is slope, ww[1] is intercept
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
    fig2 = plt.figure(2, (widthIn/2, htIn))

    ax1 = fig1.add_subplot(1,1,1,xmargin=0.0)
    ax2 = fig2.add_subplot(1,1,1,xmargin=1.0, ymargin=1.0)

    oneDay = datetime.timedelta(1.0)
    ax1.set_xlim([stimes[0] - oneDay, stimes[-1] + oneDay])
    ax1.set_title("ZDR by volume in " + label + ", compared with VERT and CP results")

    #ax1.plot(stimes[validMean], statsSdev[validMean], \
    #         "go", label = 'ZDR-sdev')

    ax1.plot(stimes[validMean], statsMean[validMean], \
             "ro", label = 'ZDR-mean', linewidth=1)

    ax1.plot(stimes[validMean], perc[validMean], \
             "bo", label = 'ZDR-percentile-' + str(options.percentile))
    
    #ax1.plot(stimes[validMean], meanMinusSdev[validMean], \
    #         "yo", label = 'ZDR Mean-Sdev')

    #ax1.plot(stimes[validMean], histMedian[validMean], \
    #         "yo", label = 'ZDR Hist-Median')

    ax1.plot(ctimes[validSunscanZdrm], SunscanZdrm[validSunscanZdrm], \
             linewidth=2, label = 'Zdrm Sun/CP (dB)', color = 'green')
    
    ax1.plot(ctimes[validZdrmVert], ZdrmVert[validZdrmVert], \
             "^", markersize=10, linewidth=1, label = 'Zdrm Vert (dB)', color = 'yellow')

    if (options.setZdrRange):
        configDateAxis(ax1, float(options.minZdr), float(options.maxZdr),
                       "ZDR Stats (dB)", 'upper right')
    else:
        configDateAxis(ax1, -9999, 9999, "ZDR Stats (dB)", 'upper right')

    #axt = fig1.add_subplot(2,1,2,xmargin=0.0)
    #axt.set_xlim([stimes[0] - oneDay, stimes[-1] + oneDay])
    #axt.set_title("Site temperature (C)")
    #axt.plot(stimes[validTempSite], tempSite[validTempSite], \
    #         linewidth=1, label = 'Site Temp', color = 'blue')
    #configDateAxis(axt, -9999, 9999, "Temp (C)", 'upper right')

    label2 = "ZDR = " + ("%.5f" % ww[0]) + " * temp + " + ("%.3f" % ww[1])
    ax2.plot(tempVals, statsVals, 
             "x", label = label2, color = 'blue')
    ax2.plot(regrX, regrY, linewidth=3, color = 'cyan')
    
    legend2 = ax2.legend(loc="upper left", ncol=2)
    for label2 in legend2.get_texts():
        label2.set_fontsize(12)
    ax2.set_xlabel("Site temperature (C)")
    ax2.set_ylabel("ZDR Stats (dB)")
    ax2.grid(True)
    if (options.setZdrRange):
        ax2.set_ylim([float(options.minZdr), float(options.maxZdr)])
    ax2.set_xlim([minTemp - 1, maxTemp + 1])
    title2 = "ZDR vs. Temp in " + label + ": " + str(startTime) + " - " + str(endTime)
    ax2.set_title(title2)

    fig1.autofmt_xdate()
    fig1.tight_layout()
    fig1.subplots_adjust(bottom=0.10, left=0.06, right=0.97, top=0.97)

    fig2.tight_layout()
    fig2.subplots_adjust(bottom=0.15, left=0.1, right=0.95, top=0.9)

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

def getClosestTemp(statsTime, tempTimes, obsTemps):

    twoHours = datetime.timedelta(0.0, 7200.0)

    validTimes = ((tempTimes > (statsTime - twoHours)) & \
                  (tempTimes < (statsTime + twoHours)))

    if (len(validTimes) < 1):
        return (statsTime, float('NaN'))
    
    searchTimes = tempTimes[validTimes]
    searchTemps = obsTemps[validTimes]

    if (len(searchTimes) < 1 or len(searchTemps) < 1):
        return (statsTime, float('NaN'))

    minDeltaTime = 1.0e99
    ttime = searchTimes[0]
    temp = searchTemps[0]
    for ii, temptime in enumerate(searchTimes, start=0):
        deltaTime = math.fabs((temptime - statsTime).total_seconds())
        if (deltaTime < minDeltaTime):
            minDeltaTime = deltaTime
            temp = searchTemps[ii]
            ttime = temptime

    return (ttime, temp)

########################################################################
# compute a percentile value from the histogram array
# the 'HistCounts' member of statsData holds a comma-delimited list
# of counts in the histogram, from which to compute the percentile

def computePercentile(statsData, perc):

    histMin = np.array(statsData["HistMin"]).astype(np.double)
    histDelta = np.array(statsData["HistDelta"]).astype(np.double)
    histCountsArray = statsData["HistCounts"]
    
    percVals = []

    for ii, histCounts in enumerate(histCountsArray, start=0):

        hmin = histMin[ii]
        hdel = histDelta[ii]

        # split the hist counts on commas
        counts = np.array(histCounts.split(",")).astype(np.double)
        nvals = sum(counts)

        # accumulate until exceed desired percentile

        countSum = 0.0
        prevSum = 0.0
        percVal = 0.0

        for jj, count in enumerate(counts):
            countSum = countSum + count
            pp = (float(countSum) / float(nvals)) * 100.0
            if (pp > perc):
                prevPp = (float(prevSum) / float(nvals)) * 100.0
                frac = (perc - prevPp) / (pp - prevPp)
                xx = hmin + float(jj) * hdel
                prevXx = xx - hdel
                percVal = prevXx + frac * hdel
                break
            prevSum = countSum

        percVals.append(percVal)

    return percVals

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

