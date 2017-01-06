#!/bin/bash

# Set some hard coded vars here
SEARCHROOT=/media/dennis/Data/recovered/files-by-type/odt/

if [ $# -ne 1 ]; then
	echo "Usage: searchodt searchterm"
	exit 1
fi

for f in $(find $SEARCHROOT -name '*.odt'); do

#for file in $(ls *.odt); do

#    echo "Looking in: $f"

	unzip -ca "$f" content.xml | grep -ql "$1"
	if [ $? -eq 0 ]; then
		echo "$f"
	fi

done
