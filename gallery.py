# Copyright (c) 2013, Bruno Gonzalez <stenyak@stenyak.com>. This software is licensed under the Affero General Public License version 3 or later.  See the LICENSE file.

import sys, os, re, hashlib, shutil, PngImagePlugin, urllib
import Image as image
from stats import Stats
from color import Color

class Video:
    extensions = ["3gp", "mov", "avi", "mpeg4", "mpg4", "mp4", "mkv"]
    @staticmethod
    def is_video(path):
        extension = os.path.splitext(path)[1][1:].lower()
        return extension in Video.extensions

class Image:
    extensions = ["jpg", "jpeg", "png", "gif"]
    @staticmethod
    def is_image(path):
        extension = os.path.splitext(path)[1][1:].lower()
        return extension in Image.extensions

class Gallery:
    thumbs_dir_components = [".thumbnails", "normal"]
    thumbs_size = 128,128
    def __init__(self, path, log_freq = 0, follow_freedesktop_standard = False):
        """ path is the root directory where all the media files and subdirectories are to be found
            log_freq specifies the logging interval during the scan process (will log every log_freq-th scanned file). use a <= 0 value to disable logging
            follow_freedesktop_standard means the thumbnails are readable by other freedesktop-compliant software, but the thumbnails are dependent on the absolute path to the media files (therefore renaming your media folder means having to rebuild everything)"""
        self.stats = Stats()
        self.path = path
        self.files = []
        self.gallery_paths = []
        self.log_freq = log_freq
        self.follow_freedesktop_standard = follow_freedesktop_standard
    def should_log(self, number):
        if self.log_freq <= 0: return False
        return number % self.log_freq == 0
    def populate(self):
        def get_galleries(path):
            return [d for d in os.listdir(path) if os.path.isdir(os.path.join(self.path, d)) and not d.startswith(".")] # ignore hidden directories
        def get_filesystem_files(path):
            regexp = ".*\.(%s)$" %"|".join(Image.extensions + Video.extensions) #match any extension...
            r = re.compile(regexp, re.IGNORECASE) #...case insensitively
            paths = [os.path.join(self.path, f) for f in os.listdir(self.path)] #get relative paths
            paths = [f for f in paths if os.path.isfile(f)] #filter non-files
            paths = [f for f in paths if r.match(f)] #filter by extension
            paths = [os.path.abspath(f) for f in paths] # convert to absolute
            return paths
        def get_thumbs(path):
            thumbs_dir = os.path.join(path, *self.thumbs_dir_components)
            try:
                thumbs = [os.path.join(thumbs_dir, f) for f in os.listdir(thumbs_dir)]
                thumbs = [f for f in thumbs if os.path.isfile(f)]
            except OSError:
                thumbs = []
            return thumbs
        def remove_orphan_thumbs(files, thumbs):
            def get_basename(path):
                return os.path.splitext(os.path.basename(path))[0]
            removed = 0
            existing_checksums = [self.get_checksum(f) for f in files]
            for thumb in thumbs:
                thumb_basename = get_basename(thumb)
                if thumb_basename not in existing_checksums:
                    os.remove(thumb)
                    if self.should_log(removed):
                        sys.stdout.write("%s-%s" %(Color.BLUE, Color.RESET))
                        sys.stdout.flush()
                    removed += 1
            return removed
        def generate_missing_thumbs(files):
            def generate_thumb(f, thumb_path):
                def verify_thumb_dir(thumb_path):
                    thumb_dir = os.path.normpath(os.path.join(thumb_path, os.pardir))
                    if not os.path.isdir(thumb_dir):
                        os.makedirs(thumb_dir)
                def video_thumb(f, thumb_path):
                    verify_thumb_dir(thumb_path)
                    shutil.copyfile("video.png", thumb_path)
                def image_thumb(f, thumb_path):
                    def get_pnginfo(file_path):
                        info = PngImagePlugin.PngInfo()
                        info.add_text("Thumb::URI", self.get_uri(file_path))
                        mtime = str(os.path.getmtime(file_path))
                        info.add_text("Thumb::MTime", mtime)
                        return info
                    img = image.open(f)
                    if img.mode != "RGB":
                        img = img.convert("RGB")
                    img.thumbnail(self.thumbs_size)
                    verify_thumb_dir(thumb_path)
                    img.save(thumb_path, pnginfo=get_pnginfo(f))
                extension = os.path.splitext(f)[1][1:].lower()
                if Image.is_image(f):
                    image_thumb(f, thumb_path)
                elif Video.is_video(f):
                    video_thumb(f, thumb_path)
                else:
                    raise UnsupportedFormatError()
            generated = 0
            failed = []
            for f in files:
                thumb_path = self.get_thumb_path(f)
                if not os.path.isfile(thumb_path):
                    try:
                        generate_thumb(f, thumb_path)
                        generated += 1
                        if self.should_log(generated):
                            sys.stdout.write("%s+%s"%(Color.GREEN, Color.RESET))
                            sys.stdout.flush()
                    except IOError, e:
                        failed.append((f, e))
                        if self.should_log(0):
                            sys.stdout.write("%s!%s"%(Color.RED, Color.RESET))
                            sys.stdout.flush()
            return generated, failed

        if self.should_log(0):
            sys.stdout.write("Scanning gallery at %s " %self.path)
            sys.stdout.flush()

        self.gallery_paths = get_galleries(self.path)
        self.files = get_filesystem_files(self.path)

        thumbs = get_thumbs(self.path)
        self.stats.files = len(self.files)
        self.stats.thumbs = len(thumbs)
        self.stats.removed_thumbs = remove_orphan_thumbs(self.files, thumbs)
        self.stats.generated_thumbs, self.stats.failed_thumbs = generate_missing_thumbs(self.files)
        if self.should_log(0):
            sys.stdout.write("\n")
            sys.stdout.flush()
    def get_uri(self, abs_path):
        if self.follow_freedesktop_standard:
            return "file://" + abs_path
        else:
            return os.path.basename(abs_path)
    def get_checksum(self, abs_path):
        return hashlib.md5(self.get_uri(abs_path)).hexdigest()
    def get_thumb_path(self, f):
        thumb_dir = os.path.join(f, os.pardir, *self.thumbs_dir_components)
        thumb_path = os.path.join(thumb_dir, self.get_checksum(f)+".png")
        thumb_path = os.path.normpath(thumb_path)
        return thumb_path
    def __repr__(self):
        return self.__str__()
    def __str__(self):
        result = "%s: %s\n" %(self.path, self.files)
        for i in self.gallery_paths:
            result += "%s" %i
        return result
    def get_route(self):
        parents = []
        paths = []
        temp_paths = self.path.split(os.sep)
        for k,v in enumerate(temp_paths):
            cur_path = temp_paths[:k+1]
            paths.append(os.path.join(*cur_path).decode("utf-8"))
        for path in paths:
            parents.append( {"key": path, "value": os.path.basename(path)} )
        return parents
    def get_galleries(self):
        galleries = []
        for path in [os.path.normpath(os.path.join(self.path, path)).decode("utf-8") for path in sorted(self.gallery_paths)]:
            galleries.append( {"key": path, "value": os.path.basename(path)} )
        return galleries
    def get_files(self):
        files = []
        for cur_file in sorted(self.files):
            thumb_path = os.path.relpath(self.get_thumb_path(cur_file))
            file_path = os.path.relpath(cur_file)
            if Image.is_image(file_path):
                files.append( {"type": "image", "file_path": file_path.decode("utf-8"), "thumb_path": thumb_path.decode("utf-8")} )
            elif Video.is_video(file_path):
                files.append( {"type": "video", "file_path": file_path.decode("utf-8"), "thumb_path": thumb_path.decode("utf-8")} )
        return files
