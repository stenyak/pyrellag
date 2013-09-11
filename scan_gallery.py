#!/usr/bin/env python
# Copyright (c) 2013, Bruno Gonzalez <stenyak@stenyak.com>. This software is licensed under the Affero General Public License version 3 or later.  See the LICENSE file.

import os, re, sys, Image, shutil, hashlib, PngImagePlugin

class UnsupportedFormatError(Exception): pass

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
        return self.__str__()
    def __str__(self):
        return "%s files,\t %s thumbs\t (%s generated,\t %s removed,\t %s failed)" %(self.files, self.thumbs, self.generated_thumbs, self.removed_thumbs, len(self.failed_thumbs))

class Gallery:
    image_exts = ["jpg", "jpeg", "png", "gif"]
    video_exts = ["3gp", "mov", "avi", "mpeg4", "mpg4", "mp4", "mkv"]
    thumbs_dir_components = [".thumbnails", "normal"]
    html_filename = "index.htm"
    thumbs_size = 128,128
    def __init__(self, path):
        self.stats = Stats()
        self.galleries = []
        self.path = path
    def populate(self):
        def get_galleries(path):
            return [d for d in os.listdir(path) if os.path.isdir(os.path.join(self.path, d)) and d != self.thumbs_dir_components[0]]
        def get_filesystem_files(path):
            regexp = ".*\.(%s)$" %"|".join(self.image_exts + self.video_exts) #match any extension...
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
                    img = Image.open(f)
                    if img.mode != "RGB":
                        img = img.convert("RGB")
                    img.thumbnail(self.thumbs_size)
                    verify_thumb_dir(thumb_path)
                    img.save(thumb_path, pnginfo=get_pnginfo(f))
                extension = os.path.splitext(f)[1][1:].lower()
                if extension in self.image_exts:
                    image_thumb(f, thumb_path)
                elif extension in self.video_exts:
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
                    except IOError, e:
                        failed.append((f, e))
            return generated, failed


        self.gallery_paths = get_galleries(self.path)
        self.files = get_filesystem_files(self.path)

        thumbs = get_thumbs(self.path)
        self.stats.files = len(self.files)
        self.stats.thumbs = len(thumbs)
        self.stats.removed_thumbs = remove_orphan_thumbs(self.files, thumbs)
        self.stats.generated_thumbs, self.stats.failed_thumbs = generate_missing_thumbs(self.files)
    def get_uri(self, abs_path):
        return "file://" + abs_path
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
        for i in self.galleries:
            result += "%s" %i
        return result
    def update_html(self):
        def fwrite(f, text):
            f.write(text)
            f.write("\n")
        def write_header(f):
            pspath = [os.pardir] * len(self.path.split(os.sep)) + ["ps"]
            ps = os.path.join(*pspath)
            fwrite(f, "<html><head><title>Gallery for %s</title>" %self.path)
            fwrite(f, '<link href="%s/photoswipe.css" type="text/css" rel="stylesheet" />' %ps)
            fwrite(f, '<script type="text/javascript" src="%s/lib/klass.min.js"></script>' %ps)
            fwrite(f, '<script type="text/javascript" src="%s/code.photoswipe-3.0.5.min.js"></script>' %ps)
            fwrite(f, '<style media="screen" type="text/css">')
            fwrite(f, open("pyrellag.css", "r").read())
            fwrite(f, '</style>')
            fwrite(f, "</head><body>")
        def write_footer(f):
            fwrite(f, """
                <script>
                    document.addEventListener(
                        'DOMContentLoaded',
                        function()
                        {
                            var myPhotoSwipe = Code.PhotoSwipe.attach( window.document.querySelectorAll('#Gallery a'), { enableMouseWheel: true , enableKeyboard: true, imageScaleMethod: 'fitNoUpscale', loop: false } );
                        },
                        false
                    );
                </script>""")
            fwrite(f, "</body></html>")
        def write_logo(f):
            fwrite(f, "<a clas='logo' href='https://github.com/stenyak/pyrellag'><div class='logo'>powered by<br/><b>Pyrellag!</b></div></a>")
        def write_subgalleries(f):
            fwrite(f, "<div id='subgalleries'>")
            paths = self.path.split(os.sep)
            for i in range(0, len(paths)-1):
                level = len(paths) - 1 - i
                path = ""
                for j in range(0, level):
                    path = os.path.join(path, os.pardir)
                fwrite(f, "<a class='hlable' href='%s'>%s</a> / " %(os.path.join(path, self.html_filename), paths[i]))
            fwrite(f, "%s (%s):" %(paths[-1], len(self.files)))
            if len(self.galleries) > 0:
                fwrite(f, "<ul style='margin: 0px'>")
                for g in self.galleries:
                    fwrite(f, "<a class='subgallery' href='%s'><li class='hlable'>%s (%s)</li></a>" %(os.path.join(os.path.basename(os.path.normpath(g.path)), self.html_filename), os.path.basename(os.path.normpath(g.path)), len(g.files)))
                fwrite(f, "</ul>")
            fwrite(f, "</div>")
        def write_files(f):
            fwrite(f, "<div id='Gallery' style='text-align:center;'>")
            for cur_file in sorted(self.files):
                thumb_path = os.path.relpath(self.get_thumb_path(cur_file), self.path)
                file_path = os.path.relpath(cur_file, self.path)
                fwrite(f, "<a href='%s'><img class='image' src='%s' alt='Filename: %s'/></a>" %(file_path, thumb_path, file_path))
            fwrite(f, "</div>")
        html_path = os.path.join(self.path, self.html_filename)
        with open(html_path, "w") as f:
            write_header(f)
            write_logo(f)
            write_subgalleries(f)
            fwrite(f, "<div style='clear:both'/>")
            write_files(f)
            write_footer(f)

def recursive_populate(path):
    gallery = Gallery(path)
    gallery.populate()
    stats = gallery.stats.clone()
    for g in gallery.gallery_paths:
        subgallery, substats = recursive_populate(os.path.join(gallery.path, g))
        gallery.galleries.append(subgallery)
        stats.increase(substats)

    gallery.update_html()
    return gallery, stats

if len(sys.argv) < 2:
    print "Need to specify the root gallery directory as first parameter."
    sys.exit(1)
root_gallery_path = sys.argv[1]
g, stats = recursive_populate(root_gallery_path)
print "Total stats: %s" %stats
if len(stats.failed_thumbs) > 0:
    print "There were errors when generating thumbnails for the following files:"
    for fail in stats.failed_thumbs:
        print " * %s: %s" %(fail[0], fail[1])
