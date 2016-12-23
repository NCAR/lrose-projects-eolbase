#!/usr/bin/env python

#===========================================================================
#
# Produce plots for sun scan analysis
#
#===========================================================================

import os
import sys
import subprocess
from optparse import OptionParser
import numpy as np
import numpy.ma as ma
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
    parser.add_option('--ss_file',
                      dest='ssFilePath',
                      default='../data/pecan/suncal.pecan.qc.txt',
                      help='Sun scan results file path')
    parser.add_option('--flux_file',
                      dest='fluxFilePath',
                      default='../data/pecan/fluxtable.txt',
                      help='Solar flux values from Penticton')
    parser.add_option('--cp_file',
                      dest='cpFilePath',
                      default='../data/pecan/spol_pecan_CP_analysis_20150524_000021.txt',
                      help='CP results file path')
    parser.add_option('--title',
                      dest='title',
                      default='SUN SCAN ANALYSIS - PECAN',
                      help='Title for plot')
    parser.add_option('--width',
                      dest='figWidthMm',
                      default=400,
                      help='Width of figure in mm')
    parser.add_option('--height',
                      dest='figHeightMm',
                      default=320,
                      help='Height of figure in mm')
    
    (options, args) = parser.parse_args()
    
    if (options.verbose == True):
        options.debug = True

    if (options.debug == True):
        print >>sys.stderr, "Running %prog"
        print >>sys.stderr, "  ssFilePath: ", options.ssFilePath
        print >>sys.stderr, "  cpFilePath: ", options.cpFilePath
        print >>sys.stderr, "  fluxFilePath: ", options.fluxFilePath

    # read in column headers for sunscan results

    iret, ssHdrs, ssData = readColumnHeaders(options.ssFilePath)
    if (iret != 0):
        sys.exit(-1)

    # read in data for sunscan results

    (ssTimes, ssData) = readInputData(options.ssFilePath, ssHdrs, ssData)

    # read in column headers for CP results

    iret, cpHdrs, cpData = readColumnHeaders(options.cpFilePath)
    if (iret != 0):
        sys.exit(-1)

    # read in data for CP results

    (cpTimes, cpData) = readInputData(options.cpFilePath, cpHdrs, cpData)

    # read in flux table data

    (fluxTimes, fluxData) = readFluxData(options.fluxFilePath);

    # render the plot
    
    doPlot(ssTimes, ssData, cpTimes, cpData, fluxTimes, fluxData)

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
    fp.close()

    # read in a line at a time, set colData
    for line in lines:
        
        commentIndex = line.find("#")
        if (commentIndex >= 0):
            continue
            
        # data
        
        data = line.strip().split()

        for index, var in enumerate(colHeaders, start=0):
            if (var == 'count' or \
                var == 'year' or var == 'month' or var == 'day' or \
                var == 'hour' or var == 'min' or var == 'sec' or \
                var == 'nBeamsNoise'):
                colData[var].append(int(data[index]))
            else:
                if (isNumber(data[index])):
                    colData[var].append(float(data[index]))
                else:
                    colData[var].append(data[index])

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

    return obsTimes, colData

########################################################################
# Read in flux data

def readFluxData(filePath):

    # open file

    fp = open(filePath, 'r')
    lines = fp.readlines()
    fp.close()

    # read in column headers from line 0

    colHeaders = []
    colHeaders = lines[0].lstrip(" ").rstrip("\n").split()
    if (options.debug == True):
        print >>sys.stderr, "colHeaders: ", colHeaders

    # read in a line at a time, set colData

    colData = {}
    for index, var in enumerate(colHeaders, start=0):
        colData[var] = []
        
    for line in lines:
        
        if (line.find("flux") >= 0):
            continue
        if (line.find("----") >= 0):
            continue
        if (line.find("#") >= 0):
            continue
            
        # data
        
        data = line.strip().split()
        
        for index, var in enumerate(colHeaders, start=0):
            if (var == 'fluxdate' or var == 'fluxtime'):
                colData[var].append(data[index])
            else:
                if (isNumber(data[index])):
                    colData[var].append(float(data[index]))

    # load observation times array

    fdate = colData['fluxdate']
    ftime = colData['fluxtime']

    obsTimes = []
    for ii, var in enumerate(fdate, start=0):
        year = fdate[ii][0:4]
        month = fdate[ii][4:6]
        day = fdate[ii][6:8]
        hour = ftime[ii][0:2]
        minute = ftime[ii][2:4]
        sec = ftime[ii][4:6]
        thisTime = datetime.datetime(int(year), int(month), int(day),
                                     int(hour), int(minute), int(sec))
        obsTimes.append(thisTime)

    return obsTimes, colData

########################################################################
# Check is a number

def isNumber(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

########################################################################
# Moving average filter

def movingAverage(values, window):

    weights = np.repeat(1.0, window)/window
    sma = np.convolve(values, weights, 'same')
    return sma

########################################################################
# Plot

def doPlot(ssTimes, ssData, cpTimes, cpData, fluxTimes, fluxData):

    fileName = options.ssFilePath
    titleStr = "File: " + fileName
    hfmt = dates.DateFormatter('%y/%m/%d')

    # times
    
    sstimes = np.array(ssTimes).astype(datetime.datetime)
    cptimes = np.array(cpTimes).astype(datetime.datetime)

    # power
    
    powerHc = np.array(ssData["quadPowerDbmHc"]).astype(np.double)
    validPowerHc = (np.isfinite(powerHc) & (powerHc < -59.0) & (powerHc > -64.0))

    powerVc = np.array(ssData["quadPowerDbmVc"]).astype(np.double)
    validPowerVc = (np.isfinite(powerVc) & (powerVc < -59.0) & (powerVc > -64.0))
    
    # S1S2, xpol ratio
    
    S1S2 = np.array(ssData["S1S2"]).astype(np.double)
    validS1S2 = (np.isfinite(S1S2) & (S1S2 < 1.2) & (S1S2 > 0.5))
    
    # XPOL ratio and Sunscan Zdrm
    
    XpolR = np.array(cpData["cpRatioClut"]).astype(np.double)
    validXpolR = (np.isfinite(XpolR) & (XpolR < 2.0) & (XpolR > -2.0))
    
    Zdrm = np.array(cpData["SunscanZdrm"]).astype(np.double)
    validZdrm = (np.isfinite(Zdrm) & (Zdrm < 0.5) & (Zdrm > -0.4))

    # get fluxes for each valid solar result

    fluxObs = np.array(fluxData["fluxobsflux"]).astype(np.double)
    flTimes = np.array(fluxTimes).astype(datetime.datetime)

    goodTimesHc = sstimes[validPowerHc]
    goodTimesVc = sstimes[validPowerVc]
    powerHcGood = powerHc[validPowerHc]
    powerVcGood = powerVc[validPowerVc]

    fltimesH = []
    fluxesH = []

    fltimesV = []
    fluxesV = []
    
    for ii, hcTime in enumerate(goodTimesHc, start=0):
        (fltime, flux) = getClosestFlux(hcTime, fluxTimes, fluxData['fluxobsflux'])
        fltimesH.append(fltime)
        fluxesH.append(flux)

    for ii, vcTime in enumerate(goodTimesVc, start=0):
        (fltime, flux) = getClosestFlux(vcTime, fluxTimes, fluxData['fluxobsflux'])
        fltimesV.append(fltime)
        fluxesV.append(flux)

    # beam width correction for solar obs

    solarRadioWidth = 0.57
    radarBeamWidth = 0.92
    kk = math.pow((1.0 + 0.18 * math.pow((solarRadioWidth / radarBeamWidth), 2.0)), 2.0)

    # estimated received power given solar flux

    beamWidthRad = (radarBeamWidth * math.pi) / 180.0
    radarFreqMhz = 2809.0
    solarFreqMhz = 2800.0
    radarWavelengthM = (2.99735e8 / (radarFreqMhz * 1.0e6))

    antennaGainHdB = 44.95
    antennaGainH = math.pow(10.0, antennaGainHdB / 10.0)
    antennaGainVdB = 45.32
    antennaGainV = math.pow(10.0, antennaGainVdB / 10.0)

    waveguideGainHdB = -1.16
    waveguideGainH = math.pow(10.0, waveguideGainHdB / 10.0)
    waveguideGainVdB = -1.44
    waveguideGainV = math.pow(10.0, waveguideGainVdB / 10.0)

    # pulse width change

    timeStart1us = datetime.datetime(2015, 6, 8, 0, 0, 0)

    if (options.debug):
        print >>sys.stderr, " kk: ", kk
        print >>sys.stderr, " antennaGainH: ", antennaGainH
        print >>sys.stderr, " antennaGainV: ", antennaGainV
        print >>sys.stderr, " radarWavelengthM: ", radarWavelengthM

    sunPwrsH = []
    rxGainsHc = []
    sunPwrsV = []
    rxGainsVc = []
    
    for ii, hcTime in enumerate(goodTimesHc, start=0):
        noiseBandWidthHz = 1.0e6
        if (hcTime < timeStart1us):
            noiseBandWidthHz = 1.0e6 / 1.3
        hcPower = powerHcGood[ii]
        flux2800 = fluxesH[ii]
        flux2809 = (0.0002 * flux2800 - 0.01) * (radarFreqMhz - solarFreqMhz) + flux2800
        PrHW = ((antennaGainH * waveguideGainH * \
                 radarWavelengthM * radarWavelengthM * flux2809 * \
                 1.0e-22 * noiseBandWidthHz) / \
                (4 * math.pi * 2.0 * kk))
        PrHdBm = 10.0 * math.log10(PrHW) + 30.0
        rxGainHcdB = hcPower - PrHdBm
        if (options.debug):
            print >>sys.stderr, "================================"
            print >>sys.stderr, "  hcTime, fltime, flux2800, flux2809: ", \
                hcTime, fltimesH[ii], flux2800, flux2809
            print >>sys.stderr, "  PrHW, PrHdBm, hcPower, rxGainHcDb: ", \
                PrHW, PrHdBm, hcPower, rxGainHcdB
        sunPwrsH.append(PrHdBm)
        rxGainsHc.append(rxGainHcdB)

    for ii, vcTime in enumerate(goodTimesVc, start=0):
        noiseBandWidthHz = 1.0e6
        if (vcTime < timeStart1us):
            noiseBandWidthHz = 1.0e6 / 1.3
        vcPower = powerVcGood[ii]
        flux2800 = fluxesV[ii]
        flux2809 = (0.0002 * flux2800 - 0.01) * (radarFreqMhz - solarFreqMhz) + flux2800
        PrVW = ((antennaGainV * waveguideGainV * \
                 radarWavelengthM * radarWavelengthM * flux2809 * \
                 1.0e-22 * noiseBandWidthHz) / \
                (4 * math.pi * 2.0 * kk))
        PrVdBm = 10.0 * math.log10(PrVW) + 30.0
        rxGainVcdB = vcPower - PrVdBm
        if (options.debug):
            print >>sys.stderr, "================================"
            print >>sys.stderr, "  vcTime, fltime, flux2800, flux2809: ", \
                vcTime, fltimesV[ii], flux2800, flux2809
            print >>sys.stderr, "  PrVW, PrVdBm, vcPower, rxGainVcDb: ", \
                PrVW, PrVdBm, vcPower, rxGainVcdB
        sunPwrsV.append(PrVdBm)
        rxGainsVc.append(rxGainVcdB)

    # rx gains daily stats
    
    (dailyTimesHc, dailyRxGainsHc) = computeDailyStats(goodTimesHc, rxGainsHc)
    (dailyTimesVc, dailyRxGainsVc) = computeDailyStats(goodTimesVc, rxGainsVc)

    # set up plot structure

    widthIn = float(options.figWidthMm) / 25.4
    htIn = float(options.figHeightMm) / 25.4

    fig1 = plt.figure(1, (widthIn, htIn))
    ax1 = fig1.add_subplot(4,1,1,xmargin=0.0)
    ax2 = fig1.add_subplot(4,1,2,xmargin=0.0)
    ax3 = fig1.add_subplot(4,1,3,xmargin=0.0)
    ax4 = fig1.add_subplot(4,1,4,xmargin=0.0)

    oneDay = datetime.timedelta(1.0)
    ax1.set_xlim([sstimes[0] - oneDay, sstimes[-1] + oneDay])
    ax2.set_xlim([sstimes[0] - oneDay, sstimes[-1] + oneDay])
    ax3.set_xlim([sstimes[0] - oneDay, sstimes[-1] + oneDay])
    ax4.set_xlim([sstimes[0] - oneDay, sstimes[-1] + oneDay])

    # solar flux - axis 1
    
    #ax1.plot(fltimesH, fluxesH, \
    #         label = 'solarFlux', linewidth=1, color='red')
    ax1.plot(flTimes, fluxObs, \
             label = 'obsFlux', linewidth=1, color='blue')

    # power - axis 2
    
    ax2.plot(sstimes[validPowerHc], powerHc[validPowerHc], \
             label = 'Power HC', linewidth=1, color='red')

    ax2.plot(sstimes[validPowerVc], powerVc[validPowerVc], \
             label = 'Power VC', linewidth=1, color='blue')
    
    # receiver gain etc - axis 4
    
    ax3.plot(dailyTimesHc, dailyRxGainsHc, \
             label = 'RxGainHc', linewidth=1, color='red')
    ax3.plot(dailyTimesVc, dailyRxGainsVc, \
             label = 'RxGainVc', linewidth=1, color='blue')
    ax3.plot(dailyTimesHc, dailyRxGainsHc, \
             "^", label = 'RxGainHc', color='red', markersize=10)
    ax3.plot(dailyTimesVc, dailyRxGainsVc, \
             "^", label = 'RxGainVc', color='blue', markersize=10)

    # S1S2, xpol ratio, Sunscan Zdrm - axis 4
    
    ax4.plot(sstimes[validS1S2], S1S2[validS1S2], \
             label = 'S1S2', linewidth=1, color='red')
    
    
    ax4.plot(cptimes[validXpolR], XpolR[validXpolR], \
             label = 'cpRatioClut', linewidth=1, color='blue')
    
    ax4.plot(cptimes[validZdrm], Zdrm[validZdrm], \
             label = 'SunscanZdrm', linewidth=1, color='green')

    # legends labels etc

    ax1.set_title("Solar Flux from Penticton, Canada (Sfu)", fontsize=12)
    ax2.set_title("Solar power as measured by SPOL (dBm)", fontsize=12)
    ax3.set_title("SPOL retrieved receiver gain (dB)", fontsize=12)
    ax4.set_title("S1S2, X-pol ratio and ZDR bias (dB)", fontsize=12)
    
    configureAxis(ax1, 90.0, 150.0, "Solar flux (Sfu)", 'upper left')
    configureAxis(ax2, -9999.0, -9999.0, "Receiver power (dBm)", 'upper left')
    configureAxis(ax3, -9999.0, -9999.0, "Receiver gain (dB)", 'upper right')
    configureAxis(ax4, -9999.0, -9999.0, "ZDR ratios (dB)", 'upper right')

    fig1.suptitle("SPOL SUN SCAN ANALYSIS FOR RECEIVER GAIN AND ZDR BIAS", fontsize=16)
    fig1.autofmt_xdate()

    plt.tight_layout()
    fig1.subplots_adjust(bottom=0.10, left=0.06, right=0.97, top=0.94)
    plt.show()

########################################################################
# initialize legends etc

def configureAxis(ax, miny, maxy, ylabel, legendLoc):
    
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
# get flux closest in time to the search time

def getClosestFlux(hcTime, fluxTimes, obsFlux):

    minDeltaTime = 1.0e99
    fltime = fluxTimes[0]
    flux = obsFlux[0]
    for ii, ftime in enumerate(fluxTimes, start=0):
        deltaTime = math.fabs((ftime - hcTime).total_seconds())
        if (deltaTime < minDeltaTime):
            minDeltaTime = deltaTime
            flux = obsFlux[ii]
            fltime = ftime
            
    return (fltime, flux)

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

