#!/usr/bin/python
# -*- coding: utf_8 -*-

# Name: Remove Duplicates (removeDups.py)
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
import sys, os, hashlib


###############################################################################
############################## Script Functions ###############################
###############################################################################

# Define functions
def chunk_reader(fobj, chunk_size=1024):
    '''Generator that reads a file in chunks of bytes'''

    while True:
        chunk = fobj.read(chunk_size)
        if not chunk:
            return
        yield chunk


def check_for_duplicates(paths, hash=hashlib.sha1):
    '''This is the main part of the script where we generate the sums and
    check for duplicates. There's a lot of vodo going on here and I do not
    own most of this code.'''

    dups = 0
    hashes = {}
    for path in paths:
        for dirpath, dirnames, filenames in os.walk(path):
            for filename in filenames:
                full_path = os.path.join(dirpath, filename)
                hashobj = hash()
                for chunk in chunk_reader(open(full_path, 'rb')):
                    hashobj.update(chunk)
                file_id = (hashobj.digest(), os.path.getsize(full_path))
                duplicate = hashes.get(file_id, None)
                if duplicate:
                    dups +=1
                    sys.stdout.write('.')
                    sys.stdout.flush()
#                    print "\nDuplicate found: %s and %s" % (full_path, duplicate)
                    try:
                        os.remove(full_path)
                    except OSError:
                        pass                
                else:
                    hashes[file_id] = full_path

    if dups > 0 :
        print '\nTotal duplicate files found: ' + str(dups)
    else :
        print '\nNo duplicate files found.'


# Simple CLI interface
if sys.argv[1:]:
    check_for_duplicates(sys.argv[1:])
else:
    print "Please pass the paths to check as parameters to the script"
