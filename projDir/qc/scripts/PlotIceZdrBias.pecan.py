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
                      default='../data/pecan/zdr_bias_ice.pecan.txt',
                      help='File path for bias results')
    parser.add_option('--cp_file',
                      dest='cpFilePath',
                      default='../data/pecan/spol_pecan_CP_analysis_20150528_000553.txt',
                      help='CP results file path')
    parser.add_option('--title',
                      dest='title',
                      default='ZDR BIAS FROM ICE',
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
                      default='2015 06 16 00 00 00',
                      help='Start time for XY plot')
    parser.add_option('--end',
                      dest='endTime',
                      default='2015 07 17 00 00 00',
                      help='End time for XY plot')
    parser.add_option('--sur_only',
                      dest='surOnly', default=False,
                      action="store_true",
                      help='Only process surveillance scans')
    parser.add_option('--rhi_only',
                      dest='rhiOnly', default=False,
                      action="store_true",
                      help='Only process RHI scans')
    parser.add_option('--regr',
                      dest='plotRegr', default=False,
                      action="store_true",
                      help='Plot the regression of ZDR vs Temp')
    parser.add_option('--temp',
                      dest='plotSiteTemp', default=False,
                      action="store_true",
                      help='Plot the site temperature')
    parser.add_option('--sunscan',
                      dest='plotSunscanCp', default=False,
                      action="store_true",
                      help='Plot the CP method from sunscans')
    parser.add_option('--mean',
                      dest='plotMean', default=False,
                      action="store_true",
                      help='Plot the adjusted mean')
    parser.add_option('--adj',
                      dest='meanAdj',
                      default='-0.15',
                      help='Adjustment to mean for ZDR bias')
    parser.add_option('--perc',
                      dest='percentile',
                      default='15.0',
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
        print >>sys.stderr, "Running %prog"
        print >>sys.stderr, "  cpFilePath: ", options.cpFilePath
        print >>sys.stderr, "  biasFilePath: ", options.biasFilePath
        print >>sys.stderr, "  startTime: ", startTime
        print >>sys.stderr, "  endTime: ", endTime
        print >>sys.stderr, "  surOnly: ", options.surOnly
        print >>sys.stderr, "  rhiOnly: ", options.rhiOnly
        print >>sys.stderr, "  meanAdj: ", options.meanAdj
        print >>sys.stderr, "  percentile: ", options.percentile

    # read in column headers for bias results

    iret, biasHdrs = readColumnHeaders(options.biasFilePath)
    if (iret != 0):
        sys.exit(-1)

    # read in data for bias results

    biasData, biasTimes = readInputData(options.biasFilePath, biasHdrs)

    # read in column headers for CP results

    iret, cpHdrs = readColumnHeaders(options.cpFilePath)
    if (iret != 0):
        sys.exit(-1)

    # read in data for CP results

    cpData, cpTimes = readInputData(options.cpFilePath, cpHdrs)

    # prepare the data for plotting

    prepareData(biasData, biasTimes, cpData, cpTimes)

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
            print >>sys.stderr, "colHeaders: ", colHeaders
    else:
        print >>sys.stderr, "ERROR - readColumnHeaders"
        print >>sys.stderr, "  First line does not start with #"
        return -1, colHeaders
    
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
                print >>sys.stderr, "skipping line: ", line
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
# Prepare data sets for plotting

def prepareData(biasData, biasTimes, cpData, cpTimes):

    lenMeanFilter = int(options.lenMean)

    # set up arrays for ZDR bias

    global btimes
    btimes = np.array(biasTimes).astype(datetime.datetime)
    
    isRhi = np.array(biasData["IsRhi"]).astype(np.int)

    global validMean
    zdrMean = np.array(biasData["ZdrmInIceMean"]).astype(np.double)
    zdrMean = movingAverage(zdrMean, lenMeanFilter)
    validMean = np.isfinite(zdrMean)
    
    percVal = float(options.percentile)
    percStr = 'ZdrInIcePerc' + '{:05.2f}'.format(percVal)
    if (options.debug):
        print >>sys.stderr, "=>> using: ", percStr

    biasIce = np.array(biasData[percStr]).astype(np.double)
    biasIce = movingAverage(biasIce, lenMeanFilter)
    validIce = np.isfinite(biasIce)
    
    percmStr = 'ZdrmInIcePerc' + '{:05.2f}'.format(percVal)
    if (options.debug):
        print >>sys.stderr, "=>> using: ", percmStr

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

    # site temp, vert pointing and sun scan results

    global ctimes
    ctimes = np.array(cpTimes).astype(datetime.datetime)

    global ZdrmVert, validZdrmVert
    ZdrmVert = np.array(cpData["ZdrmVert"]).astype(np.double)
    validZdrmVert = np.isfinite(ZdrmVert)

    global SunscanZdrm, validSunscanZdrm
    SunscanZdrm = np.array(cpData["SunscanZdrm"]).astype(np.double)
    validSunscanZdrm = np.isfinite(SunscanZdrm)

    global tempSite, validTempSite, validTempTimes
    tempSite = np.array(cpData["TempSite"]).astype(np.double)
    validTempSite = np.isfinite(tempSite)
    validTempTimes = ctimes[validTempSite]

    # tx ratio

    txPwrH = np.array(cpData["TxPwrH"]).astype(np.double)
    txPwrV = np.array(cpData["TxPwrV"]).astype(np.double)

    global ratioTimes, ratioIceVals, ratioIceBias, ratioTxCorrBias, ratioTempVals
    ratioTimes = []
    ratioIceVals = []
    ratioTempVals = []
    ratioIceBias = []

    for ii, biasVal in enumerate(validIceMVals, start=0):
        btime = validIceMBtimes[ii]
        ratioTime, ratioTemp, ratioVal = getClosestRatio \
                                         (btime, ctimes, tempSite, txPwrH, txPwrV)
        ratioTempVals.append(ratioTemp)
        txCorrBias = biasVal - ratioVal
        ratioTimes.append(ratioTime)
        ratioIceVals.append(ratioVal)
        ratioIceBias.append(biasVal)
        if (options.verbose):
            print >>sys.stderr, \
                "==>> btime, rtime, bias, txPwrH, txPwrV, ratioVal, txCorrBias:", \
                btime, ratioTime, biasVal, txPwrH[ii], txPwrV[ii], ratioVal, txCorrBias

    meanRatio = np.mean(ratioIceVals)
    normRatios = ratioIceVals - meanRatio
    ratioTxCorrBias = validIceMVals - normRatios
        
    # ZDR bias vs temp

    global tempTimes, tempIceMVals, tempIceMBias
    tempTimes = []
    tempIceMVals = []
    tempIceMBias = []

    for ii, biasVal in enumerate(validIceMVals, start=0):
        btime = validIceMBtimes[ii]
        tempTime, tempVal = getClosestTemp(btime, validTempTimes, tempSite)
        tempTimes.append(tempTime)
        tempIceMVals.append(tempVal)
        tempIceMBias.append(biasVal)
        if (options.verbose):
            print >>sys.stderr, "==>> biasTime, biasVal, tempTime, tempVal:", \
                btime, biasVal, tempTime, tempVal

    global tempMean, tempSdev, tempNorm
    tempMean = np.mean(tempSite)
    tempSdev = np.std(tempSite)
    tempNorm = (tempSite - tempMean) / (tempSdev * 10.0)
    if (options.debug):
        print >>sys.stderr, "==>> tempMean, tempSdev: ", tempMean, tempSdev

    # linear regression for bias vs temp
    # obtain the fit, ww[0] is slope, ww[1] is intercept

    global AA, ww, tempRegrX, tempRegrY, minTemp, maxTemp

    AA = array([tempIceMVals, ones(len(tempIceMVals))])
    ww = linalg.lstsq(AA.T, tempIceMBias)[0]
    minTemp = min(tempIceMVals)
    maxTemp = max(tempIceMVals)

    tempRegrX = []
    tempRegrY = []
    tempRegrX.append(minTemp)
    tempRegrX.append(maxTemp)
    tempRegrY.append(ww[0] * minTemp + ww[1])
    tempRegrY.append(ww[0] * maxTemp + ww[1])

    # linear regression for tx-corrected bias vs temp
    # obtain the fit, ww[0] is slope, ww[1] is intercept

    global AA2, ww2, tempRegrX2, tempRegrY2, minTemp2, maxTemp2

    AA2 = array([ratioTempVals, ones(len(ratioTempVals))])
    ww2 = linalg.lstsq(AA2.T, ratioTxCorrBias)[0]
    minTemp2 = min(ratioTempVals)
    maxTemp2 = max(ratioTempVals)

    tempRegrX2 = []
    tempRegrY2 = []
    tempRegrX2.append(minTemp2)
    tempRegrX2.append(maxTemp2)
    tempRegrY2.append(ww2[0] * minTemp2 + ww2[1])
    tempRegrY2.append(ww2[0] * maxTemp2 + ww2[1])

    # correct bias for linear regression

    slope = ww2[0]
    intercept = ww2[1]

    global ratioCorrBias
    ratioCorrBias = []
    for ii, rtime in enumerate(ratioTimes, start=0):
        tempC = ratioTempVals[ii]
        biasDb = ratioIceBias[ii]
        tempCorr = intercept + tempC * slope
        corrBias = biasDb - tempCorr
        ratioCorrBias.append(corrBias)

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

    nplots = 2

    ax1a = fig1.add_subplot(nplots,1,1,xmargin=1.0)
    if (options.plotSiteTemp):
        ax1c = fig1.add_subplot(nplots,1,2,xmargin=1.0)
    else:
        ax1b = fig1.add_subplot(nplots,1,2,xmargin=1.0)

    if (options.plotRegr):
        fig2 = plt.figure(2, (widthIn/2, htIn/2))
        ax2a = fig2.add_subplot(1,1,1,xmargin=1.0, ymargin=1.0)

    oneDay = datetime.timedelta(1.0)
    ax1a.set_xlim([btimes[0] - oneDay, btimes[-1] + oneDay])
    ax1a.set_title("ZDR bias in ice, compared with VERT results")
    if (options.plotSiteTemp):
        ax1c.set_xlim([btimes[0] - oneDay, btimes[-1] + oneDay])
        ax1c.set_title("Site temperature")
    else:
        ax1b.set_xlim([btimes[0] - oneDay, btimes[-1] + oneDay])
        ax1b.set_title("Daily mean ZDR bias in ice")

    # volume by volume plots

    if (options.plotMean):
        ax1a.plot(validMeanBtimes, adjMean,
                  "o", label = 'Measured ZDR Mean + ' + options.meanAdj, \
                  color='lightblue')
    else:
        ax1a.plot(validIceBtimes, validIceVals,
                  "o", label = 'Corrected ZDR Bias', color='red')
    #ax1a.plot(validIceBtimes, validIceVals, \
    #          label = 'ZDR Bias In Ice', linewidth=1, color='red')

    ax1a.plot(validIceMBtimes, validIceMVals, \
              "o", label = 'Measured ZDR bias ' + percStr, color='blue')
    #ax1a.plot(validIceMBtimes, validIceMVals, \
    #          label = 'ZDRM Bias In Ice', linewidth=1, color='blue')
    
    if (options.plotSunscanCp):
        ax1a.plot(ctimes[validSunscanZdrm], SunscanZdrm[validSunscanZdrm], \
                  "^", markersize=10, label = 'Zdrm Sun/CP', color = 'green')
    
    ax1a.plot(ctimes[validZdrmVert], ZdrmVert[validZdrmVert], \
              "^", markersize=10, linewidth=1, label = 'Vert Results', color = 'yellow')

    # daily

    if (options.plotSiteTemp):
        ax1c.plot(validTempTimes,  tempSite[validTempSite], \
                  linewidth=2, label = 'Site temperature', color = 'red')
    else:
        if (options.plotMean):
            ax1b.plot(dailyTimeMean, dailyAdjMean,
                      label = 'Meas ZDR Mean + ' + options.meanAdj, 
                      linewidth=1, color='lightblue')
            ax1b.plot(dailyTimeMean, dailyAdjMean,
                      "^", label = 'Meas ZDR Mean + ' + options.meanAdj,
                      color='lightblue', markersize=10)
        else:
            ax1b.plot(dailyTimeIce, dailyValIce,
                      label = 'Corrected ZDR Bias', linewidth=1, color='red')
            ax1b.plot(dailyTimeIce, dailyValIce,
                      "^", label = 'Corrected ZDR Bias', color='red', markersize=10)
            
        ax1b.plot(dailyTimeIceM, dailyValIceM,
                  label = 'Meas Daily ZDR Bias ' + percStr, linewidth=1, color='blue')
        ax1b.plot(dailyTimeIceM, dailyValIceM,
                  "^", label = 'Meas Daily ZDR ' + percStr, color='blue', markersize=10)
        
        ax1b.plot(ctimes[validZdrmVert], ZdrmVert[validZdrmVert],
                  "^", markersize=10, linewidth=1, label = 'Zdrm Vert (dB)', 
                  color = 'yellow')

    configDateAxis(ax1a, -0.5, 0.5, "ZDR Bias (dB)", 'upper right')

    if (options.plotSiteTemp):
        configDateAxis(ax1c, -9999, 9999, "Temp (C)", 'upper right')
    else:
        configDateAxis(ax1b, -0.5, 0.5, "ZDR Bias (dB)", 'upper right')

    if (options.plotRegr):
        label3 = "ZDR Bias In Ice = " + ("%.5f" % ww[0]) + " * temp + " + ("%.3f" % ww[1])
        ax2a.plot(tempIceMVals, tempIceMBias, 
                 "x", label = label3, color = 'blue')
        ax2a.plot(tempRegrX, tempRegrY, linewidth=3, color = 'blue')
    
        legend3 = ax2a.legend(loc="upper left", ncol=2)
        for label3 in legend3.get_texts():
            label3.set_fontsize(12)
            ax2a.set_xlabel("Site temperature (C)")
            ax2a.set_ylabel("ZDR Bias (dB)")
            ax2a.grid(True)
            ax2a.set_ylim([-0.5, 0.5])
            ax2a.set_xlim([minTemp - 1, maxTemp + 1])
            #title3 = "PECAN ZDR Bias In Ice Vs Temp: " + str(startTime) + " - " + str(endTime)
            title3 = "PECAN ZDR Bias In Ice Vs Temp"
            ax2a.set_title(title3)

    fig1.autofmt_xdate()
    fig1.tight_layout()
    fig1.subplots_adjust(bottom=0.08, left=0.10, right=0.97, top=0.92)
    if (options.plotRegr):
        fig2.subplots_adjust(bottom=0.10, left=0.15, right=0.95, top=0.95)
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
    
    stime = nptimes[0]
    etime = nptimes[-1]
    
    startDate = datetime.datetime(stime.year, stime.month, stime.day, 0, 0, 0)
    endDate = datetime.datetime(etime.year, etime.month, etime.day, 0, 0, 0)

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

