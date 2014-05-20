#!/usr/bin/env python2
# encoding: utf-8

import sys
import socket
import logging
logging.getLogger('scapy.runtime').setLevel(logging.ERROR)
from scapy.all import *
from route import Route

PACKETS_PER_TTL = 100
PACKET_TIMEOUT  = 1
MAX_TTL          = 30

###############################################################################
# Traceroute                                                                  #
###############################################################################

# Returns True if most answers are of type ICMP echo reply
def destination_reached(ans):
    echo_replies = 0
    for i in range(0, len(ans)):
        if ans[i][1].type == 0: echo_replies += 1
    return echo_replies > len(ans) / 2

# Returns True if the destination is reached or False otherwise
def tracehop(hostname, ttl, route):
    try:
        ans, unans = sr(IP(dst=hostname, ttl=ttl) / UDP(dport=34334) * PACKETS_PER_TTL,
                        verbose=0, timeout=PACKET_TIMEOUT)

        # No packets answered
        if len(ans) == 0:
            route[ttl].noreply()
            return False

        # At least one packet answered
        else:
            for i in range(0, len(ans)):
                ip  = ans[i][1].src
                rtt = (ans[i][1].time - ans[i][0].sent_time) * 1000
                route[ttl].add_reply(ip, rtt)
            return destination_reached(ans)

    except socket.error as e:
        sys.exit(e)

def traceroute(hostname):
    route = Route()

    print 'Tracing route to %s...' % hostname

    for ttl in range(1, MAX_TTL + 1):
        destination_reached = tracehop(hostname, ttl, route)

        if route[ttl].is_noreply():
            print '%3d hops away: no reply' % ttl
        else:
            ips     = route[ttl].gateway_ips()
            abs_rtt = '%0.03f ms' % route[ttl].abs_rtt()
            print '%3d hops away: %-15s  %11s  %s' % (ttl,
                                                      ips[0],
                                                      abs_rtt,
                                                      route[ttl].gateway(ips[0]).location)
            for ip in ips[1:]:
                print '               %-28s  %s' % (ip, route[ttl].gateway(ip).location)

        if destination_reached:
            print 'Destination reached.'
            break

    return route

###############################################################################
# Main                                                                        #
###############################################################################

def help():
    return 'Usage: %s [hostname]            Trace route to [hostname].\n' \
           '       %s [hostname] -o [path]  Trace route to [hostname] and save\n' \
           '       %s                       machine-readable output to [path].' \
           % (sys.argv[0], sys.argv[0], ' ' * len(sys.argv[0]))

if __name__ == '__main__':
    # Read and validate command-line arguments
    if len(sys.argv) < 2 or len(sys.argv) > 4:     sys.exit(help())
    if len(sys.argv) == 4 and sys.argv[2] != '-o': sys.exit(help())
    hostname    = sys.argv[1]
    output_path = sys.argv[3] if len(sys.argv) == 4 else None

    # Do the actual traceroute 
    route = traceroute(hostname)

    # Display results
    print '\nStatistics:\n'
    print 'TTL   IP Addresses    Absolute RTT    Relative RTT    Relative ZRTT  Location'
    for ttl in route.ttls(exclude_noreplies=True):
        ips     = route[ttl].gateway_ips()
        abs_rtt = '%0.03f ms' % route[ttl].abs_rtt()
        rel_rtt = '%0.03f ms' % route[ttl].rel_rtt()
        print '%-3d   %-15s  %11s  %14s  %15.3f  %s' % (ttl,
                                                        ips[0],
                                                        abs_rtt,
                                                        rel_rtt,
                                                        route[ttl].rel_zrtt(),
                                                        route[ttl].gateway(ips[0]).location)
        for ip in ips[1:]:
            print '      %-62s %s' % (ip, route[ttl].gateway(ip).location)
    print ''
    print 'Absolute RTT mean:           %9.3f ms' % route.abs_rtt_mean()
    print 'Absolute RTT std. deviation: %9.3f ms' % route.abs_rtt_stdev()
    print ''
    print 'Relative RTT mean:           %9.3f ms' % route.rel_rtt_mean()
    print 'Relative RTT std. deviation: %9.3f ms' % route.rel_rtt_stdev()
    print ''

    # Display results for machines
    if output_path is not None:
       route.save(output_path)
       print 'Results saved to %s.' % output_path