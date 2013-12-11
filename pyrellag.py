#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2013, Bruno Gonzalez <stenyak@stenyak.com>. This software is licensed under the Affero General Public License version 3 or later.  See the LICENSE file.

from flask import request, g, session, flash, url_for, abort
from flask_openid import OpenID

from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import os, urllib, time
from flask import Flask, redirect, send_file, render_template
from gallery import Gallery
app = Flask(__name__)
app.config.update(
    DATABASE_URI = 'sqlite:////tmp/flask-openid.db',
    SECRET_KEY = 'development key',
    DEBUG = True
)
# setup flask-openid
oid = OpenID(app)
def init_db():
    Base.metadata.create_all(bind=engine)


# setup sqlalchemy
engine = create_engine(app.config['DATABASE_URI'])
db_session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))
Base = declarative_base()
Base.query = db_session.query_property()


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(String(60))
    email = Column(String(200))
    openid = Column(String(200))

    def __init__(self, name, email, openid):
        self.name = name
        self.email = email
        self.openid = openid

@app.before_request
def before_request():
    g.user = None
    if 'openid' in session:
        g.user = User.query.filter_by(openid=session['openid']).first()


@app.after_request
def after_request(response):
    db_session.remove()
    return response


@app.route('/favicon.ico')
def favicon():
    return send_file("static/favicon.ico")

@app.route('/')
def index():
    return redirect("/gallery/data")

@app.route('/login', methods=['GET', 'POST'])
@oid.loginhandler
def login():
    """Does the login via OpenID.  Has to call into `oid.try_login` to start the OpenID machinery.  """
    # if we are already logged in, go back to were we came from
    if g.user is not None:
        return redirect(oid.get_next_url())
    if request.method == 'POST':
        openid = request.form.get('openid')
        if openid:
            return oid.try_login(openid, ask_for=['email', 'fullname', 'nickname'])
    return render_template('login.html', next=oid.get_next_url(), error=oid.fetch_error())

@oid.after_login
def create_or_login(resp):
    """This is called when login with OpenID succeeded and it's not necessary to figure out if this is the users's first login or not.  This function has to redirect otherwise the user will be presented with a terrible URL which we certainly don't want.  """
    session['openid'] = resp.identity_url
    user = User.query.filter_by(openid=resp.identity_url).first()
    if user is not None:
        flash(u'Successfully signed in')
        g.user = user
        return redirect(oid.get_next_url())
    return redirect(url_for('create_profile', next=oid.get_next_url(), name=resp.fullname or resp.nickname, email=resp.email))


@app.route('/create-profile', methods=['GET', 'POST'])
def create_profile():
    """If this is the user's first login, the create_or_login function
    will redirect here so that the user can set up his profile.
    """
    if g.user is not None or 'openid' not in session:
        return redirect(url_for('index'))
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        if not name:
            flash(u'Error: you have to provide a name')
        elif '@' not in email:
            flash(u'Error: you have to enter a valid email address')
        else:
            flash(u'Profile successfully created')
            db_session.add(User(name, email, session['openid']))
            db_session.commit()
            return redirect(oid.get_next_url())
    return render_template('create_profile.html', next_url=oid.get_next_url())


@app.route('/profile', methods=['GET', 'POST'])
def edit_profile():
    """Updates a profile"""
    if g.user is None:
        abort(401)
    form = dict(name=g.user.name, email=g.user.email)
    if request.method == 'POST':
        if 'delete' in request.form:
            db_session.delete(g.user)
            db_session.commit()
            session['openid'] = None
            flash(u'Profile deleted')
            return redirect(url_for('index'))
        form['name'] = request.form['name']
        form['email'] = request.form['email']
        if not form['name']:
            flash(u'Error: you have to provide a name')
        elif '@' not in form['email']:
            flash(u'Error: you have to enter a valid email address')
        else:
            flash(u'Profile successfully created')
            g.user.name = form['name']
            g.user.email = form['email']
            db_session.commit()
            return redirect(url_for('edit_profile'))
    return render_template('edit_profile.html', form=form)


@app.route('/logout')
def logout():
    session.pop('openid', None)
    flash(u'You have been signed out')
    return redirect(oid.get_next_url())

@app.route('/gallery/<path:path>')
def show_gallery(path):
    global g
    user = g.user
    start = time.time()
    path = urllib.unquote(path).encode("utf-8")
    check_jailed_path(path, "data")
    g = Gallery(path)
    if user is not None:
        g.populate()
    result = render_template("gallery.html", path = g.path.decode("utf-8"), parents = g.get_parents(), basename = os.path.basename(g.path.decode("utf-8")), nfiles = len(g.files), galleries = g.get_galleries(), files = g.get_files(), user = user)
    end = time.time()
    result = result.replace("TTTTIME", "%.4f" %(end-start))
    return result

@app.route('/video/<path:path>')
def show_video(path):
    global g
    user = g.user
    if user is None:
        abort(401)
    video_path = urllib.unquote(path).encode("utf-8")
    path = os.path.dirname(video_path)
    check_jailed_path(path, "data")
    return render_template("video.html", video_path = video_path, path = path, video_basename = os.path.basename(video_path), user = user)

def check_jailed_path(path, jail_path):
    if os.path.normpath(path) == jail_path:
        return
    if not os.path.normpath(path).startswith(jail_path + os.sep):
        raise Exception("Permission denied, '%s' is outside '%s'" %(path, jail_path))

@app.route('/data/<path:path>')
def show_data(path):
    global g
    user = g.user
    if user is None:
        abort(401)
    path = urllib.unquote(path).encode("utf-8")
    check_jailed_path(path, "data")
    return send_file(path)

@app.route('/static/<path:path>')
def show_static(path):
    path = os.path.join("static", urllib.unquote(path).encode("utf-8"))
    check_jailed_path(path, "static")
    return send_file(path)

if __name__ == '__main__':
    app.run(debug=True)
