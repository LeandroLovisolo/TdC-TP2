#!/usr/bin/env python2
# coding: utf-8

from sys import maxint
from plot import plot_main
import numpy as np

def plot(plt, fig, route):
    gateways, rtts, stdevs = [], [], []
    for ttl in route.ttls(exclude_noreply=True, limit_to_destination=True):
        gateways.append('%s\n%s' % (route[ttl].main_gateway().ip,
                                    route[ttl].main_gateway().location))
        rtts.append(route[ttl].abs_rtt())
        stdevs.append(route[ttl].abs_rtt_stdev())
    gateways.reverse()
    rtts .reverse()

    y_pos = np.arange(len(gateways))
    plt.barh(y_pos, rtts, xerr=stdevs, align='center', alpha=0.4)
    plt.yticks(y_pos, gateways, horizontalalignment='right', fontsize=9)
    plt.title('RTTs para cada gateway')
    plt.xlabel('RTT (ms)')
    plt.ylabel('Gateway')

    # X axis limits
    xmin, xmax = None, None
    for i in range(0, len(rtts)):
        if xmin is None or rtts[i] - stdevs[i] < xmin: xmin = rtts[i] - stdevs[i]
        if xmax is None or rtts[i] + stdevs[i] > xmax: xmax = rtts[i] + stdevs[i]
    margin = (xmax - xmin) * 0.02
    plt.xlim([xmin - margin, xmax + margin])

    # Line at y=0
    plt.vlines(0, -1, len(gateways), alpha=0.4)

    # Mean
    plt.vlines(route.abs_rtt_mean(), -1, len(gateways), linestyle='--', color='b', alpha=0.4)
    plt.text(route.abs_rtt_mean(), len(gateways) - 1, 'Media', rotation='vertical',
             verticalalignment='top', horizontalalignment='right')

    fig.set_size_inches(6, 9) 

if __name__ == '__main__':
    plot_main(plot)