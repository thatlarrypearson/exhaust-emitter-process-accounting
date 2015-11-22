#!/bin/bash

pkill --full -9 acctpublish.py
pkill --full -9 accttail

. /opt/exhaust/etc/exhaust.conf

/opt/exhaust/bin/accttail | /opt/exhaust/bin/acctpublish.py
