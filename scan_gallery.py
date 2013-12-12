#!/usr/bin/env python
# Copyright (c) 2013, Bruno Gonzalez <stenyak@stenyak.com>. This software is licensed under the Affero General Public License version 3 or later.  See the LICENSE file.

import os, sys
import json
from gallery import Gallery
from stats import Stats

def get_config():
    with open("config.json", "r") as f:
        return json.loads(f.read())

class UnsupportedFormatError(Exception): pass

def recursive_populate(path, log_freq):
    gallery = Gallery(path, log_freq)
    gallery.populate()
    stats = gallery.stats.clone()
    for g in gallery.gallery_paths:
        subgallery, substats = recursive_populate(os.path.join(gallery.path, g), log_freq)
        stats.increase(substats)
    return gallery, stats

log_freq = 5
g, stats = recursive_populate(path="data", log_freq=log_freq)
if log_freq > 0:
    sys.stdout.write("\n")

print "Total stats: %s" %stats
if len(stats.failed_thumbs) > 0:
    print "There were errors when generating thumbnails for the following files:"
    for fail in stats.failed_thumbs:
        print " %s* %s: %s%s" %(Color.RED, fail[0], fail[1], Color.RESET)
