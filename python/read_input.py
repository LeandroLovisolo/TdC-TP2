import sys

def read_input():
	mu, sigma = sys.stdin.readline().split(' ')
	mu = float(mu); sigma = float(sigma)

	hops = []

	line = sys.stdin.readline()
	while line != '':
		hop, rtt, zrtt, nsrcs = line.split(' ')
		hop = int(hop); rtt = float(rtt); zrtt = float(zrtt); nsrcs = int(nsrcs)

		srcs = []
		for i in range(0, nsrcs):
			srcs.append({'ip':        sys.stdin.readline(),
				         'location':  sys.stdin.readline(),
				         'latitude':  sys.stdin.readline(),
				         'longitude': sys.stdin.readline()})
		hops.append({'hop':  hop,
			         'rtt':  rtt,
			         'zrtt': zrtt,
			         'srcs': srcs})

		line = sys.stdin.readline()

	return mu, sigma, hops
