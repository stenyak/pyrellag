#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2013, Bruno Gonzalez <stenyak@stenyak.com>. This software is licensed under the Affero General Public License version 3 or later.  See the LICENSE file.

import os, urllib, time
import json
from functools import wraps

from flask import request, g, session, flash, url_for, abort, Flask, redirect, send_file, render_template
from flask_openid import OpenID

from gallery import Gallery
from config import get_config as cfg


def init_flask_openid(app):
    return OpenID(app)
def init_flask(name):
    app = Flask(name)
    app.config.update(SECRET_KEY='development key', DEBUG=True)
    return app

app = init_flask(__name__)
oid = init_flask_openid(app)

from user import UserList
user_list = UserList()

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
def before_request():
    g.user = None
    if 'openid' in session:
        g.user = user_list.get_by_openid(session['openid'])


@app.after_request
def after_request(response):
    user_list.save()
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

def is_in_group(user, group):
    return user is not None and group in user["groups"]

def is_admin_mode(user):
    if not is_in_group(user, "administrators"):
        return False
    try:
        return session["admin_mode"]
    except KeyError:
        return False

def render(*args, **kwargs):
    global g
    user = g.user
    return render_template(*args, debug=cfg()["debug_mode_enabled"], admin_mode=is_admin_mode(user), user=user, **kwargs)

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
    return render('login.html', next=oid.get_next_url(), error=oid.fetch_error(), providers=get_openid_providers())

@oid.after_login
def create_or_login(resp):
    """This is called when login with OpenID succeeded and it's not necessary to figure out if this is the users's first login or not.  This function has to redirect otherwise the user will be presented with a terrible URL which we certainly don't want.  """
    session['openid'] = resp.identity_url
    user = user_list.get_by_openid(resp.identity_url)
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
    if not cfg()["profile_creation_enabled"]:
        return render('create_profile.html', authn_error="profile creation has been disabled by the administrator.")
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        if not name:
            flash(u'Error: you have to provide a name')
        elif '@' not in email:
            flash(u'Error: you have to enter a valid email address')
        else:
            flash(u'Profile successfully created')
            groups = []
            if user_list.total() == 0:
                groups.append("administrators")
            user_list.add_new(name, email, session['openid'], groups)
            return redirect(oid.get_next_url())
    return render('create_profile.html', next_url=oid.get_next_url())

@app.route('/profiles', methods=['GET', 'POST'])
@render_time
def edit_profiles():
    user = g.user
    if not is_admin_mode(user):
        return render('edit_profiles.html', authn_error=True)
    if request.method == 'POST':
        user = user_list.get_by_id(int(request.form["id"]))
        action = request.form["action"]
        if action == "save":
            user["name"] = request.form["name"]
            user["email"] = request.form["email"]
            user["openid"] = request.form["openid"]
            user["groups"] = request.form["groups_string"].split()
            user_list.set(user)
        elif action == "delete":
            user_list.delete(user)
        else:
            raise Exception("Unknown profile editing action: \"%s\"" %action)
    profiles = user_list.get_all()
    return render('edit_profiles.html', profiles=profiles)

@app.route('/config', methods=['GET', 'POST'])
@render_time
def edit_config():
    user = g.user
    if not is_admin_mode(user):
        return render('edit_config.html', authn_error=True)
    def get_rows(textarea):
        return len(textarea.split("\n")) * 1.2
    def format_json(json_string):
        return json.dumps(json_string, indent=4, sort_keys=True, separators=(",", " : "))

    config = format_json(cfg())
    if request.method == 'POST':
        action = request.form["action"]
        if action == "save":
            config = request.form["config"]
            try:
                tmp = json.loads(config)
                config = format_json(tmp)
            except ValueError, ve:
                return render('edit_config.html', config=config, rows=get_rows(config), error="configuration syntax error.")
            with open("config.json", "w") as f:
                f.write(config)
                f.flush()
        elif action == "revert":
            pass
        else:
            raise Exception("Unknown config editing action: \"%s\"" %action)
    return render('edit_config.html', config=config, rows=get_rows(config))

@app.route('/profile', methods=['GET', 'POST'])
@render_time
def edit_profile():
    user = g.user
    if user is None:
        return render('edit_profile.html', authn_error="only logged in users can edit their profile")
    form = dict(name=user["name"], email=user["email"])
    if request.method == 'POST':
        if 'enable_admin_mode' in request.form:
            if not is_in_group(user, "administrators"):
                return render('edit_profile.html', authn_error=True)
            session["admin_mode"] = True
            if "next" in request.form:
                return redirect(request.form["next"])
            return render('edit_profile.html', form=form)
        if 'disable_admin_mode' in request.form:
            if not is_admin_mode(user):
                return render('edit_profile.html', authn_error=True)
            session["admin_mode"] = False
            if "next" in request.form:
                return redirect(request.form["next"])
            return render('edit_profile.html', form=form)
        if 'delete' in request.form:
            user_list.delete(user)
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
            user["name"] = form['name']
            user["email"] = form['email']
            user_list.set(user)
            return redirect(url_for('edit_profile', user=user))
    return render('edit_profile.html', form=form)


@app.route('/logout')
def logout():
    session.pop('openid', None)
    flash(u'You have been signed out')
    return redirect(oid.get_next_url())

def set_access_groups(path, groups):
    """ set groups that are authorized to read the specified directory """
    with open(os.path.join(path, ".access"), "w") as f:
        f.write("\n".join(groups))
        f.flush()
def get_access_groups(path):
    """ get groups that are authorized to read the specified directory """
    try:
        with open(os.path.join(path, ".access"), "r") as f:
            return f.read().split()
    except IOError:
        return []

def access_permitted(allowed_groups, user_groups):
    """ check if any of the user groups is in the list of allowed groups """
    return bool(set(allowed_groups).intersection(set(user_groups)))

def get_route(path):
    route = []
    paths = []
    temp_paths = path.split(os.sep)
    for k,v in enumerate(temp_paths):
        cur_path = temp_paths[:k+1]
        paths.append(os.path.join(*cur_path).decode("utf-8"))
    for p in paths:
        route.append( {"key": p, "value": os.path.basename(p)} )
    return route

@app.route('/gallery/<path:path>', methods=['GET', 'POST'])
@render_time
def show_gallery(path):
    global g
    user = g.user
    if user is None and not cfg()["public_access"]:
        return render("gallery.html", authn_error="only logged in users may view this page")
    path = urllib.unquote(path).encode("utf-8")
    check_jailed_path(path, "data")
    groups = get_access_groups(path.encode("utf-8"))
    if not cfg()["public_access"]:
        if not is_admin_mode(user) and not access_permitted(groups, user["groups"]):
            return render("gallery.html", authn_error=True)

    gallery = Gallery(path, follow_freedesktop_standard = cfg()["follow_freedesktop_standard"])
    gallery.populate()
    if cfg()["public_access"] or is_admin_mode(user):
        galleries = gallery.get_galleries()
    else:
        galleries = [gal for gal in gallery.get_galleries() if access_permitted(get_access_groups(gal["key"].encode("utf-8")), user["groups"])]
    groups_error = None
    if request.method == 'POST':
        action = request.form["action"]
        if action == "save":
            if not is_admin_mode(user):
                return render("gallery.html", authn_error=True)
            groups = request.form["groups_string"].split()
            try:
                set_access_groups(path.encode("utf-8"), groups)
            except IOError, ioe:
                groups_error = "%s" %ioe
        else:
            raise Exception("Unknown gallery editing action: \"%s\"" %action)
    return render("gallery.html", path = gallery.path.decode("utf-8"), route = get_route(gallery.path)[1:], galleries = galleries, files = gallery.get_files(), groups=groups, groups_error=groups_error)

@app.route('/video/<path:path>')
@render_time
def show_video(path):
    global g
    user = g.user
    if user is None and not cfg()["public_access"]:
        return render("video.html", authn_error="only logged in users may view this page")
    video_path = urllib.unquote(path).encode("utf-8")
    path = os.path.dirname(video_path)
    check_jailed_path(path, "data")
    return render("video.html", video_path = video_path, route=get_route(video_path)[1:-1], video_basename = os.path.basename(video_path))

def check_jailed_path(path, jail_path):
    if os.path.normpath(path) == jail_path:
        return
    if not os.path.normpath(path).startswith(jail_path + os.sep):
        raise Exception("Permission denied, '%s' is outside '%s'" %(path, jail_path))

@app.route('/data/<path:path>')
def show_data(path):
    global g
    user = g.user
    if user is None and not cfg()["public_access"]:
        abort(401)
    path = urllib.unquote(path).encode("utf-8")
    if os.path.basename(path) == ".access":
        abort(401)
    check_jailed_path(path, "data")
    return send_file(path)

@app.route('/static/<path:path>')
def show_static(path):
    path = os.path.join("static", urllib.unquote(path).encode("utf-8"))
    check_jailed_path(path, "static")
    return send_file(path)

if __name__ == '__main__':
    app.run(debug=cfg()["debug_mode_enabled"], host="0.0.0.0")
