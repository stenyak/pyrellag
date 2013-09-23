#!/usr/bin/env python
# Copyright (c) 2013, Bruno Gonzalez <stenyak@stenyak.com>. This software is licensed under the Affero General Public License version 3 or later.  See the LICENSE file.

import os
from flask import Flask, redirect, send_file
from gallery import Gallery
app = Flask(__name__)

@app.route('/')
def root():
    return redirect("/gallery/data")

@app.route('/gallery/<path:path>')
def show_gallery(path):
    g = Gallery(path)
    g.populate()
    return g.get_html()

@app.route('/file/<path:path>')
def show_image(path):
    return send_file(path)

if __name__ == '__main__':
    app.run(debug=False)
