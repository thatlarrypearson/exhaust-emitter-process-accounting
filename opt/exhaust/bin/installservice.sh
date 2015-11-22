#!/bin/bash

if [ -f /etc/init/psutilpublish.conf ]
then
	initctl emit psutilpublish
else
	exit 1
endif

if [ -f /etc/init/acctpublish.conf ]
then
	initctl emit acctpublish
else
	exit 1
endif

echo $0 `date` > /tmp/installservice.sh.out

exit 0
