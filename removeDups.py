#!/usr/bin/python
# -*- coding: utf_8 -*-

# Name: Remove Duplicates (removeDups.py)
# By: Dennis Drescher (dennis.drescher.86@gmail.com)
# Last edited: 6 Jan 2017

#    Copyright 2017, Dennis Drescher
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

# This will remove duplicate files from a folder. The bulk of this script was
# shamlessly copied from Stack Overflow from this thread:
#   http://stackoverflow.com/questions/748675/finding-duplicate-files-and-removing-them
# The description there is as follows: "This version uses the file size and a
# hash of the contents to find duplicates. You can pass it multiple paths, it
# will scan all paths recursively and report all duplicates found."

###############################################################################
################################ Initialize ###################################
###############################################################################

# Import all needed Python libs
import sys, os, hashlib, timeit, argparse
from collections import defaultdict
from datetime import datetime
from datetime import timedelta

# Set some global vars here
scriptName      = 'removeDups'
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


def chunk_reader(fobj, chunk_size=1024):
    '''Generator that reads a file in chunks of bytes'''

    while True:
        chunk = fobj.read(chunk_size)
        if not chunk:
            return
        yield chunk


def remover(path, mode, hash=hashlib.sha1):
    '''This is the main part of the script where we generate the sums and
    check for duplicates. There's a lot of vodo going on here and I do not
    own most of this code.'''

    dups = 0
    hashes = {}
    for dirpath, dirnames, filenames in os.walk(path):
        for filename in filenames:
            full_path = os.path.join(dirpath, filename)
            hashobj = hash()
            for chunk in chunk_reader(open(full_path, 'rb')):
                hashobj.update(chunk)
            file_id = (hashobj.digest(), os.path.getsize(full_path))
            duplicate = hashes.get(file_id, None)
            if duplicate :
                dups +=1
#                    print full_path
                sys.stdout.write('.')
                sys.stdout.flush()
#                print "\nDuplicate found: %s and %s" % (full_path, duplicate)
                if mode != 'test' :
                    try:
                        os.remove(full_path)
                    except OSError:
                        pass                
            else:
                hashes[file_id] = full_path

    if mode == 'test' :
        if dups > 0 :
            terminal('\nTotal duplicate files found: ' + str(dups))
        else :
            terminal('\nNo duplicate files found.')
    else :
        if dups > 0 :
            terminal('\nTotal duplicate files removed: ' + str(dups))
        else :
            terminal('\nNo duplicate files removed.')


## Simple CLI interface
#if sys.argv[1:]:
#    check_for_duplicates(sys.argv[1:])
#else:
#    print "Please pass the paths to check as parameters to the script"
    
    

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

    # This sets the mode, copy, move or test
    if args.mode :
        mode = args.mode
    else :
        sys.exit('\nERROR: Mode was not specified')


    # With all our paramters in place we can call the main function
    remover(sourcePath, mode)


###############################################################################
############################# Script Starts Here ##############################
###############################################################################

if __name__ == '__main__' :

    # Set up argument parser
    parser = argparse.ArgumentParser(description=scriptName)
    subparsers = parser.add_subparsers(help='sub-command help')

    # Add help subprocess arguments
    helpCommand = subparsers.add_parser('help', help='General system help')

    modeType            = ['remove', 'test']

    # Available choices
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--source_path', help='The path to the data to be mined.')
    parser.add_argument('-m', '--mode', choices=modeType, help='There are two modes this script can run in. You can remove files or just test to see what files could be removed.')

    # Send the collected arguments to the handler
    userArguments(parser.parse_args())

    ###########################################################################
    ######################### Close out the session ###########################
    ###########################################################################

    # In case there are any Canadians using this, politely say good bye
    timeTotal = round(timeit.default_timer() - startTime, 2)
    print '\n\t\tTotal process time: ' + str(timedelta(seconds = timeTotal)).split('.')[0] + '\n'
    print '\t\tThank you, please come again!\n'




