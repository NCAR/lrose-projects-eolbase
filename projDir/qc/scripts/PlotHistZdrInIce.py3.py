#!/usr/bin/env python3


#===========================================================================
#
# Produce histogram for ZDR bias in ice
#
#===========================================================================

from __future__ import print_function

import os
import sys

import numpy as np
import scipy.stats as stats
import matplotlib.mlab as mlab
import matplotlib.pyplot as plt
import matplotlib.mlab as mlab
from optparse import OptionParser
import subprocess

def main():

#   globals

    global options

# parse the command line

    usage = "usage: %prog [options]"
    parser = OptionParser(usage)
    parser.add_option('--debug',
                      dest='debug', default=False,
                      action="store_true",
                      help='Set debugging on')
    parser.add_option('--ice_file',
                      dest='iceFile',
                      #default='/scr/rain2/rsfdata/projects/pecan/zdr_in_ice/qcv3/rhi/ZdrmInIce_june.txt',
                      default='/scr/rain1/rsfdata/projects/dynamo/zdr_in_ice/qcv2/rhi/ZdrmInIce.nov.txt',
                      help='File path for zdr in ice data')
    parser.add_option('--title',
                      dest='title',
                      default='ZDR DISTRIBUTION IN ICE',
                      help='Title for plot')
    parser.add_option('--width',
                      dest='figWidthMm',
                      default=300,
                      help='Width of figure in mm')
    parser.add_option('--height',
                      dest='figHeightMm',
                      default=300,
                      help='Height of figure in mm')
    parser.add_option('--minElev',
                      dest='minElev',
                      default='0.0',
                      help='Min elevation for ZDR data')
    parser.add_option('--maxElev',
                      dest='maxElev',
                      default='90.0',
                      help='Max elevation for ZDR data')
    (options, args) = parser.parse_args()
    
    if (options.debug == True):
        print("Running %prog", file=sys.stderr)
        print("  iceFile: ", options.iceFile, file=sys.stderr)

    # read in headers

    (iret, colHeaders) = readColumnHeaders(options.iceFile)
    if (iret != 0):
        sys.exit(1)

    # read in data

    (iret, colData) = readInputData(options.iceFile, colHeaders)
    if (iret != 0):
        sys.exit(1)

    # render the plot
    
    doPlot(options.iceFile, colHeaders, colData)

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
        print("  File: ", filePath, file=sys.stderr)
        print("  First line does not start with #", file=sys.stderr)
        return -1, colHeaders
    
    return 0, colHeaders

########################################################################
# Read in the data

def readInputData(filePath, colHeaders):

    # open file

    fp = open(filePath, 'r')
    lines = fp.readlines()

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

        for index, var in enumerate(colHeaders, start=0):
            colData[var].append(float(data[index]))

    fp.close()

    return 0, colData

########################################################################
# Plot

def doPlot(filePath, colHeaders, colData):

    zdr = np.array(colData["zdr"]).astype(np.double)
    elev = np.array(colData["elev"]).astype(np.double)

    minElev = float(options.minElev)
    maxElev = float(options.maxElev)

    print("  ==>> zdr: ", zdr, file=sys.stderr)
    print("  ==>> minElev: ", minElev, file=sys.stderr)
    print("  ==>> maxElev: ", maxElev, file=sys.stderr)

    zdrValid = zdr[(elev >= minElev) & (elev <= maxElev)]

    print("  ==>> size of zdr: ", len(zdr), file=sys.stderr)
    print("  ==>> size of elev: ", len(elev), file=sys.stderr)
    print("  ==>> size of zdrValid: ", len(zdrValid), file=sys.stderr)

    zdrSorted = np.sort(zdrValid)
    mean = np.mean(zdrSorted)
    sdev = np.std(zdrSorted)
    skew = stats.skew(zdrSorted)
    kurtosis = stats.kurtosis(zdrSorted)

    percPoints = np.arange(0,100,1.0)
    percs = np.percentile(zdrSorted, percPoints)

    print("  ==>> mean: ", mean, file=sys.stderr)
    print("  ==>> sdev: ", sdev, file=sys.stderr)
    print("  ==>> skew: ", skew, file=sys.stderr)
    print("  ==>> kurtosis: ", kurtosis, file=sys.stderr)
    # print >>sys.stderr, "  ==>> percs: ", percs

    widthIn = float(options.figWidthMm) / 25.4
    htIn = float(options.figHeightMm) / 25.4
    
    fig1 = plt.figure(1, (widthIn, htIn))
    title = (options.title + '  for Elev Limits [ ' +
             options.minElev + ' : ' + options.maxElev + ' ]')
    fig1.suptitle(title, fontsize=16)
    ax1 = fig1.add_subplot(2,1,1,xmargin=0.0)
    ax2 = fig1.add_subplot(2,1,2,xmargin=0.0)

    # the histogram of ZDR

    n1, bins1, patches1 = ax1.hist(zdrSorted, 60, normed=True,
                                   histtype='stepfilled',
                                   facecolor='slateblue',
                                   alpha=0.35)

    ax1.set_xlabel('ZDR')
    ax1.set_ylabel('Frequency')
    ax1.set_title('PDF - Probability Density Function', fontsize=14)
    ax1.grid(True)

    pdf = stats.norm(mean, sdev).pdf
    yy1 = pdf(bins1)
    ll1 = ax1.plot(bins1, yy1, 'b', linewidth=2)

    ax1.set_xlim([mean -sdev * 3, mean + sdev * 3])

    # CDF of ZDR

    n2, bins2, patches2 = ax2.hist(zdrSorted, 60, normed=True,
                                   cumulative=True,
                                   histtype='stepfilled',
                                   facecolor='slateblue',
                                   alpha=0.35)

    ax2.set_xlabel('ZDR')
    ax2.set_ylabel('Cumulative frequency')
    ax2.set_title('CDF - Cumulative Distribution Function', fontsize=14)
    ax2.grid(True)

    cdf = stats.norm(mean, sdev).cdf
    yy2 = cdf(bins1)
    ll2 = ax2.plot(bins1, yy2, 'b', linewidth=2,
                   label = ('NormalFit mean=' + '{:.3f}'.format(mean) +
                            ' sdev=' + '{:.3f}'.format(sdev) +
                            ' skew=' + '{:.3f}'.format(skew)))
    legend2 = ax2.legend(loc='upper left', ncol=4)
    for label in legend2.get_texts():
        label.set_fontsize('medium')

    ax2.set_xlim([mean -sdev * 3, mean + sdev * 3])

    # draw line to show mean, annotate

    pmean = pdf(mean)
    plen = pmean * 0.05
    toffx = mean * 0.1

    # draw line to show mean, annotate

    annotVal(ax1, ax2,  mean, pdf, cdf, 'mean', plen, toffx,
             'black', 'black', 'left', 'center')

    # annotate percentiles

    # perc5 = percs[6]
    # annotVal(ax1, ax2,  perc5, pdf, cdf, 'p%5', plen, toffx,
    #          'black', 'black', 'left', 'center')

    # perc15 = percs[16]
    # annotVal(ax1, ax2,  perc15, pdf, cdf, 'p%15', plen, toffx,
    #          'black', 'black', 'left', 'center')

    # perc25 = percs[26]
    # annotVal(ax1, ax2,  perc25, pdf, cdf, 'p%25', plen, toffx,
    #          'black', 'black', 'left', 'center')

    # show

    plt.show()

########################################################################
# Annotate a value

def annotVal(ax1, ax2, val, pdf, cdf, label, plen,
             toffx, linecol, textcol,
             horizAlign, vertAlign):

    pval = pdf(val)
    ax1.plot([val, val], [pval - plen, pval + plen], color=linecol, linewidth=2)
    ax1.annotate(label + '=' + '{:.3f}'.format(val),
                 xy=(val, pval + toffx),
                 xytext=(val + toffx, pval),
                 color=textcol,
                 horizontalalignment=horizAlign,
                 verticalalignment=vertAlign)

    cval = cdf(val)
    clen = 0.03
    ax2.plot([val, val], [cval - clen, cval + clen], color=linecol, linewidth=2)
    ax2.annotate(label + '=' + '{:.3f}'.format(val),
                 xy=(val, cval + toffx),
                 xytext=(val + toffx, cval),
                 color=textcol,
                 horizontalalignment=horizAlign,
                 verticalalignment=vertAlign)

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

