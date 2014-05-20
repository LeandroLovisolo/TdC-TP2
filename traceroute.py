#!/usr/bin/env python2
# encoding: utf-8

import sys
import socket
import logging
logging.getLogger('scapy.runtime').setLevel(logging.ERROR)
from scapy.all import *
from route import Route

PACKAGES_PER_TTL = 100
PACKAGE_TIMEOUT  = 1
MAX_TTL          = 30

###############################################################################
# Traceroute                                                                  #
###############################################################################

# Returns True if the destination is reached or False otherwise
def tracehop(hostname, ttl, route):
    try:
        ans, unans = sr(IP(dst=hostname, ttl=ttl) / UDP(dport=34334) * PACKAGES_PER_TTL,
                        verbose=0, timeout=PACKAGE_TIMEOUT)

        if len(ans) == 0:
            route[ttl].noreply()
            destination_reached = False
        else:
            for i in range(0, len(ans)):
                ip  = ans[i][1].src
                rtt = (ans[i][1].time - ans[i][0].sent_time) * 1000
                route[ttl].add_reply(ip, rtt)
            # Check for ICMP echo reply
            destination_reached = True if ans[0][1].type == 0 else False

        return destination_reached

    except socket.error as e:
        sys.exit(e)

def traceroute(hostname, human):
    route = Route()

    for ttl in range(1, MAX_TTL + 1):
        destination_reached = tracehop(hostname, ttl, route)

        if human:
            if route[ttl].is_noreply():
                print '%3d hops away: no reply' % ttl
            else:
                ips     = route[ttl].replies().keys()
                abs_rtt = '%0.03f ms' % route[ttl].abs_rtt()
                print '%3d hops away: %-15s  %11s  %s' % (ttl,
                                                          ips[0],
                                                          abs_rtt,
                                                          route[ttl].replies()[ips[0]]['location'])
                for ip in ips[1:]:
                    print '               %-28s  %s' % (ip, route[ttl].replies()[ip]['location'])

        if destination_reached:
            if human: print 'Destination reached.'
            break

    return route

###############################################################################
# Main                                                                        #
###############################################################################

def help():
    return 'Usage: %s [hostname]       for human-friendly output\n' \
           '       %s [hostname] -m    for machine-readable output' \
           % (sys.argv[0], sys.argv[0])

if __name__ == '__main__':
    # Read and validate command-line arguments
    if len(sys.argv) < 2 or len(sys.argv) > 3:     sys.exit(help())
    if len(sys.argv) == 3 and sys.argv[2] != '-m': sys.exit(help())
    hostname = sys.argv[1]
    human    = len(sys.argv) == 2

    # Do the actual traceroute 
    route = traceroute(hostname, human)

    # Display results for humans
    if human:
        print '\nStatistics:\n'
        print 'TTL   IP Addresses    Absolute RTT    Relative RTT    Relative ZRTT  Location'
        for ttl in route.ttls(exclude_noreplies=True):
            ips     = route[ttl].replies().keys()
            abs_rtt = '%0.03f ms' % route[ttl].abs_rtt()
            rel_rtt = '%0.03f ms' % route[ttl].rel_rtt()
            print '%-3d   %-15s  %11s  %14s  %15.3f  %s' % (ttl,
                                                            ips[0],
                                                            abs_rtt,
                                                            rel_rtt,
                                                            route[ttl].rel_zrtt(),
                                                            route[ttl].replies()[ips[0]]['location'])
            for ip in ips[1:]:
                print '      %-62s %s' % (ip, route[ttl].replies()[ip]['location'])
        print ''
        print 'Absolute RTT mean:           %9.3f ms' % route.abs_rtt_mean()
        print 'Absolute RTT std. deviation: %9.3f ms' % route.abs_rtt_stdev()
        print ''
        print 'Relative RTT mean:           %9.3f ms' % route.rel_rtt_mean()
        print 'Relative RTT std. deviation: %9.3f ms' % route.rel_rtt_stdev()
        print ''

    # Display results for machines
    else:
       route.save('/dev/stdout')