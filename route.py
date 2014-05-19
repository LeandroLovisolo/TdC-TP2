from math import sqrt
import pygeoip

class Route:
    def __init__(self):
        self._hops = {}
        self._gi   = pygeoip.GeoIP('data/GeoLiteCity.dat')

    ###########################################################################
    # Insertion                                                               #
    ###########################################################################

    def add_reply(self, hop, ip, rtt):
        if not self._hops.has_key(hop):
            self._hops[hop] = []
        self._hops[hop].append({'ip': ip, 'rtt': rtt})

    def add_noreply(self, hop):
        self._hops[hop] = None

    ###########################################################################
    # Retrieval                                                               #
    ###########################################################################

    def hops(self, exclude_noreplies=False):
        if exclude_noreplies:
            hops = []
            for hop in self._hops.keys():
                if not self.is_noreply(hop):
                    hops.append(hop)
        else:
            hops = self._hops.keys()
        hops.sort()
        return hops

    def is_noreply(self, hop):
        return self._hops[hop] is None

    def replies(self, hop):
        replies = []
        for reply in self._hops[hop]:
            location, latitude, longitude = self._geolocate(reply['ip'])
            replies.append({'ip':        reply['ip'],
                            'rtt':       reply['rtt'],
                            'location':  location,
                            'latitude':  latitude,
                            'longitude': longitude})
        return replies

    def _geolocate(self, ip):
        gir = self._gi.record_by_addr(ip)
        if gir is None or gir['country_name'] is None:
            location = '*'
        elif gir['city'] is None:
            location = gir['country_name']
        else:
            location = '%s, %s' % (gir['city'], gir['country_name'])
        latitude  = '*' if gir is None else gir['latitude']
        longitude = '*' if gir is None else gir['longitude']
        return location, latitude, longitude

    ###########################################################################
    # Statistics                                                              #
    ###########################################################################

    def abs_rtt(self, hop):
        rtts = map(lambda x: x['rtt'], self.replies(hop))
        return sum(rtts) / len(rtts)

    def abs_zrtt(self, hop):
        return (self.abs_rtt(hop) - self.abs_rtt_mean()) / self.abs_rtt_stdev()

    def abs_rtt_mean(self):
        hops = self.hops(exclude_noreplies=True)
        return sum([self.abs_rtt(hop) for hop in hops]) / len(hops)

    def abs_rtt_stdev(self):
        mu = self.abs_rtt_mean()
        hops = self.hops(exclude_noreplies=True)
        return sqrt(sum([(self.abs_rtt(hop) - mu)**2 for hop in hops]) / len(hops))

    def rel_rtt(self, hop):
        if hop == 1:
            return self.abs_rtt(hop)
        else:
            prev = hop - 1
            while self.is_noreply(prev) and prev > 1: prev -= 1
            return self.abs_rtt(hop) - self.abs_rtt(prev)

    def rel_zrtt(self, hop):
        return (self.rel_rtt(hop) - self.rel_rtt_mean()) / self.rel_rtt_stdev()

    def rel_rtt_mean(self):
        hops = self.hops(exclude_noreplies=True)
        return sum([self.rel_rtt(hop) for hop in hops]) / len(hops)

    def rel_rtt_stdev(self):
        mu = self.rel_rtt_mean()
        hops = self.hops(exclude_noreplies=True)
        return sqrt(sum([(self.rel_rtt(hop) - mu)**2 for hop in hops]) / len(hops))

    ###########################################################################
    # Persistence                                                             #
    ###########################################################################

    def load(self, path):
        with open(path) as f:
            line = f.readline()
            while line != '':
                line = line.strip().split(' ')
                hop  = int(line[0])
                if line[1] == '*': self.add_noreply(hop)
                else:
                    ip  = line[1]
                    rtt = float(line[2])
                    self.add_reply(hop, ip, rtt)
                line = f.readline()

    def save(self, path):
        with open(path, 'w') as f:
            for hop in self._hops.keys():
                if self._hops[hop] is None:
                    f.write('%d *\n' % hop)
                else:
                    for gateway in self._hops[hop]:
                        f.write('%d %s %f\n' % (hop,
                                                gateway['ip'],
                                                gateway['rtt']))