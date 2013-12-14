Pyrellag
========

Description
-----------

Pyrellag is a very simple, fast, low-overhead **media gallery viewer**, suitable for huge collections of media.

For reference, it's able to scan from scratch a 7GB collection of photos/videos in under 2 minutes.

This software is released under the GNU AFFERO GENERAL PUBLIC LICENSE. Please see `LICENSE` file for more information.

Main features
-------------

 - View all your videos and images **from the browser**.
 - **Touch interface** friendly (tablets, cellphones) and poweruser-friendly (key shortcuts).
 - Choose between **public gallery** or **private gallery**:
   - Authentication via OpenID (Google, Yahoo, Flickr...).
   - Authorization via simple user groups, on a folder-by-folder basis.
 - Extract and run! No need to set up external databases.
 - No need to "upload", "register" or move your photos anywhere: just tell Pyrellag where in the disk your stuff is, and off you go!


Screenshots
-----------

Gallery view:
![alt tag](https://raw.github.com/stenyak/pyrellag/master/screenshots/gallery_view.png)

Photo view:
![alt tag](https://raw.github.com/stenyak/pyrellag/master/screenshots/photo_view.png)

Video view:
![alt tag](https://raw.github.com/stenyak/pyrellag/master/screenshots/video_view.png)


Instructions
------------

Quick set up:
 1. Create a directory named `data`, and put all your media directories there (symlink is fine too).
 2. Install the required dependencies: `$ ./get_libs.sh`
 3. Run the gallery server: `$ ./pyrellag.py`

Open the resulting URL in your browser. **The first user that registers will get administrator rights**.


Offline thumbnails generation (this is optional, only if you want to manually trigger the update of all thumbnails):
 - Run `$ ./scan_gallery.py`


Configuration
-------------

You can edit the configuration file (`config.json`) either directly on your filesystem, or using the "configuration" link near your username (you must be administrator for the link to show).

 - `follow_freedesktop_standard`: if `true`, absolute paths will be used when computing thumbnail paths.
 - `profile_creation_enabled`: if `false`, nobody will be able to create user profiles anymore.
 - `profile_db_path` : path to user profiles database file (sqlite3).
 - `public_access` : if `true`, anybody can view the whole gallery. If `false`, authorization is needed everywhere.

Authorization
-------------

**By default**, your Pyrellag gallery will be **publicly viewable** by anybody.

If you need privacy, you may want to limit who can view which galleries.

To this end, Pyrellag implements a **group-based authorization** system: you can define who belongs to each group, and which groups can view each directory:

 1. Log in as the administrator user (first user ever registered).
 2. Disable `public_access` in the configuration (top-right link).
 3. Create a `.access` file in each directory of your gallery, and write which groups can view the contents. E.g.: `data/vacations_2013/.access` file contents:

    family
    friends
(if no `.access` file exists, that directory won't be accessible)

 4. Then, access the profiles editor (top-right link), and fill the user groups that each profile belongs to.

That's it. Now only authorized users will be able to see stuff, always according to the groups they belong to.


ToDo
----

Some stuff I'd like to do in the future:
 - Use an animated gif with select frames for video thumbnails.

Contact
-------

You can notify me about problems and feature requests at the [issue tracker](https://github.com/stenyak/pyrellag/issues)

Feel free to hack the code and send me GitHub pull requests, or traditional patches too; I'll be more than happy to merge them.

For personal praise and negative critics, the author Bruno Gonzalez can be reached at [stenyak@stenyak.com](mailto:stenyak@stenyak.com) and `/dev/null` respectively :-D

