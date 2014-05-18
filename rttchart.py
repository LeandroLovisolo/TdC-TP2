#!/usr/bin/env python2
# coding: utf-8

import sys
import matplotlib.pyplot as plt; plt.rcdefaults()
import numpy as np
import matplotlib.pyplot as plt

if __name__ == '__main__':
	ips  = []
	rtts = []

	for line in sys.stdin:
		ip, rtt = line.strip().split(' ')
		ips.append(ip)
		rtts.append(float(rtt))

	x_pos = np.arange(len(ips))
	plt.bar(x_pos, rtts, align='center', alpha=0.4)
	plt.xticks(x_pos, ips, rotation='vertical')
	plt.ylabel('RTT (ms)')
	plt.title('RTTs para cada hop')
	plt.show()