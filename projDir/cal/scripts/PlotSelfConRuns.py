#!/usr/bin/env python

#===========================================================================
#
# Plot Ray details for KDP analysis
#
#===========================================================================

import os
import sys
import subprocess
from optparse import OptionParser
import numpy as np
import matplotlib.pyplot as plt
import math

def main():

    global options

    global dirPath
    global fileIndex
    global fileList
    
    global colHeaders
    global colData

    global rayTime
    global elevation
    global azimuth
    global dbzBias
    global accumCorrelation

    global thisScriptName
    thisScriptName = os.path.basename(__file__)

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
    parser.add_option('--file',
                      dest='initialFilePath',
                      default='/tmp/selfcon_run_files/cal/selfcon_run_20150716-040521.081_srun-361_erun-561_el-000.5_az-027.8_.txt',
                      help='Initial file path')
    parser.add_option('--title',
                      dest='title',
                      default='SELF-CONSISTENCY RUN PLOT',
                      help='Title for plot')
    parser.add_option('--width',
                      dest='figWidthMm',
                      default=600,
                      help='Width of figure in mm')
    parser.add_option('--height',
                      dest='figHeightMm',
                      default=250,
                      help='Height of figure in mm')
    
    (options, args) = parser.parse_args()
    
    if (options.verbose == True):
        options.debug = True

    if (options.debug == True):
        print >>sys.stderr, "Running ", thisScriptName
        print >>sys.stderr, "  initialFilePath: ", options.initialFilePath

    # read in file list

    readFileList()
    
    # read in data for self_con results
    
    if (readFileData() != 0):
        sys.exit(-1)
    
    # create the plots
    # from there it is interactive for the user

    createPlots()

    # done

    sys.exit(0)
    
########################################################################
# Read in list of available files in the directory

def readFileList():

    global dirPath
    global fileIndex
    global fileList
    
    dirPath = os.path.dirname(options.initialFilePath)
    fileList = os.listdir(dirPath)
    fileList.sort()

    fileIndex = 0
    for index, file in enumerate(fileList):
        if (options.initialFilePath.find(file) > 0):
            fileIndex = index
            break
    
    if (options.debug == True):
        print >>sys.stderr, "====>> File list"
        print >>sys.stderr, "  Dir path: ", dirPath
        print >>sys.stderr, "  Initial file path: ", options.initialFilePath
        print >>sys.stderr, "  File index : ", fileIndex
        print >>sys.stderr, "  n files : ", len(fileList)
        print >>sys.stderr, "  Computed File path: ", getFilePath()

    if (options.verbose == True):
        print >>sys.stderr, "  Files:    "
        for index, file in enumerate(fileList):
            print >>sys.stderr, "     ", index, ": ", file

########################################################################
# Get the path to the current data file

def getFilePath():

    filePath = os.path.join(dirPath, fileList[fileIndex])
    return filePath
                            
########################################################################
# Get the name of the current data file

def getFileName():

    return fileList[fileIndex]
                            
########################################################################
# Read column-based header and data

def readFileData():

    global colHeaders
    global colData
    global rayTime
    global elevation
    global azimuth
    global dbzBias
    global accumCorrelation

    colHeaders = []
    colData = {}

    fp = open(getFilePath(), 'r')
    lines = fp.readlines()
    fp.close()

    if (len(lines) < 2):
        print >>sys.stderr, "ERROR - no data, file: ", getFilePath()
        return -1
    
    commentIndex = lines[0].find("#")
    if (commentIndex == 0):
        # header
        colHeaders = lines[0].lstrip("# ").rstrip("\n").split()
        if (options.debug == True):
            print >>sys.stderr, "colHeaders: ", colHeaders
    else:
        print >>sys.stderr, "ERROR - readFileData"
        print >>sys.stderr, "  First line does not start with #"
        return -1

    # create data variables (dictionary)

    for index, var in enumerate(colHeaders, start=0):
        colData[var] = []
        
    # decode a line at a time, set colData

    for line in lines:
        
        commentIndex = line.find("#")
        if (commentIndex >= 0):
            toks = line.strip().split()
            if (len(toks) >= 4 and toks[1] == 'time:'):
                rayTime = toks[2] + '-' + toks[3] 
            elif (len(toks) >= 3 and toks[1] == 'elev:'):
                elevation = toks[2]
            elif (len(toks) >= 3 and toks[1] == 'az:'):
                azimuth = toks[2]
            elif (len(toks) >= 3 and toks[1] == 'dbzBias:'):
                dbzBias = toks[2]
            elif (len(toks) >= 3 and toks[1] == 'accumCorrelation:'):
                accumCorrelation = toks[2]
            continue
            
        data = line.strip().split()

        for index, var in enumerate(colHeaders, start=0):
            if (var == 'gateNum'):
                colData[var].append(int(data[index]))
            else:
                colData[var].append(float(data[index]))

    return 0

########################################################################
# Key-press event

def press(event):

    global fileIndex

    if (options.debug == True):
        print >>sys.stderr, "press: ", event.key
        
    if (event.key == 'left'):
        if (fileIndex > 0):
            fileIndex = fileIndex - 1
            reloadAndDraw()
            
    if (event.key == 'right'):
        if (fileIndex < len(fileList) - 1):
            fileIndex = fileIndex + 1
            reloadAndDraw()
            
    if (options.debug == True):
        print >>sys.stderr, "  File index : ", fileIndex
        print >>sys.stderr, "  File path  : ", getFilePath()

########################################################################
# Create the plots - original instance

def createPlots():

    global fig1
    global ax1
    global ax2
    global ax3
    global ax4
    global ax5

    widthIn = float(options.figWidthMm) / 25.4
    htIn = float(options.figHeightMm) / 25.4

    fig1 = plt.figure(1, (widthIn, htIn))
    fig1.canvas.mpl_connect('key_press_event', press)

    ax1 = fig1.add_subplot(1,5,1,xmargin=0.0)
    ax2 = fig1.add_subplot(1,5,2,xmargin=0.0)
    ax3 = fig1.add_subplot(1,5,3,xmargin=0.0)
    ax4 = fig1.add_subplot(1,5,4,xmargin=0.0)
    ax5 = fig1.add_subplot(1,5,5,xmargin=0.0)

    doPlot()
    fig1.suptitle("SELF-CONSISTENCY RUN ANALYSIS - file " + getFileName())
    plt.tight_layout()
    plt.subplots_adjust(top=0.9)
    plt.show()

########################################################################
# Reload and redraw - after getting new file

def reloadAndDraw():

    # read in data for self_con results
    
    if (readFileData() != 0):
        sys.exit(-1)
    
    # plot XY
    
    doPlot()
    plt.draw()
    
########################################################################
# Plot data on axes

def doPlot():

    ax1.clear()
    ax2.clear()
    ax3.clear()
    ax4.clear()
    ax5.clear()

    fileName = fileList[fileIndex]
    nameParts = fileName.split("_")
    timeStr = "Time " + rayTime
    runStartStr = nameParts[3]
    runEndStr = nameParts[4]
    azStr = nameParts[5]
    elStr = nameParts[6]

    gateNum = colData['gateNum']

    # plot 1 - SNR and DBZ

    ax1.set_title(timeStr, fontsize=12)
    ax1.plot(gateNum, colData['snr'], label='snr', color='red', linewidth=1)
    ax1.plot(gateNum, colData['dbzCorr'], label='dbzCorr', color='blue', linewidth=1)
    ax1.plot(gateNum, colData['dbzObs'], label='dbzObs', color='cyan', linewidth=1)

    legend1 = ax1.legend(loc='lower center', ncol=1, columnspacing=0, labelspacing=0)
    for label in legend1.get_texts():
        label.set_fontsize('small')
    ax1.set_xlabel("gateNum")
    ax1.set_ylabel("SNR, DBZ")

    # plot 2 - PHIDP

    phidpEst = np.array(colData['phidpEst']).astype(np.double)
    phidpFilt = np.array(colData['phidpFilt']).astype(np.double)
    phidpFiltMin = np.min(phidpFilt)
    phidpFiltExcess = phidpFilt - phidpFiltMin
    phidpDiff = (phidpEst - phidpFilt) + phidpFiltMin
    phidpDiffNorm = (phidpEst - phidpFilt) / (phidpFilt - phidpFiltMin)
    phidpDiffNorm[phidpDiffNorm < -2.0] = float('NaN')
    phidpDiffNorm[phidpDiffNorm > 2.0] = float('NaN')

    ax2.set_title('dbzBias: ' + dbzBias + ' corr: ' + accumCorrelation, fontsize=12)
    ax2.plot(gateNum, colData['phidpObs'], label='phidpObs', color='cyan', linewidth=1)
    ax2.plot(gateNum, colData['phidpEst'], label='phidpEst', color='red', linewidth=2)
    ax2.plot(gateNum, colData['phidpFilt'], label='phidpFilt', color='green', linewidth=2)
    ax2.plot(gateNum, colData['phidpCondFilt'], label='phidpCondFilt', color='orange', linewidth=1)
    ax2.plot(gateNum, phidpDiff, label='phidpDiff', color='blue', linewidth=2)
    ax2.plot([gateNum[0], gateNum[-1]], [phidpFiltMin, phidpFiltMin],
             label='phidpFiltMin', color='lightblue', linewidth=1)

    minPhidp = min(colData['phidpFilt'])
    maxPhidp = max(colData['phidpFilt'])
    rangePhidp = maxPhidp - minPhidp
    plotMin2 = minPhidp - rangePhidp * 0.3
    ax2.set_ylim(bottom = plotMin2)

    legend2 = ax2.legend(loc='lower right', ncol=2, columnspacing=0, labelspacing=0)
    for label in legend2.get_texts():
        label.set_fontsize('small')
    ax2.set_xlabel("gateNum")
    ax2.set_ylabel("PHIDP (deg)")
    
    # plot 3 - KDP, PSOB

    ax3.set_title('Elevation = ' + elevation, fontsize=12)
    ax3.plot(gateNum, colData['kdp'], label='kdp', color='red', linewidth=2)
    ax3.plot(gateNum, colData['psob'], label='psob', color='orange', linewidth=1)
    ax3.plot(gateNum, colData['rhohv'], label='rhohv', color='black', linewidth=1)
    ax3.plot(gateNum, colData['zdrObs'], label='ZdrObs', color='cyan', linewidth=1)
    ax3.plot(gateNum, colData['zdrCorr'], label='ZdrCorr', color='blue', linewidth=1)
    ax3.plot(gateNum, colData['zdrTerm'], label='ZdrTerm', color='green', linewidth=2)
    # ax3.plot(gateNum, phidpDiffNorm, label='diffNorm', color='magenta', linewidth=2)

    legend3 = ax3.legend(loc='lower center', ncol=2, columnspacing=0, labelspacing=0)
    for label in legend3.get_texts():
        label.set_fontsize('small')
    ax3.set_xlabel("gateNum")
    ax3.set_ylabel("KDP, PSOB")
    ax3.set_ylim(bottom = -1)

    # plot 4 - PID

    ax4.set_title('Azimuth = ' + azimuth, fontsize=12)
    ax4.plot(gateNum, colData['pid'], label='PID', color='red', linewidth=2)

    legend4 = ax4.legend(loc='lower center', ncol=2, columnspacing=0, labelspacing=0)
    for label in legend4.get_texts():
        label.set_fontsize('small')
    ax4.set_xlabel("gateNum")
    ax4.set_ylabel("PID")
    ax4.set_ylim([0, 7])
    
    # plot 5 - Z vs ZDR

    ax5.set_title('Z-ZDR')
    ax5.plot(colData['dbzCorr'], colData['zdrCorr'], 'o', label='Z-ZDR', color='red')

    legend5 = ax5.legend(loc='upper left', ncol=2, columnspacing=0, labelspacing=0)
    for label in legend5.get_texts():
        label.set_fontsize('small')
    ax5.set_xlabel("DBZ corrected")
    ax5.set_ylabel("ZDR corrected")
    ax5.set_xlim([10, 55])
    ax5.set_ylim([-0.5, 3.5])

    # title

    fig1.suptitle("SELF-CONSISTENCY RUN ANALYSIS - file " + getFileName())

    return

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

