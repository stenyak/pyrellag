#!/usr/bin/env python
# Copyright (c) 2013, Bruno Gonzalez <stenyak@stenyak.com>. This software is licensed under the Affero General Public License version 3 or later.  See the LICENSE file.

import os, re, sys, Image

class Gallery:
    image_exts = ["jpg", "jpeg", "png"]
    thumbs_dirname = ".thumbs"
    html_filename = "index.htm"
    thumbs_size = 128,128
    def __init__(self, path):
        self.galleries = []
        self.path = path
    def populate(self):
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
        def remove_orphan_thumbs(filesystem_images, filesystem_thumbs):
            deleted = 0
            for t in filesystem_thumbs:
                if not t in filesystem_images:
                    thumb_path = os.path.join(self.path, self.thumbs_dirname, t)
                    os.remove(thumb_path)
                    deleted += 1
                    #print "Removed orphan thumb at %s" %thumb_path
            return deleted
        def generate_thumb(original, thumb):
            i = Image.open(original)
            i.thumbnail(self.thumbs_size)
            i.save(thumb, "JPEG")
        def generate_missing_thumbs(filesystem_images, filesystem_thumbs):
            generated = 0
            errors = 0
            thumb_dir = os.path.join(self.path, self.thumbs_dirname)
            if not os.path.exists(thumb_dir):
                os.makedirs(thumb_dir)
            for i in filesystem_images:
                if not i in filesystem_thumbs:
                    original = os.path.join(self.path, i)
                    thumb = os.path.join(thumb_dir, i)
                    try:
                        generate_thumb(original, thumb)
                        print "Generated %s thumbnail at %s" %(original, thumb)
                        generated += 1
                    except IOError, e:
                        print "Error: Couldn't create %s thumbnail at %s: %s" %(original, thumb, e)
                        errors += 1
            return generated, errors

        filesystem_images = get_filesystem_images(self.path)
        filesystem_thumbs = get_filesystem_thumbs(self.path)
        deleted = remove_orphan_thumbs(filesystem_images, filesystem_thumbs)
        generated, generated_errors = generate_missing_thumbs(filesystem_images, filesystem_thumbs)

        self.gallery_paths = get_galleries(self.path)
        self.images = filesystem_images
        return deleted, generated, generated_errors, len(self.images)
    def __repr__(self):
        return self.__str__()
    def __str__(self):
        result = "%s: %s\n" %(self.path, self.images)
        for i in self.galleries:
            result += "%s" %i
        return result
    def update_html(self):
        def write_header(f):
            pspath = [os.pardir] * len(self.path.split(os.sep)) + ["ps"]
            ps = os.path.join(*pspath)
            f.write("<html><head><title>Gallery for %s</title>\n" %self.path)
            f.write('<link href="%s/photoswipe.css" type="text/css" rel="stylesheet" />' %ps)
            f.write('<script type="text/javascript" src="%s/lib/klass.min.js"></script>' %ps)
            f.write('<script type="text/javascript" src="%s/code.photoswipe-3.0.5.min.js"></script>' %ps)
            f.write("""<style media="screen" type="text/css">
                        #subgalleries {
                           float: left;
                           width: auto;

                           padding-left: 5px;
                           padding-right: 5px;

                           border-radius: 10px;
                           -webkit-border-radius: 10px;
                           -moz-border-radius: 10px;

                           background-color: grey;

                            transition: background-color 0.5s linear;
                           -moz-transition: background-color 0.5s linear;
                           -webkit-transition: background-color 0.5s linear;
                           -ms-transition: background-color 0.5s linear;
                        }
                        #subgalleries:hover {
                           background-color: silver;
                           padding-left: 5px;
                           padding-right: 5px;
                        }
                        .hlable {
                           border-radius: 5px;
                           -webkit-border-radius: 5px;
                           -moz-border-radius: 5px;

                           background-color: transparent;

                            transition: background-color 0.1s linear;
                           -moz-transition: background-color 0.1s linear;
                           -webkit-transition: background-color 0.1s linear;
                           -ms-transition: background-color 0.1s linear;
                        }
                        .hlable:hover {
                           background-color: white;
                        }
                        .image {
                           padding: 5px;

                           border-radius: 5px;
                           -webkit-border-radius: 5px;
                           -moz-border-radius: 5px;

                           background-color: grey;

                            transition: background-color 0.2s linear;
                           -moz-transition: background-color 0.2s linear;
                           -webkit-transition: background-color 0.2s linear;
                           -ms-transition: background-color 0.2s linear;
                        }
                        .image:hover {
                           background-color: white;
                        }
                        body {
                            background-image: linear-gradient(left bottom, rgb(0,0,0) 18%, rgb(28,28,28) 100%, rgb(18,18,18) 50%);
                            background-image: -o-linear-gradient(left bottom, rgb(0,0,0) 18%, rgb(28,28,28) 100%, rgb(18,18,18) 50%);
                            background-image: -moz-linear-gradient(left bottom, rgb(0,0,0) 18%, rgb(28,28,28) 100%, rgb(18,18,18) 50%);
                            background-image: -webkit-linear-gradient(left bottom, rgb(0,0,0) 18%, rgb(28,28,28) 100%, rgb(18,18,18) 50%);
                            background-image: -ms-linear-gradient(left bottom, rgb(0,0,0) 18%, rgb(28,28,28) 100%, rgb(18,18,18) 50%);

                            background-image: -webkit-gradient(
                                    linear,
                                    left bottom,
                                    right top,
                                    color-stop(0.18, rgb(0,0,0)),
                                    color-stop(1, rgb(28,28,28)),
                                    color-stop(0.5, rgb(18,18,18))
                            );
                        }
                        .subgallery {
                                text-decoration: none;
                        }
            </style>""")
            f.write("</head><body>\n")
        def write_footer(f):
            f.write("""
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
            f.write("</body></html>")
        def write_subgalleries(f):
            f.write("\n<div id='subgalleries'>")
            paths = self.path.split(os.sep)
            for i in range(0, len(paths)-1):
                level = len(paths) - 1 - i
                path = ""
                for j in range(0, level):
                    path = os.path.join(path, os.pardir)
                f.write("<a class='hlable' href='%s'>%s</a> / " %(os.path.join(path, self.html_filename), paths[i]))
            f.write("%s (%s):" %(paths[-1], len(self.images)))
            if len(self.galleries) > 0:
                f.write("\n<ul style='margin: 0px'>")
                for g in self.galleries:
                    f.write("\n<a class='subgallery' href='%s'><li class='hlable'>%s (%s)</li></a>" %(os.path.join(os.path.basename(os.path.normpath(g.path)), self.html_filename), os.path.basename(os.path.normpath(g.path)), len(g.images)))
                f.write("\n</ul>")
            f.write("</div>")
        def write_images(f):
            f.write("\n<div id='Gallery' style='text-align:center;'>")
            for i in self.images:
                f.write("\n<a href='%s'><img class='image' src='%s' alt='Filename: %s'/></a>\n" %(i, os.path.join(self.thumbs_dirname, i), i))
            f.write("\n</div>")
        html_path = os.path.join(self.path, self.html_filename)
        with open(html_path, "w") as f:
            write_header(f)
            write_subgalleries(f)
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
