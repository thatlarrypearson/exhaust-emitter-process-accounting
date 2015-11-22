# Exhaust Emitters - Process Accounting

Process Accounting is one type of exhaust emitter, a component of the [Exhaust Proof-of-Concept](https://github.com/ThatLarryPearson/exhaust-PoC).

Process accounting takes advantage of the GNU Accounting utilities for process and login accounting [pacct](http://www.tldp.org/HOWTO/text/Process-Accounting).  When activated, process accounting writes a record to the [process accounting file](http://linux.die.net/man/5/acct) as each process terminates.  This module takes the data from this file and pushes the data into the collector (publishes the data in the message queue).

## Installation

The first step is to install the Linux accounting software and enable process accounting with the [accton](http://linux.die.net/man/8/accton) command.
```
sudo apt-get install -y acct
sudo accton on
```

Next, you will need to make sure you have a C compiler installed:
```
sudo apt-get install -y build-essential python-software-properties software-properties-common
```

Python libraries to install:
- [pika](https://github.com/pika/pika) [docs](https://pika.readthedocs.org/en/latest/index.html)
- [sarge](https://github.com/vsajip/sarge) [docs](http://sarge.readthedocs.org/en/latest/)

Install Python `pip` and Python libraries:
```
sudo apt-get install -y python-pip
sudo -H pip install --upgrade pip
sudo pip install pika sarge
```

Use `git` to fetch the necessary files.
```
sudo apt-get install git-core
git clone https://github.com/ThatLarryPearson/exhaust-emitter-process-accounting.git
cd exhaust-emitter-process-accounting
cd src
cc accttail.c -o accttail
cd ..
sudo mkdir --parents /opt/exhaust/bin /opt/exhaust/etc
sudo cp src/accttail /opt/exhaust/bin
sudo cp opt/exhaust/bin/acctpublish.* /opt/exhaust/bin
sudo cp opt/exhaust/bin/syslogtopic.py /opt/exhaust/bin
sudo cp opt/exhaust/bin/installservice.sh /opt/exhaust/bin
sudo cp opt/exhaust/etc/exhaust.conf /opt/exhaust/etc
sudo cp etc/init/acctpublish.conf /etc/init
sudo cp etc/cron.daily/acct /etc/cron.daily
sudo chown -R root:root /opt/exhaust/bin/*
sudo chown root:root /etc/init/psutilpublish.conf
sudo chown root:root /etc/cron.daily/acct
sudo chmod 0755 /opt/exhaust /opt/exhaust/* /opt/exhaust/bin/*
sudo chmod 0755 /etc/cron.daily/acct
sudo chmod 0644 /opt/exhaust/etc/*
sudo chmod 0644 /etc/init/acctpublish.conf
sudo /opt/exhaust/bin/installservice.sh
service --status-all
service acctpublish restart
```

To test, run the `syslogtopic.py` command and you should see all of the messages flowing into the message queue:
```
/opt/exhaust/bin/syslogtopic.py
```

## Log Rotation

Since the `acct` accounting module creates its own logfile `/var/log/account/pacct`, there is a need to manage file changes during log rotation.  `acct` logging on Ubuntu 14.04 is done by the shell script `/etc/cron.daily/acct`.  We provide a modified daily cron file including a restart command for the `acctpublish` service.

## Licensing

The MIT License (MIT)

Copyright &copy; 2015 Lawrence Bennett Pearson

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
