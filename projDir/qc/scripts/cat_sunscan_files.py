#!/usr/bin/env python

#===========================================================================
#
# Cat the files into solars
#
#===========================================================================

from __future__ import print_function

import os
import sys
import subprocess
from optparse import OptionParser
import numpy as np
import matplotlib.pyplot as plt
import math

def main():

    global options
    global debug
    global fileList

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
    parser.add_option('--inputDir',
                      dest='inputDir',
                      default='/scr/sci/rsfdata/pecan/suncal/20150623',
                      help='Directory containing files to be concatenated')
    parser.add_option('--outputDir',
                      dest='outputDir',
                      default='/scr/sci/rsfdata/pecan/suncal/vols/20150623',
                      help='Dir for concatenated files')
    
    (options, args) = parser.parse_args()
    
    if (options.verbose == True):
        options.debug = True

    if (options.debug == True):
        print("Running %prog", file=sys.stderr)
        print("  inputDir: ", options.inputDir, file=sys.stderr)
        print("  outputDir: ", options.outputDir, file=sys.stderr)

    # read in file list

    readFileList(options.inputDir)

    # sort through list, finding the volumes

    findVols()
    
    sys.exit(0)
    
########################################################################
# Read in list of available files in the directory

def readFileList(inputDir):

    global fileList
    fileList = os.listdir(inputDir)
    fileList.sort()

    if (options.debug == True):
        print("Dir path: ", inputDir, file=sys.stderr)
        print("n files : ", len(fileList), file=sys.stderr)

    if (options.verbose == True):
        print("Files:    ", file=sys.stderr)
        for index, file in enumerate(fileList):
            print("   ", index, ": ", file, file=sys.stderr)

########################################################################
# Find the vols

def findVols():

    prevElevDeg = -9999.0
    volFileList = []

    for index, fileName in enumerate(fileList):
        if (fileName.find('.txt') < 0):
            continue
        mainParts = fileName.split('.')
        if (options.debug):
            print(" fileName: ", fileName, file=sys.stderr)
        elevDeg = getElevDeg(fileName)
        if (options.debug):
            print("   ==>> elevDeg: ", elevDeg, file=sys.stderr)
        if (elevDeg < prevElevDeg):
            print("   ================>> end of vol", file=sys.stderr)
            print("   ================>> fileList: ", volFileList, file=sys.stderr)
            concatenateVols(volFileList)
            volFileList = []
        if (elevDeg > -9990):
            prevElevDeg = elevDeg
            volFileList.append(fileName)

########################################################################
# Concatenate the vol files into a single output file

def concatenateVols(volFileList):

    if (len(volFileList) < 1):
        return

    # go to input dir

    os.chdir(options.inputDir)

    # create cat command

    cmd = 'cat '
    for fileName in volFileList:
        cmd = cmd + fileName + ' '
    outputName = os.path.join(options.outputDir, volFileList[0])
    cmd = cmd + ' > ' + outputName

    if (options.debug):
        print("   ==>> cmd: ", cmd, file=sys.stderr)

    # ensure output dir exists

    if (os.path.isdir(options.outputDir) == False):
        os.makedirs(options.outputDir)

    # run the command

    runCommand(cmd)

########################################################################
# Get the elevation angle from the file path

def getElevDeg(fileName):
    elevDeg = -9999.0
    mainParts = fileName.split('.')
    if (options.verbose):
        print("2222222 mainParts: ", mainParts, file=sys.stderr)
    if (len(mainParts) < 2):
        return elevDeg
    subParts = mainParts[1].split('_')
    if (options.verbose):
        print("333333333 subParts: ", subParts, file=sys.stderr)
    if (len(subParts) < 2):
        return elevDeg
    elevDeg = float(subParts[1]) / 10.0
    return elevDeg
                            
########################################################################
# Get the path to the current data file

def getFilePath():

    filePath = os.path.join(dirPath, fileList[fileIndex])
    return filePath
                            
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

