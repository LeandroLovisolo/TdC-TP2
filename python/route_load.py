#!/usr/bin/env python2
# coding: utf-8

import route

r = route.Route()
r.load('/dev/stdin')
print r
for ttl in r.ttls(exclude_noreplies=True):
    for ip in r[ttl].gateway_ips():
        for rtt in r[ttl].gateway(ip).rtts:
            print '%-3d %-17s %-10.3f abs rtt: %-10.3f rel rtt: %-10.3f ' \
                  'abs zrtt: %-10.3f rel zrtt %.3f' % (ttl,
                                                       ip,
                                                       rtt,
                                                       r[ttl].abs_rtt(),
                                                       r[ttl].rel_rtt(),
                                                       r[ttl].abs_zrtt(),
                                                       r[ttl].rel_zrtt())

print ''
print 'abs mean:  %f' % r.abs_rtt_mean()
print 'abs stdev: %f' % r.abs_rtt_stdev()
print ''
print 'rel mean:  %f' % r.rel_rtt_mean()
print 'rel stdev: %f' % r.rel_rtt_stdev()
print ''

r.save('/dev/stdout')