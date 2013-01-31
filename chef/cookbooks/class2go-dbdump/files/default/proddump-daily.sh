#!/bin/bash -e

# do this work in mnt, don't want to use full pathnames because then they would 
# end up in the zipfile (yuck)

cd /mnt

dumpfile=proddump-`date +%F`.sql
if [ -e $dumpfile ]; then rm $dumpfile; fi
mysqldump -h prod-ro.czjqjb57rejd.us-west-2.rds.amazonaws.com -u class2go --password=class2go463 class2go > $dumpfile

zipfile=${dumpfile}.zip
if [ -e $zipfile ]; then rm $zipfile; fi
zip $zipfile $dumpfile

cd ~

dumplink=proddump-latest.sql
if [ -e $dumplink ]; then rm $dumplink; fi
ln -s /mnt/$dumpfile $dumplink

ziplink=proddump-latest.sql.zip
if [ -e $ziplink ]; then rm $ziplink; fi
ln -s /mnt/$zipfile $ziplink

cd /mnt

AGE=2
echo "Removing files >$AGE days old (in /mnt)"
find . -maxdepth 1 -type f -name proddump-\*.sql -mtime $AGE -delete -print
find . -maxdepth 1 -type f -name proddump-\*.sql.zip -mtime $AGE -delete -print
