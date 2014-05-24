#!/usr/bin/env python2
# coding: utf-8

from plot import plot_main
import numpy as np

def plot(plt, fig, route):
    threshold = 1
    gateways, zrtts = [], []
    for ttl in route.ttls(exclude_noreply=True, limit_to_destination=True):
        gateways.append('%s\n%s' % (route[ttl].main_gateway().ip,
                                    route[ttl].main_gateway().location))
        zrtts.append(route[ttl].rel_zrtt())
    gateways.reverse()
    zrtts.reverse()

    y_pos = np.arange(len(gateways))
    plt.barh(y_pos, zrtts, align='center', alpha=0.4)
    plt.yticks(y_pos, gateways, horizontalalignment='right', fontsize=9)
    plt.title('ZRTTs para cada gateway')
    plt.xlabel('ZRTT')
    plt.ylabel('Gateway')

    # Line at y=0
    plt.vlines(0, -1, len(gateways), alpha=0.4)

    # ZRTT threshold
    plt.vlines(threshold, -1, len(gateways), linestyle='--', color='b', alpha=0.4)
    plt.text(threshold, len(gateways) - 1, 'Umbral', rotation='vertical',
             verticalalignment='top', horizontalalignment='right')

    fig.set_size_inches(6, 9) 

if __name__ == '__main__':
    plot_main(plot)