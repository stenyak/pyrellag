#!/usr/bin/env python
# Copyright (c) 2013, Bruno Gonzalez <stenyak@stenyak.com>. This software is licensed under the Affero General Public License version 3 or later.  See the LICENSE file.

import os, re, sys, Image, traceback, shutil

class UnsupportedFormatError(Exception): pass

class Gallery:
    image_exts = ["jpg", "jpeg", "png", "gif"]
    video_exts = ["3gp", "mov", "avi", "mpeg4", "mpg4", "mp4", "mkv"]
    thumbs_dirname = ".thumbs"
    html_filename = "index.htm"
    thumbs_size = 128,128
    image_thumb_ext = "jpg"
    video_thumb_ext = "gif"
    def __init__(self, path):
        self.galleries = []
        self.path = path
    def populate(self):
        def get_filesystem_videos(path):
            regexp = ".*\.(%s)$" %"|".join(self.video_exts)
            r = re.compile(regexp, re.IGNORECASE)
            images = [f for f in os.listdir(self.path) if os.path.isfile(os.path.join(self.path, f)) and r.match(f)]
            return images
        def get_filesystem_images(path):
            regexp = ".*\.(%s)$" %"|".join(self.image_exts)
            r = re.compile(regexp, re.IGNORECASE)
            images = [f for f in os.listdir(self.path) if os.path.isfile(os.path.join(self.path, f)) and r.match(f)]
            return images
        def get_filesystem_thumbs(path):
            thumbs_dir = os.path.join(path, self.thumbs_dirname)
            result = []
            if os.path.isdir(thumbs_dir):
                result = [f for f in os.listdir(os.path.join(self.path, self.thumbs_dirname)) if os.path.isfile(os.path.join(self.path, self.thumbs_dirname, f))]
            return result
        def get_galleries(path):
            return [d for d in os.listdir(self.path) if os.path.isdir(os.path.join(self.path, d)) and d != self.thumbs_dirname]
        def remove_orphan_thumbs(filesystem_file_name_exts, filesystem_thumbs):
            orphan_thumbs = []
            for k, v in filesystem_thumbs.iteritems():
                if not k in filesystem_file_name_exts:
                    orphan_thumbs.append((k,v))
            for thumb in orphan_thumbs:
                k, v = thumb
                thumb_path = os.path.join(self.path, self.thumbs_dirname, k+v)
                os.remove(thumb_path)
                del filesystem_thumbs[k]
                print "Removed orphan thumb at %s" %thumb_path
            return len(orphan_thumbs)
        def generate_thumb(original, thumb_dir):
            def image_thumb(image, thumb_dir, basename):
                img.thumbnail(self.thumbs_size)
                thumb_path = os.path.join(thumb_dir, basename+"."+self.image_thumb_ext)
                img.save(thumb_path)
                print "writen image path: %s" %thumb_path
                return self.image_thumb_ext
            def gif_thumb(image, thumb_dir, basename):
                if image.mode != "RGB":
                    image = image.convert("RGB")
                thumb_path = os.path.join(thumb_dir, basename+"."+self.video_thumb_ext)
                shutil.copyfile("video.gif", thumb_path)
                return self.video_thumb_ext
            def video_thumb(original, thumb_dir, basename):
                thumb_path = os.path.join(thumb_dir, basename+"."+self.video_thumb_ext)
                shutil.copyfile("video.gif", thumb_path)
                return self.video_thumb_ext
            basename, extension = os.path.splitext(os.path.basename(os.path.normpath(original)))
            extension = extension[1:].lower()
            if extension in self.image_exts:
                img = Image.open(original)
                if extension == "gif":
                    try:
                        img.seek(0)
                        thumb_extension = gif_thumb(img, thumb_dir, basename)
                    except EOFError:
                        thumb_extension = image_thumb(img, thumb_dir, basename)
                else:
                    thumb_extension = image_thumb(img, thumb_dir, basename)
                return thumb_extension
            elif extension in self.video_exts:
                thumb_extension = video_thumb(original, thumb_dir, basename)
            else:
                raise UnsupportedFormatError()
            return thumb_extension
        def generate_missing_thumbs(filesystem_file_name_exts, filesystem_thumbs):
            generated = 0
            errors = 0
            thumb_dir = os.path.join(self.path, self.thumbs_dirname)
            if not os.path.exists(thumb_dir):
                os.makedirs(thumb_dir)
            for k, v in filesystem_file_name_exts.iteritems():
                if not k in filesystem_thumbs:
                    original = os.path.join(self.path, k+v)
                    try:
                        thumb_ext = generate_thumb(original, thumb_dir)
                        filesystem_thumbs[k] = ".%s" %thumb_ext
                        #print "Generated %s thumbnail for %s" %(thumb_ext, original)
                        generated += 1
                    except UnsupportedFormatError, e:
                        print "Unsupported format, couldn't create thumbnail for %s" %original
                        errors += 1
                    except Exception, e:
                        print "Unknown error, couldn't create thumbnail for %s" %original
                        traceback.print_exc()
                        print ""
                        errors += 1
            return generated, errors

        filesystem_images = get_filesystem_images(self.path)
        filesystem_videos = get_filesystem_videos(self.path)
        filesystem_thumbs = get_filesystem_thumbs(self.path)
        filesystem_image_name_exts = [os.path.splitext(i) for i in filesystem_images]
        filesystem_video_name_exts = [os.path.splitext(i) for i in filesystem_videos]
        filesystem_file_name_exts = dict(filesystem_image_name_exts + filesystem_video_name_exts)
        filesystem_thumbs = dict([os.path.splitext(i) for i in filesystem_thumbs])
        deleted = remove_orphan_thumbs(filesystem_file_name_exts, filesystem_thumbs)
        generated, generated_errors = generate_missing_thumbs(filesystem_file_name_exts, filesystem_thumbs)

        self.gallery_paths = get_galleries(self.path)
        self.images = filesystem_images
        self.videos = filesystem_videos
        return deleted, generated, generated_errors, len(self.images)
    def __repr__(self):
        return self.__str__()
    def __str__(self):
        result = "%s: %s\n" %(self.path, self.images)
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
            fwrite(f, "%s (%s):" %(paths[-1], len(self.images)))
            if len(self.galleries) > 0:
                fwrite(f, "<ul style='margin: 0px'>")
                for g in self.galleries:
                    fwrite(f, "<a class='subgallery' href='%s'><li class='hlable'>%s (%s)</li></a>" %(os.path.join(os.path.basename(os.path.normpath(g.path)), self.html_filename), os.path.basename(os.path.normpath(g.path)), len(g.images)))
                fwrite(f, "</ul>")
            fwrite(f, "</div>")
        def write_images(f):
            fwrite(f, "<div id='Gallery' style='text-align:center;'>")
            for i in self.images:
                fwrite(f, "<a href='%s'><img class='image' src='%s' alt='Filename: %s'/></a>" %(i, os.path.splitext(os.path.join(self.thumbs_dirname, i))[0]+"."+self.image_thumb_ext, i))
            fwrite(f, "</div>")
        def write_videos(f):
            fwrite(f, "<div id='Videos' style='text-align:center;'>")
            for i in self.videos:
                fwrite(f, "<a href='%s'><img class='image' src='%s' alt='Filename: %s'/></a>" %(i, os.path.splitext(os.path.join(self.thumbs_dirname, i))[0]+"."+self.video_thumb_ext, i))
            fwrite(f, "</div>")
        html_path = os.path.join(self.path, self.html_filename)
        with open(html_path, "w") as f:
            write_header(f)
            write_logo(f)
            write_subgalleries(f)
            fwrite(f, "<div style='clear:both'/>")
            write_videos(f)
            write_images(f)
            write_footer(f)


def recursive_populate(path):
    gallery = Gallery(path)
    totupdated, totdeleted, totgenerated, totgenerated_errors, totimages = 0, 0, 0, 0, 0
    deleted, generated, generated_errors, images = gallery.populate()
    for g in gallery.gallery_paths:
        subgallery, subdeleted, subgenerated, subgenerated_errors, subimages, subupdated = recursive_populate(os.path.join(gallery.path, g))
        gallery.galleries.append(subgallery)
        totdeleted += subdeleted
        totgenerated += subgenerated
        totgenerated_errors += subgenerated_errors
        totimages += subimages
        totupdated += subupdated

    totdeleted += deleted
    totgenerated += generated
    totgenerated_errors += generated_errors
    totimages += images

    if generated + deleted > 0 or not os.path.isfile(os.path.join(path, Gallery.html_filename)):
        gallery.update_html()
        totupdated += 1
    return gallery, totdeleted, totgenerated, totgenerated_errors, totimages, totupdated

g, deleted, generated, generated_errors, images, updated = recursive_populate(sys.argv[1])
print ""
print "Stats:"
print " * total detected images: %s" %images
print " * deleted thumbnails: %s" %deleted
print " * generated thumbnails: %s (and %s errors)" %(generated, generated_errors)
print " * updated html indexes: %s" %updated
