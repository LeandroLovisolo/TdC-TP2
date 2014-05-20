#!/usr/bin/env python2
# coding: utf-8

import matplotlib.pyplot as plt; plt.rcdefaults()
import numpy as np
import matplotlib.pyplot as plt
from route import Route

if __name__ == '__main__':
    route = Route()
    route.load('/dev/stdin')

    ips  = []
    rtts = []

    for ttl in route.ttls(exclude_noreplies=True):
        ips.append(route[ttl].main_gateway().ip)
        rtts.append(route[ttl].abs_rtt())

    plt.rcParams['text.latex.preamble']=[r'\usepackage{lmodern}']
    plt.rcParams.update({'text.usetex':       True,
                         'font.size':         10,
                         'font.family':       'lmodern',
                         'text.latex.unicode': True} )

    fig = plt.figure()
    fig.set_size_inches(6, 4) 

    x_pos = np.arange(len(ips))
    plt.bar(x_pos, rtts, align='center', alpha=0.4)
    plt.xticks(x_pos, ips, rotation='45', fontsize=8)
    plt.title('RTTs para cada hop')
    plt.xlabel('Gateway')
    plt.ylabel('RTT (ms)')
    plt.tight_layout()

    # Mean
    plt.hlines(route.abs_rtt_mean(), -1, len(ips), linestyle='--', color='b', alpha=0.4)
    plt.text(0, route.abs_rtt_mean(), u'Media', verticalalignment='bottom')

    #plt.savefig('tex/foo.pdf', dpi=1000, box_inches='tight')
    plt.show()