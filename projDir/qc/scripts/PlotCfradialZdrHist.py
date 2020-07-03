#!/usr/bin/env python

#===========================================================================
#
# Produce histogram for ZDR from CfRadial file
#
#===========================================================================

import os
import sys

import numpy as np
import scipy.stats as stats
from scipy.stats import skewnorm
from scipy.stats import lognorm
from scipy.stats import weibull_max
import matplotlib.mlab as mlab
import matplotlib.pyplot as plt
import matplotlib.mlab as mlab
import math
import pyart

from math import sqrt
from math import pow
from optparse import OptionParser
from netCDF4 import Dataset

def main():

#   globals

    global options
    global appName
    global dataSet
    appName = os.path.basename(__file__)

# parse the command line

    usage = "usage: " + appName + " [options]"
    parser = OptionParser(usage)
    parser.add_option('--debug',
                      dest='debug', default=False,
                      action="store_true",
                      help='Set debugging on')
    parser.add_option('--file',
                      dest='filePath',
                      default='/scr/rain1/rsfdata/projects/pecan/cfradial/spol/partrain/sband/rhi/20150626/cfrad.20150626_000423.767_to_20150626_000727.919_SPOL_v3835_PunRhi_RHI.nc',
                      help='File path for cfradial file')
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
    
    if (options.debug):
        print("Running ", appName, file=sys.stderr)
        print("  filePath: ", options.filePath, file=sys.stderr)

    # read in CfRadial file data

    readVol(options.filePath)

    # dataSet = Dataset(options.filePath)
    # print >>sys.stderr, dataSet
    # if (dataSet.n_gates_vary == "false"):
    #     readCfradialNgatesConstant()
    # else:
    #     readCfradialNgatesVariable()

    sys.exit(0)

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
# Read in CfRadial data for constant nGates

def readCfradialNgatesConstant():

    print("  nGates are constant", file=sys.stderr)
    # print >>sys.stderr, "  ntimes", dataSet.dimensions.time

        
########################################################################
# Read in CfRadial data for variable nGates

def readCfradialNgatesVariable():

    print("  nGates are variable", file=sys.stderr)

        
########################################################################
# Read in CfRadial data volume using pyart

def readVol(filePath):

    vol = pyart.io.read_cfradial(options.filePath)
    print(vol, file=sys.stderr)
    print("type(vol): ", type(vol), file=sys.stderr)

    print("nrays: ", vol.nrays, file=sys.stderr)
    print("ngates: ", vol.ngates, file=sys.stderr)
    print("nsweeps: ", vol.nsweeps, file=sys.stderr)

    dbz = vol.get_field(0, "DBZ")
    print("dbz: ", dbz, file=sys.stderr)
    print("type(dbz): ", type(dbz), file=sys.stderr)
    print("shape(dbz): ", dbz.shape, file=sys.stderr)

    print("range: ", vol.range, file=sys.stderr)
    print("type(range): ", type(vol.range), file=sys.stderr)

        
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

    minElev = float(options.minElev)
    maxElev = float(options.maxElev)
    if (minElev != 0.0 or maxElev != 90.0):
        elev = np.array(colData["elev"]).astype(np.double)
        zdrValid = zdr[(elev >= minElev) & (elev <= maxElev)]
    else:
        zdrValid = zdr

    print("  ==>> zdr: ", zdr, file=sys.stderr)
    print("  ==>> minElev: ", minElev, file=sys.stderr)
    print("  ==>> maxElev: ", maxElev, file=sys.stderr)

    print("  ==>> size of zdr: ", len(zdr), file=sys.stderr)
    # print >>sys.stderr, "  ==>> size of elev: ", len(elev)
    print("  ==>> size of zdrValid: ", len(zdrValid), file=sys.stderr)

    zdrSorted = np.sort(zdrValid)
    mean = np.mean(zdrSorted)
    sdev = np.std(zdrSorted)
    variance = sdev * sdev
    skew = stats.skew(zdrSorted)
    kurtosis = stats.kurtosis(zdrSorted)
    median = zdrSorted[len(zdrSorted)/2]
    lna = median - (variance / 2.0 * (mean - median))

    percPoints = np.arange(0,100,1.0)
    percs = np.percentile(zdrSorted, percPoints)

    print("  ==>> mean: ", mean, file=sys.stderr)
    print("  ==>> median: ", median, file=sys.stderr)
    print("  ==>> sdev: ", sdev, file=sys.stderr)
    print("  ==>> variance: ", variance, file=sys.stderr)
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
    ax1Xlims=ax1.get_xlim()

    print("1111111111111111111111111111", file=sys.stderr)
    ae, loce, scalee=skewnorm.fit(zdrValid)
    print("2222222222222222222222222222", file=sys.stderr)
    print("  ==>> ae: ", ae, file=sys.stderr)
    print("  ==>> loce: ", loce, file=sys.stderr)
    print("  ==>> scalee: ", scalee, file=sys.stderr)
    xmin, xmax = ax2.get_xlim()
    xplot = np.linspace(xmin, xmax, 60)

    tt = 2.0 / 3.0
    deltt = pow(math.fabs(skew), tt)
    piBy2 = math.pi / 2.0
    piFac = pow(((4.0 - math.pi) / 2.0), tt)
    del1 = sqrt((piBy2 * deltt) / (deltt + piFac))
    alpha = del1 / math.sqrt(1.0 - del1 * del1)
    print("  ==>> del1: ", del1, file=sys.stderr)
    print("  ==>> alpha: ", alpha, file=sys.stderr)
    
    pd2 = skewnorm.pdf(xplot,ae, loce, scalee)
    ll2 = ax1.plot(xplot, pd2, 'r', linewidth=2)

    # pd3 = skewnorm.pdf(xplot, alpha, loce, scalee)#.rvs(100)
    # ll3 = ax1.plot(xplot, pd3, 'g', linewidth=2)

    zdrLinear = np.exp(zdrValid / 10.0)
    a4, loc4, scale4 = lognorm.fit(zdrValid)
    print("  ==>> a4: ", a4, file=sys.stderr)
    print("  ==>> loc4: ", loc4, file=sys.stderr)
    print("  ==>> scale4: ", scale4, file=sys.stderr)

    pd4 = lognorm.pdf(xplot, a4, loc4, scale4)
    ll4 = ax1.plot(xplot, pd4, 'k', linewidth=2)

    a5, loc5, scale5 = weibull_max.fit(zdrValid)
    print("  ==>> a5: ", a5, file=sys.stderr)
    print("  ==>> loc5: ", loc5, file=sys.stderr)
    print("  ==>> scale5: ", scale5, file=sys.stderr)

    pd5 = weibull_max.pdf(xplot, a5, loc5, scale5)
    ll5 = ax1.plot(xplot, pd5, 'o', linewidth=2)

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
    ax2.set_xlim(ax1Xlims)

    cdf = stats.norm(mean, sdev).cdf
    yy2 = cdf(bins1)
    ll2 = ax2.plot(bins1, yy2, 'b', linewidth=2,
                   label = ('NormalFit mean=' + '{:.3f}'.format(mean) +
                            ' sdev=' + '{:.3f}'.format(sdev) +
                            ' skew=' + '{:.3f}'.format(skew)))

    cdf4 = stats.lognorm(a4, loc4, scale4).cdf
    yy4 = cdf4(bins1)
    ll4 = ax2.plot(bins1, yy4, 'k', linewidth=2,
                   label = ('LogNormalFit a4=' + '{:.3f}'.format(a4) +
                            ' loc4=' + '{:.3f}'.format(loc4) +
                            ' scale4=' + '{:.3f}'.format(scale4)))

    legend2 = ax2.legend(loc='upper left', ncol=1)
    for label in legend2.get_texts():
        label.set_fontsize('medium')

    # ax2.set_xlim([mean -sdev * 3, mean + sdev * 3])

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

