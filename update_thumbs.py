#!/usr/bin/env python
# Copyright (c) 2013, Bruno Gonzalez <stenyak@stenyak.com>. This software is licensed under the Affero General Public License version 3 or later.  See the LICENSE file.

import os, re, sys, Image, traceback

class Gallery:
    image_exts = ["jpg", "jpeg", "png", "gif"]
    thumbs_dirname = ".thumbs"
    html_filename = "index.htm"
    thumbs_size = 128,128
    image_thumb_ext = "jpg"
    video_thumb_ext = "gif"
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
        def remove_orphan_thumbs(filesystem_image_name_exts, filesystem_thumbs):
            orphan_thumbs = []
            for k, v in filesystem_thumbs.iteritems():
                if not k in filesystem_image_name_exts:
                    orphan_thumbs.append((k,v))
            for thumb in orphan_thumbs:
                k, v = thumb
                thumb_path = os.path.join(self.path, self.thumbs_dirname, k+v)
                os.remove(thumb_path)
                del filesystem_thumbs[k]
                print "Removed orphan thumb at %s" %thumb_path
            return len(orphan_thumbs)
        def generate_thumb(original, thumb_dir):
            basename, extension = os.path.splitext(os.path.basename(os.path.normpath(original)))
            extension = extension[1:]
            if extension in self.image_exts:
                img = Image.open(original)
                if img.mode != "RGB":
                    img = img.convert("RGB")
                def image_thumb(image, thumb_dir, basename):
                    img.thumbnail(self.thumbs_size)
                    thumb_extension = self.image_thumb_ext
                    thumb_path = os.path.join(thumb_dir, basename+"."+thumb_extension)
                    img.save(thumb_path)
                    print "Image thumb. Info is: %s" %img.info
                    return thumb_extension
                def gif_thumb(image, thumb_dir, basename):
                    print "GIF thumb. Info is: %s" %img.info
                    thumb_extension = self.video_thumb_ext
                    return thumb_extension
                def video_thumb(image, thumb_dir, basename):
                    print "Video thumb. Info is: %s" %img.info
                    thumb_extension = self.video_thumb_ext
                    return thumb_extension

                if extension == "gif":
                    try:
                        img.seek(0)
                        thumb_extension = gif_thumb(img, thumb_dir, basename)
                    except EOFError:
                        thumb_extension = image_thumb(img, thumb_dir, basename)
                else:
                    thumb_extension = image_thumb(img, thumb_dir, basename)
                return thumb_extension
            else:
                thumb_extension = video_thumb(img, thumb_dir, basename)
            return os.path.splitext(thumb_path)[1] #return extension
        def generate_missing_thumbs(filesystem_image_name_exts, filesystem_thumbs):
            generated = 0
            errors = 0
            thumb_dir = os.path.join(self.path, self.thumbs_dirname)
            if not os.path.exists(thumb_dir):
                os.makedirs(thumb_dir)
            for k, v in filesystem_image_name_exts.iteritems():
                if not k in filesystem_thumbs:
                    original = os.path.join(self.path, k+v)
                    try:
                        thumb_ext = generate_thumb(original, thumb_dir)
                        filesystem_thumbs[k] = "."+thumb_ext
                        #print "Generated %s thumbnail with extension %s" %(original, thumb_ext)
                        generated += 1
                    except IOError, e:
                        print "Couldn't create %s thumbnail:" %original
                        traceback.print_exc()
                        print ""
                        errors += 1
            return generated, errors

        filesystem_images = get_filesystem_images(self.path)
        filesystem_thumbs = get_filesystem_thumbs(self.path)
        filesystem_image_name_exts = dict([os.path.splitext(i) for i in filesystem_images])
        filesystem_thumbs = dict([os.path.splitext(i) for i in filesystem_thumbs])
        deleted = remove_orphan_thumbs(filesystem_image_name_exts, filesystem_thumbs)
        generated, generated_errors = generate_missing_thumbs(filesystem_image_name_exts, filesystem_thumbs)

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
                            overflow-y: scroll;
                            overflow-x: hidden;
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
                        #Gallery{
                            clear:both;
                        }
                        .logo {
                            width: auto;
                            float: right;
                            padding: 5px;
                            background-color: silver;
                            text-align:center;
                            text-shadow:5px 5px 10px #000000;

                            border:solid 3px grey;
                            -moz-border-radius: 38px;
                            -webkit-border-radius: 38px;
                            border-radius: 20px;

                            -moz-box-shadow:-10px 10px 5px #000000;
                            -webkit-box-shadow:-10px 10px 5px #000000;
                            box-shadow:-10px 10px 5px #000000;

                            transition:All 0.3s ease-in-out;
                            -webkit-transition:All 0.3s ease-in-out;
                            -moz-transition:All 0.3s ease-in-out;
                            -o-transition:All 0.3s ease-in-out;
                            transform: rotate(25deg) scale(1) translate(10px, -15px);
                            -webkit-transform: rotate(25deg) scale(1) translate(10px, -15px);
                            -moz-transform: rotate(25deg) scale(1) translate(10px, -15px);
                            -o-transform: rotate(25deg) scale(1) translate(10px, -15px);
                            -ms-transform: rotate(25deg) scale(1) translate(10px, -15px);
                        }
                        .logo:hover{
                            transform: rotate(5deg) scale(1.5) translate(-10px);
                            -webkit-transform: rotate(5deg) scale(1.5) translate(-10px);
                            -moz-transform: rotate(5deg) scale(1.5) translate(-10px);
                            -o-transform: rotate(5deg) scale(1.5) translate(-10px);
                            -ms-transform: rotate(5deg) scale(1.5) translate(-10px);
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
        def write_logo(f):
            f.write("\n<a clas='logo' href='https://github.com/stenyak/pyrellag'><div class='logo'>powered by<br/><b>Pyrellag!</b></div></a>")
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
            write_logo(f)
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
