#!/usr/bin/env python2
# encoding: utf-8

# Código parcialmente robado de:
# http://jvns.ca/blog/2013/10/31/day-20-scapy-and-traceroute/

import sys
from scapy.all import *
from time import time

def traceroute(hostname):
	for i in range(1, 64):
	    pkt = IP(dst=hostname, ttl=i) / UDP(dport=33434)
	    # Send the packet and get a reply
	    t0 = time()
	    reply = sr1(pkt, verbose=0, timeout=1)
	    t = (time() - t0) * 1000
	    
	    if reply is None:
	        # No reply =(
	        # break
	        print "%d hops away:\tno reply" % i
	    elif reply.type == 3:
	        # We've reached our destination
	        print "Done!", reply.src
	        break
	    else:
	        # We're in the middle somewhere
	        print "%d hops away:\t%s\t(%.3f ms)" % (i, reply.src, t)

if __name__ == "__main__":
	if len(sys.argv) != 2:
		sys.exit("Usage: %s [hostname]" % sys.argv[0])
	hostname = sys.argv[1]
	traceroute(hostname)