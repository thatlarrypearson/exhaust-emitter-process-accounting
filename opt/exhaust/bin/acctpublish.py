#!/usr/bin/python
#
# acctpublish.py
#
# Description:
#
# Arguments:
#	None - See Environment Variables for AMQP Connection Information
#
# Environment Varaibles:
# - AMQP Connection Information:
#
# Dependencies:
#	- pika==0.10.0
#	- sarge==0.1.4
#
# Published Data Format:
#   {
#      "TAGS":".source.s_acct",
#      "SOURCEIP":"127.0.0.1",
#      "PROGRAM":"acctpublish",
#      "PRIORITY":"info",
#      "MESSAGE":"<acct-record>",
#      "LEGACY_MSGHDR":"acct: ",
#      "HOST_FROM":"<hostname>",
#      "HOST":"<hostname>",
#      "FACILITY":"daemon",
#      "DATE":"<date>"
#      "UTC-TIMESTAMP":"<utc-timestamp>"
#   }
#
# Usage:
#	accttail | acctpublish.py
#
# See Also:
#	- accttail.c
#	- syslogtopic.py
#	- syslogtopicpprint.py

import pika
import json
import sys
import os
import datetime

from sarge import get_stdout

settings = {}

defaults = {
    "pikahost":                   "localhost",
    "pikaport":                   5672,
    "pikavirtual-host":           None,
    "pikausername":               "guest",
    "pikapassword":               "guest",
    "pikachannel-max":            None,
    "pikaframe-max":              None,
    "pikaheartbeat-interval":     None,
    "pikassl":                    None,
    "pikassl-options":            None,
    "pikaconnection-attempts":    32768,
    "pikaretry-delay":            5,
    "pikasocket-timeout":         5,
    "pikalocale":                 None,
    "pikabackpressure-detection": None,
    }

users = {}
groups = {}
def uid2userinfo(uid):
    if uid in users:
        return users[uid]
    else:
        with open("/etc/passwd", mode='r') as f:
            for line in f:
                a = line.split(":")
                users[a[2]] = {
                    "username": a[0],
                    "default-gid": a[3],
                    "default-groupname": gid2groupname(a[3])
                }
                # print "users[%s] = %s" % (a[2], repr(users[a[2]]), )
    if uid in users:
        return users[uid]
    return None

def uid2username(uid):
    if uid in users:
        return users[uid]["username"]
    rtnVal = uid2userinfo(uid)
    if rtnVal:
        return rtnVal["username"]
    return None

def uid2default_groupname(uid):
    if uid in users:
        return users[uid]["default-groupname"]
    rtnVal = uid2userinfo(uid)
    if rtnVal:
        return rtnVal["default-groupname"]
    return None

def gid2groupname(gid):
    if gid in groups:
        return groups[gid]
    else:
        with open("/etc/group", mode='r') as f:
            for line in f:
                a = line.split(":")
                groups[a[2]] = a[0]
                # print "groups[%s]=%s" % (a[2], a[0], )
    if gid in groups:
        return groups[gid]
    return None

def hostname():
    s = get_stdout("hostname")
    # print "hostname=%s" % (s.strip(), )
    return s.strip()

def ipaddress():
    s = get_stdout("hostname -I")
    a = s.split()
    # print "ipaddress=%s" % (a[0], )
    return a[0]

def environmentvariable(name):
    if name in os.environ:
        return os.environ[name]
    elif name in defaults:
        return defaults[name]
    else:
        return None

ac_flag_enum = {
    "AFORK": 1,
    "ASU": 2,
    "ACORE": 8,
    "AXSIG": 16,
}
def ac_flag(name, val):
    if name in ac_flag_enum:
        if ac_flag_enum[name] & int(val):
            return True
    return False

def nixtime2utc(str):
    t = datetime.datetime.utcfromtimestamp(int(str))
    return t.isoformat()

def acctparse(data):
    a = data.split(",")
    rtnVal = {}
    rtnVal['ac_flag']		= a[0]
    rtnVal['AFORK']         = ac_flag("AFORK", a[0])
    rtnVal['ASU']           = ac_flag("ASU", a[0])
    rtnVal['ACORE']         = ac_flag("ACORE", a[0])
    rtnVal['AXSIG']         = ac_flag("AXSIG", a[0])
    rtnVal['ac_version']	= a[1]
    rtnVal['ac_tty']		= a[2]
    rtnVal['ac_exitcode']	= a[3]
    rtnVal['ac_uid']		= a[4]
    rtnVal['username']          = uid2username(a[4])
    rtnVal['default-groupname'] = uid2default_groupname(a[4])
    rtnVal['ac_gid']		= a[5]
    rtnVal['groupname']         = gid2groupname(a[5])
    rtnVal['ac_pid']		= a[6]
    rtnVal['ac_ppid']		= a[7]
    rtnVal['ac_btime']		= a[8]
    rtnVal['process-creation-time'] = nixtime2utc(a[8])
    rtnVal['ac_etime']		= a[9]
    rtnVal['ac_utime']		= a[10]
    rtnVal['ac_stime']		= a[11]
    rtnVal['ac_mem']		= a[12]
    rtnVal['acminflt']		= a[13]
    rtnVal['acmajflt']		= a[14]
    rtnVal['ac_comm']		= a[15].strip()

    return rtnVal

settings["pikahost"]                   = environmentvariable("pikahost")
settings["pikaport"]                   = int(environmentvariable("pikaport"))
settings["pikavirtual-host"]           = environmentvariable("pikavirtual-host")
settings["pikausername"]               = environmentvariable("pikausername")
settings["pikapassword"]               = environmentvariable("pikapassword")
settings["pikachannel-max"]            = environmentvariable("pikachannel-max")
settings["pikaframe-max"]              = environmentvariable("pikaframe-max")
settings["pikaheartbeat-interval"]     = environmentvariable("pikaheartbeat-interval")
settings["pikassl"]                    = environmentvariable("pikassl")
settings["pikassl-options"]            = environmentvariable("pikassl-options")
settings["pikaconnection-attempts"]    = environmentvariable("pikaconnection-attempts")
settings["pikaretry-delay"]            = environmentvariable("pikaretry-delay")
settings["pikasocket-timeout"]         = environmentvariable("pikasocket-timeout")
settings["pikalocale"]                 = environmentvariable("pikalocale")
settings["pikabackpressure-detection"] = environmentvariable("pikabackpressure-detection")


settings["ipaddress"] = ipaddress()
settings["hostname"] = hostname()

# connection = pika.BlockingConnection(pika.URLParameters('amqp://guest:guest@localhost:5672/%2F'))
connection = pika.BlockingConnection(pika.ConnectionParameters(
        host=settings["pikahost"],
        port=settings["pikaport"],
        virtual_host=settings["pikavirtual-host"],
        credentials = pika.credentials.PlainCredentials(
             username=settings["pikausername"], password=settings["pikapassword"]
        ),
        channel_max=settings["pikachannel-max"],
        frame_max=settings["pikaframe-max"],
        heartbeat_interval=settings["pikaheartbeat-interval"],
        ssl=settings["pikassl"],
        ssl_options=settings["pikassl-options"],
        connection_attempts=settings["pikaconnection-attempts"],
        retry_delay=settings["pikaretry-delay"],
        socket_timeout=settings["pikasocket-timeout"],
        locale=settings["pikalocale"],
        backpressure_detection=settings["pikabackpressure-detection"]
    ))

channel = connection.channel()

# for line in sys.stdin:
while True:
    line = sys.stdin.readline()
    if not line:
        break
    utc_ts = datetime.datetime.utcnow()
    local_datetime = datetime.datetime.now()

    publish_message = {
        "TAGS":              ".source.s_acct",
        "SOURCEIP":          settings["ipaddress"],
        "PROGRAM":           "acctpublish",
        "PRIORITY":          "info",
        "MESSAGE":           acctparse(line),
        "LEGACY_MSGHDR":     "acct: ",
        "HOST_FROM":         settings["hostname"],
        "HOST":              settings["hostname"],
        "FACILITY":          "daemon",
        "DATE":              local_datetime.strftime("%b %e %H:%M:%S"),
        "UTC-TIMESTAMP":     utc_ts.isoformat(),
    }

    # print repr(json.dumps(publish_message))

    channel.basic_publish(
        'syslog',
        'syslog',
        json.dumps(publish_message),
        pika.BasicProperties(content_type="application/json", delivery_mode=1)
    )

connection.close()
