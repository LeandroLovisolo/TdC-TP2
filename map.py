#!/usr/bin/env python2
# encoding: utf-8

import sys
from mpl_toolkits.basemap import Basemap
import numpy as np
import matplotlib.pyplot as plt

def corners(lons, lats):
    w = max(lons) - min(lons)
    h = max(lats) - min(lats)
    llcrnrlon = min(lons) - w * 0.1
    llcrnrlat = min(lats) - h * 0.1
    urcrnrlon = max(lons) + w * 0.1
    urcrnrlat = max(lats) + h * 0.1

    return llcrnrlon, llcrnrlat, urcrnrlon, urcrnrlat

def create_map(llcrnrlon, llcrnrlat, urcrnrlon, urcrnrlat):
    # create new figure, axes instances.
    fig = plt.figure()
    ax  = fig.add_axes([0.1, 0.1, 0.8, 0.8])

    # setup mercator map projection.
    m = Basemap(llcrnrlon=llcrnrlon, llcrnrlat=llcrnrlat,
                urcrnrlon=urcrnrlon, urcrnrlat=urcrnrlat,
                projection='merc')

    m.drawcoastlines()
    m.fillcontinents()

    return m

def plot_route(route, m):
    lastplace = None
    for place in route:
        if(lastplace == None): lastplace = place
        else:
            # draw line between lastplace and place
            xx = []; yy = []
            for p in [lastplace, place]:
                x, y = m(p[0], p[1])
                xx.append(x)
                yy.append(y)
            m.plot(xx, yy, linewidth=2, color='b')

            # m.drawgreatcircle(lastplace[0], lastplace[1],
            #                   place[0], place[1],
            #                   linewidth=2,color='b')

            # mark lastplace
            x, y = m(lastplace[0], lastplace[1])
            plt.text(x, y, lastplace[2])
            m.plot(x, y, 'ro')

            lastplace = place
        
        # mark final place
        x, y = m(place[0], place[1])
        plt.text(x, y, place[2])
        m.plot(x, y, 'ro')

if __name__ == '__main__':
    route = []
    for line in sys.stdin:
        latitude  = float(line.split(' ')[0])
        longitude = float(line.split(' ')[1])
        city      = ' '.join(line.split(' ')[2:])
        route.append([longitude, latitude, city])

    lons = map(lambda x: x[0], route)
    lats = map(lambda x: x[1], route)
    llcrnrlon, llcrnrlat, urcrnrlon, urcrnrlat = corners(lons, lats)

    m = create_map(llcrnrlon, llcrnrlat, urcrnrlon, urcrnrlat)
    
    plot_route(route, m)
    
    plt.show()