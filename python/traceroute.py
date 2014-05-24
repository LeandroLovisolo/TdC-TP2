#!/usr/bin/env python2
# encoding: utf-8

import argparse
import os
import sys
import socket
import logging
logging.getLogger('scapy.runtime').setLevel(logging.ERROR)
from scapy.all import *
from random import randint
from route import Route
from statistics import print_statistics

MAX_TTL         = 30
PACKET_TIMEOUT  = 1

def traceroute(hostname, seconds):
    dst_ip = socket.gethostbyname(hostname)
    route = Route(dst_ip)

    print 'Tracing route to %s...' % hostname

    t0 = time.time()
    last_id = 0

    while time.time() - t0 < seconds:
        base_id = last_id

        pkts = []
        for ttl in range(1, MAX_TTL + 1):
            id = base_id + ttl
            pkts.append(IP(dst=dst_ip, ttl=ttl) / ICMP(id=id))

        last_id = id

        try:
            ans, unans = sr(pkts, verbose=0, timeout=PACKET_TIMEOUT)
        except socket.error as e:
            sys.exit(e)

        for snd, rcv in ans:
            id = rcv[3].id

            # Check that the received packet is a response to
            # a packet from the current batch.
            if id < base_id + 1 or id > base_id + 30:
                continue

            ttl  = id - base_id
            ip   = rcv.src
            type = rcv.type
            rtt  = (rcv.time - snd.sent_time) * 1000
            route[ttl].add_reply(ip, type, rtt)

        os.system('clear')
        print_statistics(route)

    return route

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('hostname',
                        help='trace route to [hostname] and measure round-trip times to each hop')
    parser.add_argument('-t', '--time',
                        type=int, default=10,
                        help='measure round-trip times for TIME seconds (default 10)')
    parser.add_argument('-o', '--output',
                        help='save machine-readable output to OUTPUT')
    args = parser.parse_args()

    # Do the actual traceroute 
    route = traceroute(args.hostname, args.time)

    # Display results
    print_statistics(route)

    # Display results for machines
    if args.output:
       route.save(args.output)
       print 'Results saved to %s.' % args.output