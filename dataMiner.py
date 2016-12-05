#!/usr/bin/python
# -*- coding: utf_8 -*-

# Name: Data Miner (dataMiner.py)
# By: Dennis Drescher (dennis.drescher.86@gmail.com)
# Last edited: 3 Dec 2016

#    Copyright 2016, Dennis Drescher
#    All rights reserved.
#
#    This library is free software; you can redistribute it and/or modify
#    it under the terms of the GNU Lesser General Public License as published
#    by the Free Software Foundation; either version 2.1 of License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
#    Lesser General Public License for more details.

###############################################################################
######################### Description/Documentation ###########################
###############################################################################

# Providing a couple basic paramters, this script will copy or move files from
# a set of files. It will walk a tree and choose files that meet the paramters
# provided. It has a test mode so it can do a dry run to see how many files and
# folders will be created. Remember, its miner, not minor. :-)

###############################################################################
################################ Initialize ###################################
###############################################################################

# Import all needed Python libs
import codecs, shutil, os, sys, argparse, timeit
from datetime import datetime
from datetime import timedelta

# Set some global vars here
systemName      = 'dataMiner'
systemVersion   = '0.01'
startTime       = timeit.default_timer()


###############################################################################
################################## Begin CLI ##################################
###############################################################################

# Give a welcome message
print '\n\t\tWelcome to ' + systemName + ' ' + systemVersion

###############################################################################
############################## Script Functions ###############################
###############################################################################

# Define functions

def tStamp () :
    '''Create a simple time stamp for logging and timing purposes.'''

    return str(datetime.now()).split(".")[0]


def wordWrap (text, width) :
    '''A word-wrap function that preserves existing line breaks
        and most spaces in the text. Expects that existing line
        breaks are linux style newlines (\n).'''

    def func(line, word) :
        nextword = word.split("\n", 1)[0]
        n = len(line) - line.rfind('\n') - 1 + len(nextword)
        if n >= width:
            sep = "\n"
        else:
            sep = " "
        return '%s%s%s' % (line, sep, word)
    text = text.split(" ")
    while len(text) > 1:
        text[0] = func(text.pop(0), text[0])
    return text[0]


def terminal (msg) :
    '''Send a message to the terminal with a little formating to make it
    look nicer.'''

    # Output the message and wrap it if it is over 60 chars long.
    print wordWrap(msg, 60).encode(sys.getfilesystemencoding())


def writeToLog (msg, log) :
    '''Write to the session log file.'''
    
    # Build the event line
    eventLine = tStamp() + ' : ' + msg

    try :
        # Because we want to read errors from top to bottom, we don't pre append
        # them to the error log file.
        if not os.path.isfile(log) :
            writeObject = codecs.open(log, "w", encoding='utf_8')
        else :
            writeObject = codecs.open(log, "a", encoding='utf_8')

        # Write and close
        writeObject.write(eventLine + '\n')
        writeObject.close()
    except :
        terminal('Error writing this event to error log: ' + eventLine)

    return


def dig (sourcePath, targetPath, fileType, sizeMultiplier='bt', fileSize=1, targetDirs=None, mode='test', log=None) :
    '''Dig is what we do and the ground (source) is where the data is. This
    starts the process and from here we find the data, sift through it and
    then move or copy it to where we need it to go.'''

    # Use float() rather than int() so decimals can be used in file sizes
    fs = float(fileSize)
    totalFiles = 0
    fileCount = 0
    dirCount = 1

    # Set up the target dir if needed
    if targetDirs :
        targetDirs = int(targetDirs)
        curDir = os.path.join(targetPath, 'dir_' + str(dirCount).zfill(3))
        if not os.path.isdir(curDir) :
            if mode != 'test' :
                os.mkdir(curDir)
            dirCount +=1
    else :
        curDir = targetPath

    # Create log file path
    if log :
        logFile = os.path.join(targetPath, 'dataMiner_log.txt')
        if os.path.isfile(logFile) :
            os.remove(logFile)
        writeToLog('Open log\nSource Path: ' + sourcePath + '\n\n', logFile)

    if sizeMultiplier == 'bt' :
        ms = fs
    elif sizeMultiplier == 'kb' :
        ms = fs * 1024
    elif sizeMultiplier == 'mb' :
        ms = fs * 1048576
    elif sizeMultiplier == 'gb' :
        ms = fs * 1073741824

    terminal('\n\nProcessing files, please wait as this might take a while.')
    for root, dirs, files in os.walk(sourcePath):
        for f in files:
            if targetDirs :
                if fileCount >= targetDirs : 
                    curDir = os.path.join(targetPath, 'dir_' + str(dirCount).zfill(3))
                    if not os.path.isdir(curDir) :
                        if mode != 'test' :
                            os.mkdir(curDir)
                    fileCount = 0
                    dirCount +=1
                    sys.stdout.write('.')
                    sys.stdout.flush()
            source = os.path.join(root, f)
            # Look only at the file type we want
            ext = os.path.splitext(f)
            ext = ext[1].replace('.', '')
            if ext in fileType :
                size = os.path.getsize(source)
                # evaluate by size
                if ( int(size) >= int(ms) ) :
                    fileCount +=1
                    totalFiles +=1
                    if mode != 'test' :
                        shutil.copy(source, os.path.join(curDir, f))
                    if log :
                        writeToLog('File: ' + f + ' : ' + str(size), logFile)

    terminal('\n\nTotal files copied: ' + str(totalFiles) + ' / Folders created: ' + str(dirCount))
    writeToLog('Total files copied: ' + str(totalFiles) + ' / Folders created: ' + str(dirCount), logFile)

    return


###############################################################################
############################# Command Process ###############################
###############################################################################

# The argument handler
def userArguments (args) :
    '''Process incoming command arguments.'''

#    import pdb; pdb.set_trace()

    # Check the source (the ground) where we're going to dig.
    if args.source_path :
        sourcePath = args.source_path
        if not os.path.isdir(sourcePath) :
            sys.exit('\nERROR: Source path <' + sourcePath + '> is not valid!')
    else :
        sys.exit('\nERROR: No source path was specified!')

    # A valid target path must be specified
    if args.target_path :
        targetPath = args.target_path
        if not os.path.isdir(targetPath) :
            sys.exit('\nERROR: Target path <' + targetPath + '> is not valid!')
    else :
        sys.exit('\nERROR: No target path was specified')

    # We will only allow the digging to be for more than one type of file at a time
    # which must be specified in a list.
    if args.file_type :
        fileType = args.file_type.lower()
        if type(fileType) != list :
            fileType = fileType.split()
    else :
        sys.exit('\nERROR: No file type was specified')

    # If this isn't used a default will be assigned
    if args.size_multiplier :
        sizeMultiplier = args.size_multiplier
    else :
        sizeMultiplier = None

    # Same as the previous setting
    if args.file_size :
        fileSize = args.file_size
    else :
        fileSize = None

    # The default is None which will cause the script to put all the 
    # files copied/moved into one folder. Otherwise, the number given
    # will be the number of files copied into a folder.
    if args.target_dirs :
        targetDirs = args.target_dirs
    else :
        move = None

    # The default is to copy the file, this gives the option to move it
    if args.mode :
        mode = args.mode
    else :
        sys.exit('\nERROR: Mode was not specified')

    # The default is to have no log file.
    if args.log :
        log = args.log

    # With all our paramters in place we can call the main function
    dig(sourcePath, targetPath, fileType, sizeMultiplier, fileSize, targetDirs, mode, log)


###############################################################################
############################# Script Starts Here ##############################
###############################################################################

if __name__ == '__main__' :

    # Set up argument parser
    parser = argparse.ArgumentParser(description=systemName)
    subparsers = parser.add_subparsers(help='sub-command help')

    # Add help subprocess arguments
    helpCommand = subparsers.add_parser('help', help='General system help')

    sizeType            = ['bt', 'kb', 'mb', 'gb']
    modeType            = ['copy', 'move', 'test']

    # Available choices
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--source_path', help='The path to the data to be mined.')
    parser.add_argument('-t', '--target_path', help='The path to where the data that is mined will go.')
    parser.add_argument('-y', '--file_type', help='The type of file to be mined.')
    parser.add_argument('-m', '--size_multiplier', choices=sizeType, help='The byte data size multiplier.')
    parser.add_argument('-f', '--file_size', help='The minumum size of the data files. This number must be a multiple of a byte.')
    parser.add_argument('-d', '--target_dirs', help='The number of files that will go in a folder. None is the default which means no folders will be made. All the files will be copied/moved into the target path.')
    parser.add_argument('-o', '--mode', choices=modeType, help='There are three modes this script can run in. Copy files, move files, or just testing to see what files would be copied or moved.')
    parser.add_argument('-l', '--log', action='store_true', help='This switch will cause a log file to be created in the target folder.')

    # Send the collected arguments to the handler
    userArguments(parser.parse_args())

    ###########################################################################
    ######################### Close out the session ###########################
    ###########################################################################

    # In case there are any Canadians using this, politely say good bye
    timeTotal = round(timeit.default_timer() - startTime, 2)
    print '\n\t\tTotal process time: ' + str(timedelta(seconds = timeTotal)).split('.')[0] + '\n'
    print '\t\tThank you, please come again!\n'



