#!/usr/bin/env python2
# coding: utf-8

import route

r = route.Route()
r.add_reply(1, '192.168.1.1', 20.24)
r.add_reply(1, '192.168.1.2', 15.73)
r.add_reply(2, '192.168.1.5', 115.73)
r.add_noreply(3)
r.add_reply(4, '200.32.3.42', 123.56)
r.add_reply(5, '2.4.8.16', 200.532)
r.save('/dev/stdout')
