#!/usr/bin/env python2
# encoding: utf-8

import sys
import socket
import logging
logging.getLogger('scapy.runtime').setLevel(logging.ERROR)
from scapy.all import *
from time import time
from math import sqrt
import pygeoip

PACKAGES_PER_TTL = 50
PACKAGE_TIMEOUT  = 1
MAX_TTL          = 64

###############################################################################
# Traceroute                                                                  #
###############################################################################

def avg_rtt(ans):
    rtt_total = 0
    for i in range(0, len(ans)):
        rtt_total += ans[i][1].time - ans[i][0].sent_time
    return rtt_total / len(ans) * 1000

def extract_and_geolocate_srcs(ans, gi):
    srcs = [] # [{'ip': '4.69.138.123', 'location': '*', 'latitude': '*', 'longitude': '*'}]

    for i in range(0, len(ans)):
        ip  = ans[i][1].src
        gir = gi.record_by_addr(ip)

        if gir is None or gir['country_name'] is None:
            location = '*'
        elif gir['city'] is None:
            location = gir['country_name']
        else:
            location = '%s, %s' % (gir['city'], gir['country_name'])

        src = {'ip':        ip,
               'location':  location,
               'latitude':  '*' if gir is None else gir['latitude'],
               'longitude': '*' if gir is None else gir['longitude']}

        if src not in srcs: srcs.append(src)

    return srcs

def tracehop(hostname, ttl, gi):
    try:
        ans, unans = sr(IP(dst=hostname, ttl=ttl) / ICMP() * PACKAGES_PER_TTL,
                        verbose=0, timeout=PACKAGE_TIMEOUT)

        if len(ans) == 0:
            srcs = '*'
            rtt  = '*'
            destination_reached = False
        else:
            srcs = extract_and_geolocate_srcs(ans, gi)
            rtt  = avg_rtt(ans)
            destination_reached = True if ans[0][1].type == 0 else False

        return {'hop': ttl, 'srcs': srcs, 'rtt': rtt}, destination_reached

    except socket.error as e:
        sys.exit(e)

def traceroute(hostname, human):
    gi = pygeoip.GeoIP('data/GeoLiteCity.dat')

    hops = []

    for i in range(1, MAX_TTL):
        hop, destination_reached = tracehop(hostname, i, gi)
        hops.append(hop)

        if human:
            if hop['srcs'] == '*':
                print '%-3d hops away: no reply' % i
            else:
                rtt = '%0.03f ms' % hop['rtt']
                print '%-3d hops away: %-15s %-11s %s' % (i,
                                                          hop['srcs'][0]['ip'],
                                                          rtt,
                                                          hop['srcs'][0]['location'])
                for i in range(1, len(hop['srcs'])):
                    print '               %-27s %s' % (hop['srcs'][i]['ip'],
                                                       hop['srcs'][i]['location'])

        if destination_reached:
            if human: print 'Destination reached.'
            break

    return hops

###############################################################################
# Statistics                                                                  #
###############################################################################

def exclude_noreply(hops):
    return filter(lambda x: x['srcs'] != '*', hops)

def extract_rtts(hops):
    return map(lambda x: x['rtt'], exclude_noreply(hops))

def mean(rtts):
    return sum(rtts) / len(rtts)

def stdev(rtts):
    n  = len(rtts)
    mu = mean(rtts)
    return sqrt(sum([(rtt - mu)**2 for rtt in rtts]) / n)

def zrtt(rtt, mu, sigma):
    return (rtt - mu) / sigma

###############################################################################
# Main                                                                        #
###############################################################################

def help():
    return 'Usage: %s [hostname]       for human-friendly output\n' \
           '       %s [hostname] -m    for machine readable output' \
           % (sys.argv[0], sys.argv[0])

if __name__ == '__main__':
    # Read and validate command-line arguments
    if len(sys.argv) < 2 or len(sys.argv) > 3:     sys.exit(help())
    if len(sys.argv) == 3 and sys.argv[2] != '-m': sys.exit(help())
    hostname = sys.argv[1]
    human    = len(sys.argv) == 2

    # Do the actual traceroute 
    hops = traceroute(hostname, human)

    # Compute statistics
    rtts  = extract_rtts(hops)
    mu    = mean(rtts)
    sigma = stdev(rtts)

    # Display results for humans
    if human:
        print '\nStatistics:\n'
        print 'Hop  IP Addresses    RTT      ZRTT     Location'
        for hop in exclude_noreply(hops):
            print '%-3d  %-15s %-8.3f %-8.3f %s' % (hop['hop'],
                                                    hop['srcs'][0]['ip'],
                                                    hop['rtt'],
                                                    zrtt(hop['rtt'], mu, sigma),
                                                    hop['srcs'][0]['location'])
            for i in range(1, len(hop['srcs'])):
                print '     %-33s %s' % (hop['srcs'][i]['ip'],
                                         hop['srcs'][i]['location'])
        print ''
        print 'Mean RTT:       %0.3f ms' % mean(rtts)
        print 'Std. deviation: %0.3f ms' % stdev(rtts)
        print ''

    # Display results for machines
    else:
        print 'Machine readable output not yet implemented.'
