#!/usr/bin/python
# -*- coding: utf_8 -*-

# Name: Check Sum Getter (checkSumGetter.py)
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

# This will create a text file that contains a list of files with their check
# sums for future comparison.

###############################################################################
################################ Initialize ###################################
###############################################################################

# Import all needed Python libs
import codecs, shutil, os, sys, argparse, timeit, hashlib
from datetime import datetime
from datetime import timedelta

# Set some global vars here
scriptName      = 'Check Sum Getter'
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


def sumUp (targetPath) :
    '''This is the main function which will go into a folder and get the
    sum of all the files there. It is not recursive.'''

    # Create log file
    logFile = os.path.join(targetPath, 'checkSum.txt')
    if os.path.isfile(logFile) :
        os.remove(logFile)

    terminal('\n\nProcessing files, please wait as this might take a while.')

    files = [f for f in os.listdir(targetPath) if os.path.isfile(os.path.join(targetPath, f))]

    for f in files :
        md5 = mdfiveSum(os.path.join(targetPath, f))
        writeToLog(f + ', ' + md5, logFile)

    terminal('\n\nTotal files: ' + str(len(files)))

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
    sumUp(targetPath)


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



