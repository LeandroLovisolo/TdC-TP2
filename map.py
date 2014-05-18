#!/usr/bin/env python2
# encoding: utf-8

from mpl_toolkits.basemap import Basemap
import numpy as np
import matplotlib.pyplot as plt

def corners(lons, lats):
    w = max(lons) - min(lons)
    h = max(lats) - min(lats)
    llcrnrlon = min(lons) - w * 0.05
    llcrnrlat = min(lats) - h * 0.05
    urcrnrlon = max(lons) + w * 0.05
    urcrnrlat = max(lats) + h * 0.05
    return llcrnrlon, llcrnrlat, urcrnrlon, urcrnrlat

def create_map(llcrnrlon, llcrnrlat, urcrnrlon, urcrnrlat):
    # create new figure, axes instances.
    fig = plt.figure()
    ax  = fig.add_axes([0.1, 0.1, 0.8, 0.8])
    ax.set_title('Ruta desde X hacia Y')

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
            m.drawgreatcircle(lastplace[0], lastplace[1],
                              place[0], place[1],
                              linewidth=2, color='b')
            lastplace = place
        
        x, y = m(place[0], place[1])
        plt.text(x, y, place[2])
        m.plot(x, y, 'ro')    

if __name__ == '__main__':
    route = [[-58.4005861, -34.618222 , 'Buenos Aires, Argentina'],
             [-56.1927248,  -34.8837332, 'Montevideo, Uruguay'],
             [-43.2630369, -22.9272733, 'Rio de Janeiro, Brazil'],
             [-74.0323916, 40.7665059, 'New York, USA'],
             [-122.4889645, 37.7267417, 'San Francisco, USA']]

    lons = map(lambda x: x[0], route)
    lats = map(lambda x: x[1], route)
    llcrnrlon, llcrnrlat, urcrnrlon, urcrnrlat = corners(lons, lats)

    m = create_map(llcrnrlon, llcrnrlat, urcrnrlon, urcrnrlat)
    
    plot_route(route, m)
    
    plt.show()