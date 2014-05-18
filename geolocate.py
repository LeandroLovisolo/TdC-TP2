#!/usr/bin/env python2
# coding: utf-8

import sys
import pygeoip

if __name__ == '__main__':

    gi = pygeoip.GeoIP('data/GeoLiteCity.dat')

    for line in sys.stdin:
        ip = line.strip()
        gir = gi.record_by_addr(ip)

        if gir is not None:
            if gir['city'] is None:
                print "%f %f %s" % (gir['latitude'],
                                    gir['longitude'],
                                    gir['country_name'])
            else:
                print "%f %f %s, %s" % (gir['latitude'],
                                        gir['longitude'],
                                        gir['city'],
                                        gir['country_name'])