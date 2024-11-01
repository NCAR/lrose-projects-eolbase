#!/usr/bin/env python

#===========================================================================
#
# Produce histogram for ZDR bias from vertical pointing
#
#===========================================================================

from __future__ import print_function

import os
import sys

import math
import numpy as np
import scipy.stats as stats
import matplotlib.mlab as mlab
import matplotlib.pyplot as plt
import matplotlib.mlab as mlab
from optparse import OptionParser

def main():

#   globals

    global options

# parse the command line

    usage = "usage: " + __file__ + " [options]"
    parser = OptionParser(usage)
    parser.add_option('--debug',
                      dest='debug', default=False,
                      action="store_true",
                      help='Set debugging on')
    parser.add_option('--vert_file',
                      dest='vertFile',
                      default='../data/marshall/vert90/zdr_points_20170923_221545.txt',
                      help='File path for vert point zdr data')
    parser.add_option('--title',
                      dest='title',
                      default='ZDR DISTRIB VERT POINT',
                      help='Title for plot')
    parser.add_option('--width',
                      dest='figWidthMm',
                      default=200,
                      help='Width of figure in mm')
    parser.add_option('--height',
                      dest='figHeightMm',
                      default=150,
                      help='Height of figure in mm')
    parser.add_option('--minHt',
                      dest='minHt',
                      default='2.5',
                      help='Min height for ZDR data')
    parser.add_option('--maxHt',
                      dest='maxHt',
                      default='4.0',
                      help='Max height for ZDR data')
    parser.add_option('--setZdrRange',
                      dest='setZdrRange', default=False,
                      action="store_true",
                      help='Set the ZDR range to plot from minZdr to maxZdr. If false, we plot to 4 * stddev.')
    parser.add_option('--minZdr',
                      dest='minZdr',
                      default='-2.0',
                      help='Min val on ZDR data axis')
    parser.add_option('--maxZdr',
                      dest='maxZdr',
                      default='2.0',
                      help='Max val on ZDR axis')
    parser.add_option('--plotPercentile',
                      dest='plotPercentile', default=False,
                      action="store_true",
                      help='Plot the specified percentile value.')
    parser.add_option('--percentile',
                      dest='percentile',
                      default='10',
                      help='Percentile value to plot')

    (options, args) = parser.parse_args()
    
    # get date and time from filename

    (dir, fileName) = os.path.split(options.vertFile)
    (baseName, ext) = os.path.splitext(fileName)
    baseNameParts = baseName.split('_')
    nParts = len(baseNameParts)
    global dateStr, timeStr
    dateStr = baseNameParts[nParts-2]
    timeStr = baseNameParts[nParts-1]

    if (options.debug == True):
        print("Running " + __file__, file=sys.stderr)
        print("  vertFile: ", options.vertFile, file=sys.stderr)
        print("  fileName: ", fileName, file=sys.stderr)
        print("  dateStr: ", dateStr, file=sys.stderr)
        print("  timeStr: ", timeStr, file=sys.stderr)
    
    # read in headers

    (iret, colHeaders) = readColumnHeaders(options.vertFile)
    if (iret != 0):
        sys.exit(1)

    # read in data

    (iret, colData) = readInputData(options.vertFile, colHeaders)
    if (iret != 0):
        sys.exit(1)

    # render the plot
    
    doPlot(options.vertFile, colHeaders, colData)

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

    zdrm = np.array(colData["zdrm"]).astype(np.double)
    height = np.array(colData["height"]).astype(np.double)

    minHt = float(options.minHt)
    maxHt = float(options.maxHt)

    print("  ==>> zdrm: ", zdrm, file=sys.stderr)
    print("  ==>> minHt: ", minHt, file=sys.stderr)
    print("  ==>> maxHt: ", maxHt, file=sys.stderr)

    zdrValid = zdrm[(height >= minHt) & (height <= maxHt)]
    minZdr = -2.0
    maxZdr = 2.0
    if (options.setZdrRange):
        minZdr = float(options.minZdr)
        maxZdr = float(options.maxZdr)
        zdrValid = zdrm[(height >= minHt) & \
                        (height <= maxHt) & \
                        (zdrm >= minZdr) & \
                        (zdrm <= maxZdr)]

    print("  ==>> size of zdrm: ", len(zdrm), file=sys.stderr)
    print("  ==>> size of height: ", len(height), file=sys.stderr)
    print("  ==>> size of zdrValid: ", len(zdrValid), file=sys.stderr)

    mean = np.mean(zdrValid)
    sdev = np.std(zdrValid)
    skew = stats.skew(zdrValid)
    kurtosis = stats.kurtosis(zdrValid)

    percPoints = np.arange(0,100,1.0)
    zdrSorted = np.sort(zdrValid)
    percs = np.percentile(zdrSorted, percPoints)

    print("  ==>> mean: ", mean, file=sys.stderr)
    print("  ==>> sdev: ", sdev, file=sys.stderr)
    print("  ==>> skew: ", skew, file=sys.stderr)
    print("  ==>> kurtosis: ", kurtosis, file=sys.stderr)
    # print >>sys.stderr, "  ==>> percs: ", percs

    widthIn = float(options.figWidthMm) / 25.4
    htIn = float(options.figHeightMm) / 25.4
    
    fig1 = plt.figure(1, (widthIn, htIn))
    title = (options.title + " " + dateStr + '-' + timeStr)
    fig1.suptitle(title, fontsize=16)
    ax1 = fig1.add_subplot(1,1,1,xmargin=0.0)
    # ax2 = fig1.add_subplot(2,1,2,xmargin=0.0)

    # the histogram of ZDR

    n1, bins1, patches1 = ax1.hist(zdrSorted, 101, normed=True,
                                   histtype='stepfilled',
                                   facecolor='slateblue',
                                   alpha=0.35)

    ax1.set_xlabel('ZDR')
    ax1.set_ylabel('Frequency')
    ax1.set_title('Probability Density Function', fontsize=14)
    ax1.grid(True)

    pdf = stats.norm(mean, sdev).pdf
    yy1 = pdf(bins1)
    label1 = ('NormalFit' +
              '\nmean = ' + '{:.3f}'.format(mean) +
              '\nsdev = ' + '{:.3f}'.format(sdev) +
              '\nskew = ' + '{:.3f}'.format(skew) +
              '\nminHt = ' + options.minHt +
              '\nmaxHt = ' + options.maxHt)
    ll1 = ax1.plot(bins1, yy1, 'b', linewidth=2,
                   label = label1)
    legend1 = ax1.legend(loc='upper left', ncol=4)
    for label in legend1.get_texts():
        label.set_fontsize('medium')

    ax1.set_xlim([minZdr, maxZdr])
    
    # CDF of ZDR

    # n2, bins2, patches2 = ax2.hist(zdrSorted, 60, normed=True,
    #                                cumulative=True,
    #                                histtype='stepfilled',
    #                                facecolor='slateblue',
    #                                alpha=0.35)

    # ax2.set_xlabel('ZDR')
    # ax2.set_ylabel('Cumulative frequency')
    # ax2.set_title('CDF - Cumulative Distribution Function', fontsize=14)
    # ax2.grid(True)

    # cdf = stats.norm(mean, sdev).cdf
    # yy2 = cdf(bins1)
    # ll2 = ax2.plot(bins1, yy2, 'b', linewidth=2,
    #                label = ('NormalFit mean=' + '{:.3f}'.format(mean) +
    #                         ' sdev=' + '{:.3f}'.format(sdev) +
    #                         ' skew=' + '{:.3f}'.format(skew)))
    # legend2 = ax2.legend(loc='upper left', ncol=4)
    # for label in legend2.get_texts():
    #     label.set_fontsize('medium')

    # axis limits

    # minZdr = mean - (sdev * 3)
    # maxZdr = mean + (sdev * 3)
    # if (options.setZdrRange):
    #     minZdr = float(options.minZdr)
    #     maxZdr = float(options.maxZdr)

    #ax2.set_xlim([minZdr, maxZdr])

    # draw line to show mean, annotate

    pmean = pdf(mean)
    plen = pmean * 0.05
    toffx = mean * 0.1

    # draw line to show mean, annotate

    #annotVal(ax1, ax2,  mean, pdf, cdf, 'mean', plen, toffx,
    #         'black', 'black', 'left', 'center', 16)

    annotVal(ax1, mean, pdf, 'mean', plen, toffx,
             'black', 'black', 'left', 'center', 16)
    #annotVal(ax2, mean, cdf, 'mean', 0.03, toffx,
    #         'black', 'black', 'left', 'center', 16)

    # annotate percentiles

    if (options.plotPercentile):
        perc = percs[int(options.percentile)]
        label = 'p' + options.percentile + '%'
        #annotVal(ax2, perc, cdf, label, 0.03, toffx,
        #         'blue', 'blue', 'left', 'center', 14)

    #perc15 = percs[16]
    #annotVal(ax1, ax2,  perc15, pdf, cdf, 'p%15', plen, toffx,
    #         'black', 'black', 'left', 'center', 14)

    # perc25 = percs[26]
    # annotVal(ax1, ax2,  perc25, pdf, cdf, 'p%25', plen, toffx,
    #          'black', 'black', 'left', 'center', 14)

    # adjust margins

    fig1.tight_layout()
    fig1.subplots_adjust(bottom=0.04, left=0.07, right=0.97, top=0.88)

    # show

    plt.show()

########################################################################
# Annotate a value

# def annotVal(ax1, ax2, val, pdf, cdf, label, plen,
#              toffx, linecol, textcol,
#              horizAlign, vertAlign, fsize):

#     pval = pdf(val)
#     ax1.plot([val, val], [pval - plen, pval + plen], color=linecol, linewidth=2)
#     ax1.annotate(label + '=' + '{:.3f}'.format(val),
#                  xy=(val, pval + toffx),
#                  xytext=(val + toffx, pval),
#                  color=textcol,
#                  horizontalalignment=horizAlign,
#                  verticalalignment=vertAlign, fontsize=fsize)

#     cval = cdf(val)
#     clen = 0.03
#     ax2.plot([val, val], [cval - clen, cval + clen], color=linecol, linewidth=2)
#     ax2.annotate(label + '=' + '{:.3f}'.format(val),
#                  xy=(val, cval + toffx),
#                  xytext=(val + toffx, cval),
#                  color=textcol,
#                  horizontalalignment=horizAlign,
#                  verticalalignment=vertAlign, fontsize=fsize)

def annotVal(ax, val, distrib, label, tickLen, toffx,
             linecol, textcol, horizAlign, vertAlign, fsize):

    dval = distrib(val)
    ax.plot([val, val], [dval - tickLen, dval + tickLen],
            color=linecol, linewidth=2)
    ax.annotate(label + '=' + '{:.3f}'.format(val),
                xy=(val, dval + toffx),
                xytext=(val + toffx, dval),
                color=textcol,
                horizontalalignment=horizAlign,
                verticalalignment=vertAlign, fontsize=fsize)

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

