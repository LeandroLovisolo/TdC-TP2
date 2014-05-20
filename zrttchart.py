#!/usr/bin/env python2
# coding: utf-8

import matplotlib.pyplot as plt; plt.rcdefaults()
import numpy as np
import matplotlib.pyplot as plt
from route import Route

if __name__ == '__main__':
    route = Route()
    route.load('/dev/stdin')

    ips       = []
    zrtts     = []
    threshold = 1.0

    for ttl in route.ttls(exclude_noreplies=True):
        ips.append(route[ttl].main_gateway().ip)
        zrtts.append(route[ttl].rel_zrtt())

    plt.rcParams['text.latex.preamble']=[r'\usepackage{lmodern}']
    plt.rcParams.update({'text.usetex':       True,
                         'font.size':         10,
                         'font.family':       'lmodern',
                         'text.latex.unicode': True})

    x_pos = np.arange(len(ips))
    plt.bar(x_pos, zrtts, align='center', alpha=0.4)
    plt.xticks(x_pos, ips, rotation='45', fontsize=8)
    plt.title('ZRTTs para cada hop')
    plt.xlabel('Gateway')
    plt.ylabel('ZRTT')
    plt.tight_layout()

    # Line at y=0
    plt.hlines(0, -1, len(ips))

    # ZRTT threshold
    plt.hlines(threshold, -1, len(ips), linestyle='--', color='b', alpha=0.4)
    plt.text(0, threshold, 'Umbral', verticalalignment='bottom')

    plt.show()