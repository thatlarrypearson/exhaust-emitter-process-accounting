#!/usr/bin/env python
#
#  syslogtopic.py
#
# $ amqp-consume -e syslog -r syslog cat | tee amqp-2.txt
#
__author__ = 'lbp'

import pika
import sys
import pprint
import json

connection = pika.BlockingConnection(pika.ConnectionParameters( host='rabbitmq'))
channel = connection.channel()

channel.exchange_declare(exchange='syslog', type='topic')

result = channel.queue_declare(exclusive=True)
queue_name = result.method.queue

# binding_keys = sys.argv[1:]
# if not binding_keys:
#     print >> sys.stderr, "Usage: %s [binding_key]..." % (sys.argv[0],)
#     sys.exit(1)

# for binding_key in binding_keys:
#    channel.queue_bind(exchange="syslog", queue=queue_name, routing_key=binding_key)

channel.queue_bind(exchange="syslog", queue=queue_name, routing_key="syslog")


print ' [*] Waiting for logs. To exit press CTRL+C'

def callback(ch, method, properties, body):
    # print " [x] %r:%r" % (method.routing_key, body,)
    # properties = <BasicProperties(
    # [
    #     'content_type=text/plain',
    #     'delivery_mode=2',
    #     "headers= {
    #            'HOST_FROM': u'obd-gps',
    #            'FACILITY': u'auth',
    #            'SEQNUM': u'1071',
    #            'TAGS': u'.source.s_src',
    #            'PID': u'25077',
    #            'LEGACY_MSGHDR': u'sshd[25077]: ',
    #            'PRIORITY': u'info',
    #            'HOST': u'obd-gps',
    #            'PROGRAM': u'sshd',
    #            'DATE': u'Aug 26 12:29:39',
    #            'MESSAGE': u'Connection closed by 112.5.16.86 [preauth]',
    #            'SOURCEIP': u'127.0.0.1'
    #      }"
    # ]
    # )>
    # pprint.pprint(json.loads(body))
    print body
    sys.stdout.flush()

channel.basic_consume(callback, queue=queue_name, no_ack=True)

channel.start_consuming()
