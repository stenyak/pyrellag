#!/usr/bin/env python
# Copyright (c) 2013, Bruno Gonzalez <stenyak@stenyak.com>. This software is licensed under the Affero General Public License version 3 or later.  See the LICENSE file.

import json

def get_config():
    with open("config.json", "r") as f:
        return json.loads(f.read())

