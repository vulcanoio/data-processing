#!/usr/bin/env python
# -*- coding: utf-8 -*-

from redis import StrictRedis
from helper import dict_to_md
import dateutil.parser
import time

r = StrictRedis(port=6399)
use_subset = True

names_by_events = {}
events_by_ts = {}

for key, score in r.zrevrange('timestamps', 0, -1, True):
    if score == 1:
        continue
    timestamp = time.mktime(dateutil.parser.parse(key).timetuple())
    hashes = r.smembers('{}:{}'.format('timestamp', int(timestamp)))
    for h in hashes:
        md5 = r.hget(h, 'md5')
        sha1 = r.hget(h, 'sha1')
        eids = r.smembers('{}:eids'.format(md5)).union(r.smembers('{}:eids'.format(sha1))).union(r.smembers('{}:eids'.format(h)))
        for e in eids:
            uuid = r.get('eventuuid:{}'.format(e))
            if use_subset and uuid not in r.smembers('subset'):
                continue

            if not names_by_events.get(e):
                names_by_events[e] = []
            names_by_events[e].append(key)
            if not events_by_ts.get(key):
                events_by_ts[key] = []
            events_by_ts[key].append([e, r.hget('event:{}'.format(uuid), 'info')])

dict_to_md(events_by_ts)
