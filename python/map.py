#!/usr/bin/env python2
# encoding: utf-8

from plot import plot_main
from mpl_toolkits.basemap import Basemap

def corners(lons, lats):
    w = max(lons) - min(lons)
    h = max(lats) - min(lats)
    llcrnrlon = min(lons) - w * 0.1
    llcrnrlat = min(lats) - h * 0.1
    urcrnrlon = max(lons) + w * 0.1
    urcrnrlat = max(lats) + h * 0.1
    return llcrnrlon, llcrnrlat, urcrnrlon, urcrnrlat

def create_map(llcrnrlon, llcrnrlat, urcrnrlon, urcrnrlat):
    m = Basemap(llcrnrlon=llcrnrlon, llcrnrlat=llcrnrlat,
                urcrnrlon=urcrnrlon, urcrnrlat=urcrnrlat,
                projection='merc')
    m.drawcoastlines()
    m.fillcontinents()
    return m

def plot_route(gateways, m):
    prev_gateway = None

    for gateway in gateways:
        if(prev_gateway == None): prev_gateway = gateway
        else:
            # draw line between prev_gateway and gateway
            xx = []; yy = []
            for gw in [prev_gateway, gateway]:
                x, y = m(gw.longitude, gw.latitude)
                xx.append(x)
                yy.append(y)
            m.plot(xx, yy, linewidth=2, color='b')

            # m.drawgreatcircle(prev_gateway.longitude, prev_gateway.latitude,
            #                   gateway.longitude, gateway.latitude,
            #                   linewidth=2,color='b')

            # mark prev_gateway
            x, y = m(prev_gateway.longitude, prev_gateway.latitude)
            # plt.text(x, y, prev_gateway.location)
            m.plot(x, y, 'ro')

            prev_gateway = gateway
        
        # mark final gateway
        x, y = m(gateway.longitude, gateway.latitude)
        # plt.text(x, y, gateway.location)
        m.plot(x, y, 'ro')

def plot(plt, fig, route):
    gateways = []
    for ttl in route.ttls(exclude_noreplies=True):
        if route[ttl].main_gateway().has_location():
            gateways.append(route[ttl].main_gateway())

    lons, lats = [], []
    for gateway in gateways:
        lons.append(gateway.longitude)
        lats.append(gateway.latitude)
    llcrnrlon, llcrnrlat, urcrnrlon, urcrnrlat = corners(lons, lats)

    m = create_map(llcrnrlon, llcrnrlat, urcrnrlon, urcrnrlat)
    
    plot_route(gateways, m)

    fig.set_size_inches(6, 4) 

if __name__ == '__main__':
    plot_main(plot)