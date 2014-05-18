#!/usr/bin/env python2
# coding: utf-8

import sys
import matplotlib.pyplot as plt; plt.rcdefaults()
import numpy as np
import matplotlib.pyplot as plt

if __name__ == '__main__':
	ips  = []
	rtts = []
	threshold = 1.0

	for line in sys.stdin:
		ip, rtt = line.strip().split(' ')
		ips.append(ip)
		rtts.append(float(rtt))

	x_pos = np.arange(len(ips))
	plt.bar(x_pos, rtts, align='center', alpha=0.4)
	plt.xticks(x_pos, ips, rotation='45', fontsize=8)
	plt.ylabel('ZRTT')
	plt.title('ZRTTs para cada hop')

	# Line at y=0
	plt.hlines(0, -1, len(ips))

	# ZRTT threshold
	plt.hlines(threshold, -1, len(ips), linestyle='--', color='b', alpha=0.4)
	plt.text(0, threshold, 'Umbral', verticalalignment='bottom')

	plt.show()