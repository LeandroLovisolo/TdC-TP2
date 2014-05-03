#!/usr/bin/env python2
# encoding: utf-8

# Código parcialmente robado de:
# http://jvns.ca/blog/2013/10/31/day-20-scapy-and-traceroute/

import sys
import socket
import logging
logging.getLogger("scapy.runtime").setLevel(logging.ERROR)
from scapy.all import *
from time import time
from math import sqrt

def help():
    return "Usage: %s [hostname]\tfor human-friendly output\n" \
           "       %s [hostname] -m\tfor machine readable output" \
           % (sys.argv[0], sys.argv[0])

def tracehop(hostname, ttl):
    try:        
        t0 = time()
        reply = sr1(IP(dst=hostname, ttl=ttl) / UDP(dport=33434),
                    verbose=0, timeout=1)
        t = (time() - t0) * 1000
        return reply, t
    except socket.error as e:
        sys.exit(e)

def traceroute(hostname, human):
    hops = []

    for i in range(1, 64):
        reply, t = tracehop(hostname, i)

        hop = {"hop": i,
               "src": "*" if reply is None else reply.src,
               "rtt": -1  if reply is None else t}
        hops.append(hop)

        if human:
            msg = "%d hops away:\t" % i
            if hop["src"] == "*": msg += "no reply"
            else:                 msg += "%s\t(%0.3f ms)" % (hop["src"], hop["rtt"])
            print msg

        if reply is not None and reply.type == 3:
            if human: print "Destination reached."
            break

    return hops

def filter_noreply(hops):
    return filter(lambda x: x["src"] != "*", hops)

def extract_rtts(hops):
    return map(lambda x: x["rtt"], filter_noreply(hops))

def mean(rtts):
    return sum(rtts) / len(rtts)

def stdev(rtts):
    n  = len(rtts)
    mu = mean(rtts)
    return sqrt(sum([(rtt - mu)**2 for rtt in rtts]) / n)

def zrtt(rtt, mu, sigma):
    return (rtt - mu) / sigma

if __name__ == "__main__":
    if len(sys.argv) < 2 or len(sys.argv) > 3:     sys.exit(help())
    if len(sys.argv) == 3 and sys.argv[2] != "-m": sys.exit(help())

    hostname = sys.argv[1]
    human    = len(sys.argv) == 2

    hops = traceroute(hostname, human)

    rtts  = extract_rtts(hops)
    mu    = mean(rtts)
    sigma = stdev(rtts)

    if human:
        print ""
        print "=================================================="
        print ""
        print "Mean: %f" % mean(rtts)
        print "Standard deviation: %f" % stdev(rtts)
        print ""

    print "Hop\tIP Address\tRTT\tZRTT"
    for hop in filter_noreply(hops):
        print "%d\t%s\t%0.3f\t%0.3f" % \
            (hop["hop"], hop["src"], hop["rtt"], zrtt(hop["rtt"], mu, sigma))
