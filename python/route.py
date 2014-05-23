from math import sqrt
import pygeoip

class Geolocator:
    def __init__(self):
        self._gi    = pygeoip.GeoIP('data/GeoLiteCity.dat')

    def geolocate(self, ip):
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

class Reply:
    def __init__(self, type, rtt):
        self.type = type
        self.rtt  = rtt

class Gateway:
    def __init__(self, ip, geolocator):
        location, latitude, longitude = geolocator.geolocate(ip)
        self.ip        = ip
        self.location  = location
        self.latitude  = latitude
        self.longitude = longitude
        self.replies   = []

    def has_location(self):
        return self.location  != '*' and \
               self.latitude  != '*' and \
               self.longitude != '*'

class Hop:
    def __init__(self, ttl, route, geolocator):
        self._ttl        = ttl
        self._noreply    = False
        self._gateways   = {}
        self._replies    = {}
        self._route      = route
        self._geolocator = geolocator

    ###########################################################################
    # Insertion                                                               #
    ###########################################################################

    def add_reply(self, ip, type, rtt):
        if ip not in self._gateways.keys():
            self._gateways[ip] = Gateway(ip, self._geolocator)
        self._gateways[ip].replies.append(Reply(type, rtt))

    ###########################################################################
    # Retrieval                                                               #
    ###########################################################################

    def is_noreply(self):
        return len(self._gateways) == 0

    def gateway_ips(self):
        return self._gateways.keys()

    def gateway(self, ip):
        return self._gateways[ip]

    def main_gateway(self):
        main = None
        for gateway in self._gateways.values():
            if main is None or len(gateway.replies) > len(main.replies):
                main = gateway
        return main

    def is_destination(self):
        return self.main_gateway().ip == self._route.dst_ip

    ###########################################################################
    # Statistics                                                              #
    ###########################################################################

    def abs_rtt(self):
        total = 0
        n = 0
        for ip in self.gateway_ips():
            total += sum([reply.rtt for reply in self.gateway(ip).replies])
            n += len(self.gateway(ip).replies)
        return 0 if n == 0 else total / n

    def abs_rtt_stdev(self):
        mu = self.abs_rtt()
        rtts = []
        for ip in self.gateway_ips():
            for reply in self.gateway(ip).replies:
                rtts.append(reply.rtt)
        return sqrt(sum([(rtt - mu)**2 for rtt in rtts]) / len(rtts))

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
    def __init__(self, dst_ip=None, max_ttl=None):
        self.dst_ip      = dst_ip
        self._hops       = {}
        self._geolocator = Geolocator()

    ###########################################################################
    # Hops                                                                    #
    ###########################################################################

    def __getitem__(self, ttl):
        if ttl not in self._hops.keys():
            self._hops[ttl] = Hop(ttl, self, self._geolocator)
        return self._hops[ttl]

    def ttls(self, exclude_noreply=False, limit_to_destination=False):
        ttls = self._hops.keys()
        ttls.sort()

        if exclude_noreply:
            ttls = [ttl for ttl in ttls if not self[ttl].is_noreply()]

        if limit_to_destination:
            limited_ttls = []
            for ttl in ttls:
                limited_ttls.append(ttl)
                if self[ttl].is_destination(): break
            ttls = limited_ttls

        return ttls

    ###########################################################################
    # Statistics                                                              #
    ###########################################################################

    def abs_rtt_mean(self):
        ttls = self.ttls()
        return sum([self[ttl].abs_rtt() for ttl in ttls]) / len(ttls)

    def abs_rtt_stdev(self):
        mu = self.abs_rtt_mean()
        ttls = self.ttls()
        return sqrt(sum([(self[ttl].abs_rtt() - mu)**2 for ttl in ttls]) / len(ttls))

    def rel_rtt_mean(self):
        ttls = self.ttls()
        return sum([self[ttl].rel_rtt() for ttl in ttls]) / len(ttls)

    def rel_rtt_stdev(self):
        mu = self.rel_rtt_mean()
        ttls = self.ttls()
        return sqrt(sum([(self[ttl].rel_rtt() - mu)**2 for ttl in ttls]) / len(ttls))

    ###########################################################################
    # Persistence                                                             #
    ###########################################################################

    def load(self, path):
        first = True
        for line in open(path):
            if first:
                self.dst_ip = line.strip()
                first = False
            else:
                line = line.strip().split(' ')
                ttl  = int(line[0])
                ip   = line[1]
                type = int(line[2])
                rtt = float(line[3])
                self[ttl].add_reply(ip, type, rtt)

    def save(self, path):
        with open(path, 'w') as f:
            f.write('%s\n' % self.dst_ip)
            for ttl in self.ttls():
                for ip in self[ttl].gateway_ips():
                    for reply in self[ttl].gateway(ip).replies:
                        f.write('%d %s %d %f\n' % (ttl, ip, reply.type, reply.rtt))