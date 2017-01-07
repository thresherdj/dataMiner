#!/usr/bin/python
# -*- coding: utf_8 -*-

# Name: File Sorter (fileSorter.py)
# By: Dennis Drescher (dennis.drescher.86@gmail.com)
# Last edited: 8 Dec 2016

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

# This script is part of the Data Miner package. Its primary purpose is to
# troll through a set of files that have come from Photorec or a tool like it.
# It will sort files by file type and create folders that will hold a specified
# number of files.

###############################################################################
################################ Initialize ###################################
###############################################################################

# Import all needed Python libs
import shutil, os, sys, argparse, timeit
from collections import defaultdict
from datetime import datetime
from datetime import timedelta

# Set some global vars here
scriptName      = 'fileSorter'
scriptVersion   = '0.01'
startTime       = timeit.default_timer()


###############################################################################
################################## Begin CLI ##################################
###############################################################################

# Give a welcome message
print '\n\t\tWelcome to ' + scriptName + ' ' + scriptVersion

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


def sorter (sourcePath, targetPath, mode) :
    '''Organize the files by type. If fileType is omitted, it will arrange
    all the files in the data set by type.'''

    fileType = []
    typeDic = defaultdict(list)
    fileCount = 0
    totalFiles = 0
    dirCount = 1
    maxFiles = 100
    ext = ''

    # Set up the (master) target dir if needed
    if not os.path.isdir(targetPath) and mode != 'test' :
        os.mkdir(targetPath)
        dirCount +=1

    masterTarget    = targetPath
    curDir          = ''

    terminal('\n\nProcessing files, please wait as this might take a while.')
    for root, dirs, files in os.walk(sourcePath):
        for f in files:
            totalFiles +=1
            # We sort by extention
            ext = os.path.splitext(f)
            ext = ext[1].replace('.', '')
            if ext not in fileType :
                fileType.append(ext)
            # Add file to dict we will process further down
#            typeDic[ext].append(os.path.join(sourcePath, f))
            typeDic[ext].append(os.path.join(root, f))

            # Create a folder for each of the extention types under the
            # master folder if needed
            if not os.path.isdir(os.path.join(targetPath, ext)) and mode != 'test' :
                os.mkdir(os.path.join(targetPath, ext))


    # Now process the dict we made
    for ext, sourceFiles in typeDic.iteritems() :
#        dirCount = 1
        # Create initial target folder if needed
        curDir = os.path.join(targetPath, ext, ext + '_' + str(dirCount).zfill(3))
        if not os.path.isdir(curDir) and mode != 'test' :
            sys.stdout.write('.')
            sys.stdout.flush()
            os.mkdir(curDir)
            dirCount +=1
            fileCount = 1
        # Loop through the files in this type
        for source in sourceFiles :
            if fileCount > maxFiles :
#                sys.stdout.write('.')
#                sys.stdout.flush()
                curDir = os.path.join(targetPath, ext, ext + '_' + str(dirCount).zfill(3))
                if not os.path.isdir(curDir) and mode != 'test' :
                    sys.stdout.write('.')
                    sys.stdout.flush()
                    os.mkdir(curDir)
                    dirCount +=1
                    fileCount = 1
            # Now copy the file over to the target
            if mode == 'copy' :
                shutil.copy(source, os.path.join(curDir, os.path.basename(source)))
            elif mode == 'move' :
                shutil.move(source, os.path.join(curDir, os.path.basename(source)))

            fileCount +=1

    if  mode == 'test' :
        terminal('\nRunning in test mode. Found ' + str(totalFiles) + ' files to copy.')
        terminal('\n\nTotal files: ' + str(totalFiles) + ' / Files Copied: ' + str(fileCount))
    else :
        terminal('\n\nTotal files copied: ' + str(fileCount) + ' / Folders created: ' + str(dirCount))

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

    # This sets the mode, copy, move or test
    if args.mode :
        mode = args.mode
    else :
        sys.exit('\nERROR: Mode was not specified')


    # With all our paramters in place we can call the main function
    sorter(sourcePath, targetPath, mode)


###############################################################################
############################# Script Starts Here ##############################
###############################################################################

if __name__ == '__main__' :

    # Set up argument parser
    parser = argparse.ArgumentParser(description=scriptName)
    subparsers = parser.add_subparsers(help='sub-command help')

    # Add help subprocess arguments
    helpCommand = subparsers.add_parser('help', help='General system help')

    modeType            = ['copy', 'move', 'test']

    # Available choices
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--source_path', help='The path to the data to be mined.')
    parser.add_argument('-t', '--target_path', help='The path to where the data that is mined will go.')
    parser.add_argument('-m', '--mode', choices=modeType, help='There are three modes this script can run in. Copy files, move files, or just testing to see what files would be copied or moved.')

    # Send the collected arguments to the handler
    userArguments(parser.parse_args())

    ###########################################################################
    ######################### Close out the session ###########################
    ###########################################################################

    # In case there are any Canadians using this, politely say good bye
    timeTotal = round(timeit.default_timer() - startTime, 2)
    print '\n\t\tTotal process time: ' + str(timedelta(seconds = timeTotal)).split('.')[0] + '\n'
    print '\t\tThank you, please come again!\n'



