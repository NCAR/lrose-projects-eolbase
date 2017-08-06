#!/usr/bin/env python

#===========================================================================
#
# Produce histogram and CDF plots for ZDR bias in ice
#
#===========================================================================

import os
import sys

import numpy as np
import scipy.stats as stats
import matplotlib.mlab as mlab
import matplotlib.pyplot as plt
import matplotlib.mlab as mlab
from optparse import OptionParser

def main():

#   globals

    global options
    global zdr

# parse the command line

    usage = "usage: %prog [options]"
    parser = OptionParser(usage)
    parser.add_option('--debug',
                      dest='debug', default=False,
                      action="store_true",
                      help='Set debugging on')
    parser.add_option('--zdr_file',
                      dest='zdrFile',
                      default='./zdr.txt',
                      help='File path for bias results')
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
    (options, args) = parser.parse_args()
    
    if (options.debug == True):
        print >>sys.stderr, "Running %prog"
        print >>sys.stderr, "  zdrFile: ", options.zdrFile

    # read in data

    zdr = np.genfromtxt(options.zdrFile)

    # render the plot
    
    doPlot(zdr)

    sys.exit(0)
    
########################################################################
# Plot

def doPlot(zdr):

    zdrSorted = np.sort(zdr)
    mean = np.mean(zdrSorted)
    sdev = np.std(zdrSorted)
    skew = stats.skew(zdrSorted)
    kurtosis = stats.kurtosis(zdrSorted)

    percPoints = np.arange(0,100,1.0)
    percs = np.percentile(zdrSorted, percPoints)

    print >>sys.stderr, "  ==>> mean: ", mean
    print >>sys.stderr, "  ==>> sdev: ", sdev
    print >>sys.stderr, "  ==>> skew: ", skew
    print >>sys.stderr, "  ==>> kurtosis: ", kurtosis
    print >>sys.stderr, "  ==>> percs: ", percs

    widthIn = float(options.figWidthMm) / 25.4
    htIn = float(options.figHeightMm) / 25.4
    
    fig1 = plt.figure(1, (widthIn, htIn))
    fig1.suptitle(options.title, fontsize=18)
    ax1 = fig1.add_subplot(2,1,1,xmargin=0.0)
    ax2 = fig1.add_subplot(2,1,2,xmargin=0.0)

    # the histogram of ZDR

    n1, bins1, patches1 = ax1.hist(zdrSorted, 50, normed=True,
                                   histtype='stepfilled',
                                   facecolor='slateblue',
                                   alpha=1.0)

    ax1.set_xlabel('ZDR')
    ax1.set_ylabel('Frequency')
    ax1.set_title('PDF - Probability Density Function', fontsize=14)
    ax1.grid(True)

    pdf = stats.norm(mean, sdev).pdf
    yy1 = pdf(bins1)
    ll1 = ax1.plot(bins1, yy1, 'r', linewidth=3,
                   label = ('NormalFit mean=' + '{:.3f}'.format(mean) + 
                            ' sdev=' + '{:.3f}'.format(sdev) +
                            ' skew=' + '{:.3f}'.format(skew)))
    legend1 = ax1.legend(loc='upper left', ncol=4)
    for label in legend1.get_texts():
        label.set_fontsize('medium')

    # CDF of ZDR

    n2, bins2, patches2 = ax2.hist(zdrSorted, 50, normed=True,
                                   cumulative=True,
                                   histtype='stepfilled',
                                   facecolor='slateblue',
                                   alpha=1.0)

    ax2.set_xlabel('ZDR')
    ax2.set_ylabel('Cumulative frequency')
    ax2.set_title('CDF - Cumulative Distribution Function', fontsize=14)
    ax2.grid(True)

    cdf = stats.norm(mean, sdev).cdf
    yy2 = cdf(bins1)
    ll2 = ax2.plot(bins1, yy2, 'r', linewidth=3,
                   label = ('NormalFit mean=' + '{:.3f}'.format(mean) +
                            ' sdev=' + '{:.3f}'.format(sdev) +
                            ' skew=' + '{:.3f}'.format(skew)))
    legend2 = ax2.legend(loc='upper left', ncol=4)
    for label in legend2.get_texts():
        label.set_fontsize('medium')

    # draw line to show mean, annotate

    pmean = pdf(mean)
    plen = pmean * 0.1
    toffy = pmean * 0.025
    toffx = mean * 0.1

    annotVal(ax1, ax2,  mean, pdf, cdf, 'mean', plen, toffx, toffy, 'magenta', 'magenta')

    # draw line to show mean - 0.2, annotate
    
    annotVal(ax1, ax2,  mean - 0.2, pdf, cdf, 'mean-0.2', plen, toffx, toffy, 'magenta', 'magenta')

    # annotate percentiles

    perc5 = percs[6]
    annotVal(ax1, ax2,  perc5, pdf, cdf, 'p%5', plen, toffx, toffy, 'cyan', 'cyan')

    perc10 = percs[11]
    annotVal(ax1, ax2,  perc10, pdf, cdf, 'p%10', plen, toffx, toffy, 'cyan', 'cyan')

    perc15 = percs[16]
    annotVal(ax1, ax2,  perc15, pdf, cdf, 'p%15', plen, toffx, toffy, 'cyan', 'cyan')

    perc20 = percs[21]
    annotVal(ax1, ax2,  perc20, pdf, cdf, 'p%20', plen, toffx, toffy, 'cyan', 'cyan')

    perc25 = percs[26]
    annotVal(ax1, ax2,  perc25, pdf, cdf, 'p%25', plen, toffx, toffy, 'cyan', 'cyan')

    # show

    plt.show()

########################################################################
# Annotate a value

def annotVal(ax1, ax2, val, pdf, cdf, label, plen, toffx, toffy, linecol, textcol):

    pval = pdf(val)
    ax1.plot([val, val], [pval - plen, pval + plen], color=linecol, linewidth=3)
    ax1.annotate(label + '=' + '{:.3f}'.format(val),
                 xy=(val, pval + toffx),
                 xytext=(val + toffx, pval + toffy),
                 color=textcol)

    cval = cdf(val)
    clen = 0.1
    ax2.plot([val, val], [cval - clen, cval + clen], color=linecol, linewidth=3)
    ax2.annotate(label + '=' + '{:.3f}'.format(val),
                 xy=(val, cval + toffx),
                 xytext=(val + toffx, cval + toffy),
                 color=textcol)

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

