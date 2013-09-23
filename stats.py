# Copyright (c) 2013, Bruno Gonzalez <stenyak@stenyak.com>. This software is licensed under the Affero General Public License version 3 or later.  See the LICENSE file.

from color import Color
class Stats:
    def __init__(self):
        self.files = 0
        self.thumbs = 0
        self.removed_thumbs = 0
        self.generated_thumbs = 0
        self.failed_thumbs = []
    def increase(self, stats):
        self.files += stats.files
        self.thumbs += stats.thumbs
        self.removed_thumbs += stats.removed_thumbs
        self.generated_thumbs += stats.generated_thumbs
        self.failed_thumbs += stats.failed_thumbs
    def clone(self):
        result = Stats()
        result.files = self.files
        result.thumbs = self.thumbs
        result.removed_thumbs = self.removed_thumbs
        result.generated_thumbs = self.generated_thumbs
        result.failed_thumbs = self.failed_thumbs[:]
        return result
    def __repr__(self):
        return "%s files, %s thumbs (%s generated, %s removed, %s failed)" %(self.files, self.thumbs, self.generated_thumbs, self.removed_thumbs, len(self.failed_thumbs))
    def __str__(self):
        return "%s files, %s thumbs (%s%s%s generated, %s%s%s removed, %s%s%s failed)" %(self.files, self.thumbs, Color.GREEN, self.generated_thumbs, Color.RESET, Color.BLUE, self.removed_thumbs, Color.RESET, Color.RED, len(self.failed_thumbs), Color.RESET)

