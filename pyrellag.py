#!/usr/bin/env python
# Copyright (c) 2013, Bruno Gonzalez <stenyak@stenyak.com>. This software is licensed under the Affero General Public License version 3 or later.  See the LICENSE file.

import os, urllib, time
from flask import Flask, redirect, send_file, render_template
from gallery import Gallery
app = Flask(__name__)

@app.route('/favicon.ico')
def favicon():
    return send_file("favicon.ico")

@app.route('/')
def root():
    return redirect("/gallery/data")

@app.route('/gallery/<path:path>')
def show_gallery(path):
    start = time.time()
    path = urllib.unquote(path).encode("utf-8")
    g = Gallery(path)
    g.populate()
    result = render_template("gallery.html", path = g.path.decode("utf-8"), parents = g.get_parents(), basename = os.path.basename(g.path.decode("utf-8")), nfiles = len(g.files), galleries = g.get_galleries(), files = g.get_files())
    end = time.time()
    result = result.replace("TTTTIME", "%.4f" %(end-start))
    return result

@app.route('/file/<path:path>')
def show_image(path):
    path = urllib.unquote(path).encode("utf-8")
    return send_file(path)

if __name__ == '__main__':
    app.run(debug=False)
