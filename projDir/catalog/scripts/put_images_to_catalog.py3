#!/usr/bin/env python

#===========================================================================
#
# Put image data to catalog
#
#===========================================================================

from __future__ import print_function
import os
import sys
from stat import *
import time
import datetime
from datetime import timedelta
import string
import ftplib
import subprocess
from optparse import OptionParser

def main():

    appName = os.path.basename(__file__)
    
    global options
    global ftpUser
    global ftpPassword

    ftpUser = "anonymous"
    ftpPassword = "front@ucar.edu"

    # parse the command line

    parseArgs()

    # initialize
    
    if (options.debug == True):
        print("=======================================================", file=sys.stderr)
        print("BEGIN: " + appName + " " + str(datetime.datetime.now()), file=sys.stderr)
        print("=======================================================", file=sys.stderr)

    #   compute valid time string

    validTime = time.gmtime(int(options.validTime))
    year = int(validTime[0])
    month = int(validTime[1])
    day = int(validTime[2])
    hour = int(validTime[3])
    minute = int(validTime[4])
    sec = int(validTime[5])
    validDayStr = "%.4d%.2d%.2d" % (year, month, day)
    validTimeStr = "%.4d%.2d%.2d%.2d%.2d" % (year, month, day, hour, minute)
    dateTimeStr = "%.4d%.2d%.2d-%.2d%.2d%.2d" % (year, month, day, hour, minute, sec)

    # compute full path of image
    
    fullFilePath = options.imageDir
    fullFilePath = os.path.join(fullFilePath, options.fileName);

    # extract the platform and product from the file name.
    # The image files are named like:
    #   <category>.<legend_label>.<button_label>.<platform>.<time>.png.
    
    file_tokens = options.fileName.split(".")
    if (options.debug == True):
        print("filename toks: ", file=sys.stderr)
        print(file_tokens, file=sys.stderr)

    if len(file_tokens) != 6:
        print("*** Invalid file name: ", options.fileName, file=sys.stderr)
        sys.exit(0)

    # category

    category = file_tokens[0]
    if (options.category.find("NONE") < 0):
        category = options.category

    # field
        
    field_name = file_tokens[2]

    # platform name

    platform = file_tokens[3]
    if (options.platform.find("NONE") < 0):
        platform = options.platform

    # time - use from latest data file
    # time_tokens = file_tokens[4].split(".")
    # validTimeStr = time_tokens[0];

    # compute catalog file name

    catalogName = (category + "." + platform + "." +
                   validTimeStr + "." +
                   field_name + "." + "png")

    if (options.debug == True):
        print("catalogName: ", catalogName, file=sys.stderr)

    # put the image file

    putFile(fullFilePath, catalogName)

    #  # put the associated XML file
    #  xmlFilePath = os.path.join(options.imageDir, options.fileName[:-3] + "xml")
    #  xmlCatalogName = options.category + "." + platform + "." + validTimeStr + "." + product + ".xml"
    #  putFile(xmlFilePath, xmlCatalogName)

    # optionally move the file

    if (options.moveAfterCopy == True):

        targetDir = options.imageDir
        targetDir = os.path.join(targetDir, validDayStr);
        targetPath = os.path.join(targetDir, options.fileName);

        if (options.debug):
            print("Moving file: ", fullFilePath, file=sys.stderr)
            print("        to: ", targetPath, file=sys.stderr)
        if not os.path.exists(targetDir):
            os.makedirs(targetDir)
            
        cmd = "/bin/mv -f " + fullFilePath + " " + targetDir
        runCommand(cmd)

    # optionally remove the file

    if (options.removeAfterCopy == True):
        if (options.debug):
            print("Removing file: ", fullFilePath, file=sys.stderr)
        os.remove(fullFilePath)

    # let the user know we are done

    if (options.debug == True):
        print("=======================================================", file=sys.stderr)
        print("END: " + appName + " " + str(datetime.datetime.now()), file=sys.stderr)
        print("=======================================================", file=sys.stderr)

    sys.exit(0)

########################################################################
# Put the specified file

def putFile(filePath, catalogName):

    if (options.debug == True):
        print("Handling file: ", filePath, file=sys.stderr)
        print("  catalogName: ", catalogName, file=sys.stderr)

    # create tmp dir if necessary

    catalog_name = os.environ['catalog_name']
    imageDir = os.path.join(catalog_name, "raw/tmp/images")
    dataDir = os.environ['DATA_DIR']
    tmpDir = os.path.join(dataDir, imageDir)
    if (options.debug == True):
        print("  tmpDir: ", tmpDir, file=sys.stderr)
    if not os.path.exists(tmpDir):
        os.makedirs(tmpDir)

    # copy the file to the tmp directory

    tmpPath = os.path.join(tmpDir, catalogName)
    cmd = "cp " + filePath + " " + tmpPath
    runCommand(cmd)

    # send the file to the catalog
    
    ftpFile(catalogName, tmpPath)

    # remove the tmp file

    os.remove(tmpPath)

    return 0
    
########################################################################
# Ftp the file

def ftpFile(fileName, filePath):

    # set ftp debug level

    if (options.debug == True):
        ftpDebugLevel = 2
    else:
        ftpDebugLevel = 0
    
    targetDir = options.targetDir
    ftpServer = options.ftpServer
    
    # open ftp connection
    
    ftp = ftplib.FTP(ftpServer, ftpUser, ftpPassword)
    ftp.set_debuglevel(ftpDebugLevel)
    
    # go to target dir

    if (options.debug == True):
        print("ftp cwd to: " + targetDir, file=sys.stderr)
    
    ftp.cwd(targetDir)

    # put the file

    if (options.debug == True):
        print("putting file: ", filePath, file=sys.stderr)

    fp = open(filePath, 'rb')
    ftp.storbinary('STOR ' + fileName, fp)
    
    # close ftp connection
                
    ftp.quit()

    return

########################################################################
# Parse the command line

def parseArgs():
    
    global options

    # parse the command line

    usage = "usage: %prog [options]"
    parser = OptionParser(usage)

    # these options come from the ldata info file

    parser.add_option('--debug',
                      dest='debug', default='False',
                      action="store_true",
                      help='Set debugging on')
    parser.add_option('--unix_time',
                      dest='validTime',
                      default=0,
                      help='Valid time for image')
    parser.add_option('--full_path',
                      dest='imageDir',
                      default='unknown',
                      help='Full path of image file')
    parser.add_option('--file_name',
                      dest='fileName',
                      default='unknown',
                      help='Name of image file')
    parser.add_option('--rel_file_path',
                      dest='relFilePath',
                      default='unknown',
                      help='Relative path of image file')

    # these options are specific to the image type

    parser.add_option('--ftp_server',
                      dest='ftpServer',
                      default='catalog.eol.ucar.edu',
                      help='Target FTP server')
    catalog_name = os.environ['catalog_name']
    defaultTargetDir = 'pub/incoming/catalog/' + catalog_name
    parser.add_option('--target_dir',
                      dest='targetDir',
                      default=defaultTargetDir,
                      help='Target directory on the FTP server')
    parser.add_option('--category',
                      dest='category',
                      default='NONE',
                      help='Category portion of the catalog file name')
    parser.add_option('--platform',
                      dest='platform',
                      default='NONE',
                      help='Platform portion of the catalog file name.  Overrides platform in image file name if specified.')
    parser.add_option('--move_after_copy',
                      dest='moveAfterCopy', default='False',
                      action="store_true",
                      help='Move files to time dir after copy to ftp server')
    parser.add_option('--remove_after_copy',
                      dest='removeAfterCopy', default='False',
                      action="store_true",
                      help='Remove files after copy to ftp server')

    (options, args) = parser.parse_args()

    if (options.debug == True):
        print("Options:", file=sys.stderr)
        print("  debug? ", options.debug, file=sys.stderr)
        print("  validTime: ", options.validTime, file=sys.stderr)
        print("  imageDir: ", options.imageDir, file=sys.stderr)
        print("  relFilePath: ", options.relFilePath, file=sys.stderr)
        print("  fileName: ", options.fileName, file=sys.stderr)
        print("  ftpServer: ", options.ftpServer, file=sys.stderr)
        print("  targetDir: ", options.targetDir, file=sys.stderr)
        print("  category: ", options.category, file=sys.stderr)
        print("  platform: ", options.platform, file=sys.stderr)
        print("  moveAfterCopy: ", options.moveAfterCopy, file=sys.stderr)
        print("  removeAfterCopy: ", options.removeAfterCopy, file=sys.stderr)

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
# kick off main method

if __name__ == "__main__":

   main()
