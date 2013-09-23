# Copyright (c) 2013, Bruno Gonzalez <stenyak@stenyak.com>. This software is licensed under the Affero General Public License version 3 or later.  See the LICENSE file.

import sys
class Color:
    if sys.stdout.isatty():
        MAGENTA = '\033[95m'
        BLUE = '\033[94m'
        GREEN = '\033[92m'
        YELLOW = '\033[93m'
        RED = '\033[91m'
        RESET = '\033[0m'
    else:
        MAGENTA = ''
        BLUE = ''
        GREEN = ''
        YELLOW = ''
        RED = ''
        RESET = ''

