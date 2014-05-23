#!/usr/bin/env python2
# coding: utf-8

from route import Route

def print_statistics(route):
    print 'TTL   IP Addresses    Absolute RTT    Relative RTT    Relative ZRTT  Location'
    
    for ttl in route.ttls(exclude_noreply=True):
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

        if route[ttl].is_destination(): break

    print ''

if __name__ == '__main__':
    route = Route()
    route.load('/dev/stdin')

    print_statistics(route)