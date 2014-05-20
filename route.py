from math import sqrt
import pygeoip

class Geolocator:
    def __init__(self):
        self._gi    = pygeoip.GeoIP('data/GeoLiteCity.dat')
        self._cache = {}

    def location(self, ip):
        if ip not in self._cache.keys(): self._geolocate(ip)
        return self._cache[ip]['location']

    def latitude(self, ip):
        if ip not in self._cache.keys(): self._geolocate(ip)
        return self._cache[ip]['latitude']

    def longitude(self, ip):
        if ip not in self._cache.keys(): self._geolocate(ip)
        return self._cache[ip]['longitude']

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
        self._cache[ip] = {'location':  location,
                           'latitude':  latitude,
                           'longitude': longitude}

class Hop:
    def __init__(self, ttl, route, geolocator):
        self._ttl        = ttl
        self._noreply    = False
        self._replies    = {}
        self._route      = route
        self._geolocator = geolocator

    ###########################################################################
    # Insertion                                                               #
    ###########################################################################

    def noreply(self):
        self._noreply = True

    def add_reply(self, ip, rtt):
        if ip not in self._replies.keys():
            self._replies[ip] = {'location':  self._geolocator.location(ip),
                                 'latitude':  self._geolocator.latitude(ip),
                                 'longitude': self._geolocator.longitude(ip),
                                 'rtts':      []}
        self._replies[ip]['rtts'].append(rtt)

    ###########################################################################
    # Retrieval                                                               #
    ###########################################################################

    def is_noreply(self):
        return self._noreply

    def replies(self):
        return self._replies

    ###########################################################################
    # Statistics                                                              #
    ###########################################################################

    def abs_rtt(self):
        total = 0
        n = 0
        for ip in self._replies.keys():
            for rtt in self._replies[ip]['rtts']:
                total += rtt
                n += 1
        return total / n

    def abs_zrtt(self):
        return (self.abs_rtt() - self._route.abs_rtt_mean()) / self._route.abs_rtt_stdev()

    def rel_rtt(self):
        if self._ttl == 1:
            return self.abs_rtt()
        else:
            prev = self._ttl - 1
            while self._route[prev].is_noreply() and prev > 1: prev -= 1
            return self.abs_rtt() - self._route[prev].abs_rtt()

    def rel_zrtt(self):
        return (self.rel_rtt() - self._route.rel_rtt_mean()) / self._route.rel_rtt_stdev()

class Route:
    def __init__(self):
        self._hops       = {}
        self._geolocator = Geolocator()

    ###########################################################################
    # Hops                                                                    #
    ###########################################################################

    def __getitem__(self, ttl):
        if ttl not in self._hops.keys():
            self._hops[ttl] = Hop(ttl, self, self._geolocator)
        return self._hops[ttl]

    def ttls(self, exclude_noreplies=False):
        if exclude_noreplies:
            ttls = []
            for ttl in self._hops.keys():
                if not self[ttl].is_noreply():
                    ttls.append(ttl)
        else:
            ttls = self._hops.keys()
        ttls.sort()
        return ttls

    ###########################################################################
    # Statistics                                                              #
    ###########################################################################

    def abs_rtt_mean(self):
        ttls = self.ttls(exclude_noreplies=True)
        return sum([self[ttl].abs_rtt() for ttl in ttls]) / len(ttls)

    def abs_rtt_stdev(self):
        mu = self.abs_rtt_mean()
        ttls = self.ttls(exclude_noreplies=True)
        return sqrt(sum([(self[ttl].abs_rtt() - mu)**2 for ttl in ttls]) / len(ttls))

    def rel_rtt_mean(self):
        ttls = self.ttls(exclude_noreplies=True)
        return sum([self[ttl].rel_rtt() for ttl in ttls]) / len(ttls)

    def rel_rtt_stdev(self):
        mu = self.rel_rtt_mean()
        ttls = self.ttls(exclude_noreplies=True)
        return sqrt(sum([(self[ttl].rel_rtt() - mu)**2 for ttl in ttls]) / len(ttls))

    ###########################################################################
    # Persistence                                                             #
    ###########################################################################

    def load(self, path):
        for line in open(path):
            line = line.strip().split(' ')
            ttl  = int(line[0])
            if line[1] == '*': self[ttl].noreply()
            else:
                ip  = line[1]
                rtt = float(line[2])
                self[ttl].add_reply(ip, rtt)

    def save(self, path):
        with open(path, 'w') as f:
            for ttl in self.ttls():
                if self[ttl].is_noreply():
                    f.write('%d *\n' % ttl)
                else:
                    for ip in self[ttl].replies().keys():
                        for rtt in self[ttl].replies()[ip]['rtts']:
                            f.write('%d %s %f\n' % (ttl, ip, rtt))