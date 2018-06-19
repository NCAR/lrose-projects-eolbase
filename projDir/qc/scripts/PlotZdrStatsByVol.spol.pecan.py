#!/usr/bin/env python

#===========================================================================
#
# Produce plots for ZDR stats by volume
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
    parser.add_option('--cp_file',
                      dest='cpFilePath',
                      default='../data/pecan/spol_pecan_CP_analysis_20150524_000021.txt',
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
                      default=320,
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
        print >>sys.stderr, "  statsFilePath: ", options.statsFilePath
        print >>sys.stderr, "  startTime: ", startTime
        print >>sys.stderr, "  endTime: ", endTime

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
            elif (var == 'PidLabel' or var == 'TempTime' or \
                  var == 'HistCounts'):
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

    perc = np.array(computePercentile(statsData, float(options.percentile))).astype(np.double)

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
    
#    tempVals = []
#    statsVals = []

#    for ii, statsVal in enumerate(validStats, start=0):
#        stime = validStimes[ii]
#        if (stime >= startTime and stime <= endTime):
#            tempTime, tempVal = getClosestTemp(stime, cpTimes, tempSite)
#            if (np.isfinite(tempVal)):
#                tempVals.append(tempVal)
#                statsVals.append(statsVal)
#                if (options.verbose):
#                    print >>sys.stderr, "==>> statsTime, statsVal, tempTime, tempVal:", \
#                        stime, statsVal, tempTime, tempVal

    # linear regression stats vs temp

#    A = array([tempVals, ones(len(tempVals))])
#    ww = linalg.lstsq(A.T, statsVals)[0] # obtaining the fit, ww[0] is slope, ww[1] is intercept
#    regrX = []
#    regrY = []
#    minTemp = min(tempVals)
#    maxTemp = max(tempVals)
#    regrX.append(minTemp)
#    regrX.append(maxTemp)
#    regrY.append(ww[0] * minTemp + ww[1])
#    regrY.append(ww[0] * maxTemp + ww[1])
    
    # set up plots

    widthIn = float(options.figWidthMm) / 25.4
    htIn = float(options.figHeightMm) / 25.4

    fig1 = plt.figure(1, (widthIn, htIn))
#    fig2 = plt.figure(2, (widthIn/2, htIn/2))

    ax1 = fig1.add_subplot(2,1,1,xmargin=0.0)
#    ax2 = fig1.add_subplot(2,1,2,xmargin=0.0)

#    ax3 = fig2.add_subplot(1,1,1,xmargin=1.0, ymargin=1.0)
    #ax3 = fig2.add_subplot(1,1,1,xmargin=0.0)

    oneDay = datetime.timedelta(1.0)
    ax1.set_xlim([stimes[0] - oneDay, stimes[-1] + oneDay])
    ax1.set_title("ZDRM stats by volume in " + label + ", compared with VERT and CP results")
#    ax2.set_xlim([stimes[0] - oneDay, stimes[-1] + oneDay])
#    ax2.set_title("Site temperature (C)")

    ax1.plot(stimes[validMean], statsMean[validMean], \
             "ro", label = 'ZDR Mean', linewidth=1)

    ax1.plot(stimes[validMean], perc[validMean], \
             "bo", label = 'ZDR perc ' + str(options.percentile))

#    ax1.plot(ctimes[validSunscanZdrm], SunscanZdrm[validSunscanZdrm], \
#             linewidth=2, label = 'Zdrm Sun/CP (dB)', color = 'green')
    
#    ax1.plot(ctimes[validZdrmVert], ZdrmVert[validZdrmVert], \
#             "^", markersize=10, linewidth=1, label = 'Zdrm Vert (dB)', color = 'yellow')


#    ax2.plot(cptimes[validTempSite], tempSite[validTempSite], \
#             linewidth=1, label = 'Site Temp', color = 'blue')

    configDateAxis(ax1, -9999, 9999, "ZDR Stats (dB)", 'upper right')
#    configDateAxis(ax2, -9999, 9999, "Temp (C)", 'upper right')
#   label3 = "ZDR Stats = " + ("%.5f" % ww[0]) + " * temp + " + ("%.3f" % ww[1])
#    ax3.plot(tempVals, statsVals, 
#             "x", label = label3, color = 'blue')
#    ax3.plot(regrX, regrY, linewidth=3, color = 'blue')
    
#    legend3 = ax3.legend(loc="upper left", ncol=2)
#    for label3 in legend3.get_texts():
#        label3.set_fontsize(12)
#    ax3.set_xlabel("Site temperature (C)")
#    ax3.set_ylabel("ZDR Stats (dB)")
#    ax3.grid(True)
#    ax3.set_ylim([-0.5, 0.5])
#    ax3.set_xlim([minTemp - 1, maxTemp + 1])
#    title3 = "ZDR stats Vs Temp: " + str(startTime) + " - " + str(endTime)
#    ax3.set_title(title3)

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
                #print >>sys.stderr, "jj, xx, count, countSum: ", jj, ", ", xx, ", ", count, ", ", countSum
                #print >>sys.stderr, "===>> percVal: ", percVal
                break
            prevSum = countSum

        percVals.append(percVal)

    return percVals

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

