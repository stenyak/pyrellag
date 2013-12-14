#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2013, Bruno Gonzalez <stenyak@stenyak.com>. This software is licensed under the Affero General Public License version 3 or later.  See the LICENSE file.

import os, urllib, time
from functools import wraps

from flask import request, g, session, flash, url_for, abort, Flask, redirect, send_file, render_template
from flask_openid import OpenID
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from gallery import Gallery
from config import get_config as cfg


def init_globals(name, db_uri):
    def init_flask_openid(app):
        return OpenID(app)
    def init_flask(name, db_uri):
        app = Flask(name)
        app.config.update(DATABASE_URI=db_uri, SECRET_KEY='development key', DEBUG=True)
        return app
    def init_sqlalchemy(db_uri):
        engine = create_engine(db_uri)
        db_session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))
        base = declarative_base()
        base.query = db_session.query_property()
        return engine, base, db_session
    app = init_flask(name, db_uri)
    oid = init_flask_openid(app)
    engine, base, db_session = init_sqlalchemy(db_uri)
    return app, oid, engine, base, db_session

db_uri = "sqlite:///" + cfg()["profile_db_path"]
app, oid, engine, Base, db_session = init_globals(__name__, db_uri)

def init_db():
    global engine
    global Base
    Base.metadata.create_all(bind=engine)

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(String(60))
    email = Column(String(200))
    openid = Column(String(200))
    groups = Column(String(200))

    def __init__(self, name, email, openid, groups):
        self.name = name
        self.email = email
        self.openid = openid
        self.groups = groups
    def in_group(self, group):
        return group in self.groups.split(",")

def db_created():
    try:
        User.query.filter_by(openid="foobar").first()
        return True
    except:
        return False

def db_required(fn):
    @wraps(fn)
    def inner(*args, **kwargs):
        if not db_created():
            init_db()
        return fn(*args, **kwargs)
    return inner

def render_time(fn):
    @wraps(fn)
    def inner(*args, **kwargs):
        start = time.time()
        result = fn(*args, **kwargs)
        end = time.time()
        try:
            return result.replace("TTTTIME", "%.4f" %(end-start))
        except AttributeError:
            return result
    return inner

@app.before_request
@db_required
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

def get_openid_providers():
    class OpenIdProvider():
        def __init__(self, name, url, hidden=True):
            self.name = name
            self.url = url
            self.image = "openid/" + name.replace(" ", "").lower() + ".png"
            self.hidden = hidden
    return [
    OpenIdProvider("Google", "https://www.google.com/accounts/o8/id"),
    OpenIdProvider("Yahoo", "yahoo.com"),
    OpenIdProvider("WordPress", "Your WordPress blog url", False),
    OpenIdProvider("Flickr", "flickr.com"),
    OpenIdProvider("Stack Exchange", "https://openid.stackexchange.com"),
    OpenIdProvider("Blogger", "Your Blogger blog url", False),
    OpenIdProvider("LiveJournal", "Your LiveJournal blog url", False),
    OpenIdProvider("OpenID", "Your custom OpenID url", False)
    ]

@app.route('/login', methods=['GET', 'POST'])
@render_time
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
    return render_template('login.html', next=oid.get_next_url(), error=oid.fetch_error(), providers=get_openid_providers())

@db_required
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
@render_time
def create_profile():
    """If this is the user's first login, the create_or_login function will redirect here so that the user can set up his profile.  """
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
            groups = ""
            if len(User.query.all()) == 0:
                groups = "profile_editors"
            db_session.add(User(name, email, session['openid'], groups))
            db_session.commit()
            return redirect(oid.get_next_url())
    return render_template('create_profile.html', next_url=oid.get_next_url(), config=cfg())

@app.route('/profiles', methods=['GET', 'POST'])
@render_time
def edit_profiles():
    user = g.user
    if user is None:
        abort(401)
    if not user.in_group("profile_editors"):
        abort(401)
    if request.method == 'POST':
        user = User.query.filter_by(id=request.form["id"]).first()
        action = request.form["action"]
        if action == "save":
            user.name = request.form["name"]
            user.email = request.form["email"]
            user.openid = request.form["openid"]
            user.groups = request.form["groups"]
        elif action == "delete":
            db_session.delete(user)
        else:
            raise Exception("Unknown profile editing action: \"%s\"" %action)
        db_session.commit()
    profiles = User.query.all()
    return render_template('edit_profiles.html', profiles=profiles, user=user)

@app.route('/profile', methods=['GET', 'POST'])
@render_time
def edit_profile():
    user = g.user
    if user is None:
        abort(401)
    form = dict(name=user.name, email=user.email)
    if request.method == 'POST':
        if 'delete' in request.form:
            db_session.delete(user)
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
            user.name = form['name']
            user.email = form['email']
            db_session.commit()
            return redirect(url_for('edit_profile', user=user))
    return render_template('edit_profile.html', form=form, user=user)


@app.route('/logout')
def logout():
    session.pop('openid', None)
    flash(u'You have been signed out')
    return redirect(oid.get_next_url())

@app.route('/gallery/<path:path>')
@render_time
def show_gallery(path):
    global g
    user = g.user
    path = urllib.unquote(path).encode("utf-8")
    check_jailed_path(path, "data")
    g = Gallery(path, follow_freedesktop_standard = cfg()["follow_freedesktop_standard"])
    if user is not None:
        g.populate()
    return render_template("gallery.html", path = g.path.decode("utf-8"), parents = g.get_parents(), basename = os.path.basename(g.path.decode("utf-8")), nfiles = len(g.files), galleries = g.get_galleries(), files = g.get_files(), user = user)

@app.route('/video/<path:path>')
@render_time
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
