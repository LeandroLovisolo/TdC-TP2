#!/usr/bin/env python2
# coding: utf-8

from plot import plot_main
import numpy as np

def plot(plt, fig, route):
    gateways, rtts = [], []
    for ttl in reversed(route.ttls(exclude_noreplies=True)):
        gateways.append('%s\n%s' % (route[ttl].main_gateway().ip,
                                    route[ttl].main_gateway().location))
        rtts.append(route[ttl].abs_rtt())

    y_pos = np.arange(len(gateways))
    plt.barh(y_pos, rtts, align='center', alpha=0.4)
    plt.yticks(y_pos, gateways, fontsize=8, horizontalalignment='right')
    plt.title('RTTs para cada gateway')
    plt.xlabel('RTT (ms)')
    plt.ylabel('Gateway')

    # Mean
    plt.vlines(route.abs_rtt_mean(), -1, len(gateways), linestyle='--', color='b', alpha=0.4)
    plt.text(route.abs_rtt_mean(), len(gateways) - 1, 'Media', rotation='vertical',
             verticalalignment='top', horizontalalignment='right')

    fig.set_size_inches(6, 8) 

if __name__ == '__main__':
    plot_main(plot)