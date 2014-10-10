#!/bin/bash

for FILE in `find . -name "fastbillreport.po"`
do 
    DIR=`dirname $FILE`
    FILENAME=`basename $FILE .po` 
    msgfmt $FILE -o $DIR/$FILENAME.mo
done
