#!/usr/bin/python
# -*- coding: utf_8 -*-

# Name: Compare Sums (compareSums.py)
# By: Dennis Drescher (dennis.drescher.86@gmail.com)
# Last edited: 18 Dec 2016

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

# Look for the checkSumGetter log file in a folder and compare the list of
# files in it with the actual files in the folder.

###############################################################################
################################ Initialize ###################################
###############################################################################

# Import all needed Python libs
import codecs, shutil, os, sys, argparse, timeit, hashlib
from datetime import datetime
from datetime import timedelta

# Set some global vars here
scriptName      = 'Compare Sums'
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


def mdfiveSum (fname) :
    '''Get an md5 sum on a file.'''

    hash_md5 = hashlib.md5()
    with open(fname, "rb") as f :
        for chunk in iter(lambda: f.read(4096), b"") :
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


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

    try :
        # Because we want to read errors from top to bottom, we don't pre append
        # them to the error log file.
        if not os.path.isfile(log) :
            writeObject = codecs.open(log, "w", encoding='utf_8')
        else :
            writeObject = codecs.open(log, "a", encoding='utf_8')

        # Write and close
        writeObject.write(msg + '\n')
        writeObject.close()
    except :
        terminal('Error writing this event to error log: ' + msg)

    return


def compare (targetPath) :
    '''This is the main function which will go into a folder and look
    for a checkSum.txt file, then read it and compare the sums listed
    for each of the files found in the folder.'''

    # Find log file
    logFile = os.path.join(targetPath, 'checkSum.txt')
    # Bail out now if we can't find the checkSum file
    if not os.path.isfile(logFile) :
        sys.exit('\nERROR: Log file: ' + logFile + ' not found!')

    fileCount = 0
    total = 0
    terminal('\n\nProcessing files, please wait as this might take a while.')

    # Process files listed in the log file
    with codecs.open(logFile, 'rt', 'utf_8_sig') as contents :
        for line in contents :
            total +=1
            target = os.path.join(targetPath, line.split(', ')[0])
            targetSum = mdfiveSum(target)
            listSum = line.split(', ')[1].strip()
            if not os.path.isfile(target) :
                terminal('File not found: ' + target)
            if not str(targetSum) == str(listSum) :
                terminal('File not the same: ' + target)
            else :
                fileCount +=1

    terminal('\n\nMatched ' + str(fileCount) + ' of ' + str(total) + ' files')

    return


###############################################################################
############################# Command Process ###############################
###############################################################################

# The argument handler
def userArguments (args) :
    '''Process incoming command arguments.'''

#    import pdb; pdb.set_trace()

    # A valid target path must be specified
    if args.target_path :
        targetPath = args.target_path
        if not os.path.isdir(targetPath) :
            sys.exit('\nERROR: Target path <' + targetPath + '> is not valid!')
    else :
        sys.exit('\nERROR: No target path was specified')

    # With all our paramters in place we can call the main function
    compare(targetPath)


###############################################################################
############################# Script Starts Here ##############################
###############################################################################

if __name__ == '__main__' :

    # Set up argument parser
    parser = argparse.ArgumentParser(description=scriptName)
    subparsers = parser.add_subparsers(help='sub-command help')

    # Add help subprocess arguments
    helpCommand = subparsers.add_parser('help', help='General system help')

    # Available choices
    parser = argparse.ArgumentParser()
    parser.add_argument('-t', '--target_path', help='The path to where the data that is mined will go.')

    # Send the collected arguments to the handler
    userArguments(parser.parse_args())

    ###########################################################################
    ######################### Close out the session ###########################
    ###########################################################################

    # In case there are any Canadians using this, politely say good bye
    timeTotal = round(timeit.default_timer() - startTime, 2)
    print '\n\t\tTotal process time: ' + str(timedelta(seconds = timeTotal)).split('.')[0] + '\n'
    print '\t\tThank you, please come again!\n'



