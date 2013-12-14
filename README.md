Pyrellag
========

Description
-----------

Pyrellag is a very simple, low-overhead gallery viewer, suitable for huge collections of media.

For reference, it's able to scan from scratch a 7GB collection of photos/videos in under 2 minutes.

This software is released under the GNU AFFERO GENERAL PUBLIC LICENSE. Please see `LICENSE` file for more information.

Screenshots
-----------

Gallery view:
![alt tag](https://raw.github.com/stenyak/pyrellag/master/screenshots/gallery_view.png)

Photo view:
![alt tag](https://raw.github.com/stenyak/pyrellag/master/screenshots/photo_view.png)

Video view:
![alt tag](https://raw.github.com/stenyak/pyrellag/master/screenshots/video_view.png)

Login dialog:
![alt tag](https://raw.github.com/stenyak/pyrellag/master/screenshots/login_dialog.png)

Features
--------

 - Support for image files: jpg, jpeg, png and gif.
 - Support for video files: 3gp, mov, avi, mpeg4, mpg4, mp4 and mkv (embedded player if supported by browser).
 - Support for AuthN via openid (goog, yahoo, etc).
 - Support for AuthZ (group access permissions), or completely public gallery.
 - Use your keyboard or mouse wheel for faster browsing.
 - Designed to work straight from your existing filesystem: no need to re-arrange directories into any special structure, or "upload" stuff anywhere, or set up any stinkin database.
 - On-the-fly or off-line thumbnail generation.
 - Can follow **freedesktop.org Thumbnail Managing Standard** if desired.
 - Very light on the CPU and network.

Instructions
------------

Quick set up:
 - Create a directory named `data`, and put all your media directories there (symlink is fine too).
 - Install the required dependencies: `$ ./get_libs.sh`
 - Run the gallery server: `$ ./pyrellag.py`


Offline thumbnails generation (this is optional, only if you want to manually trigger the update of all thumbnails):
 - Run `$ ./scan_gallery.py`


ToDo
----

Some stuff I'd like to do in the future:
 - Use an animated gif with select frames for video thumbnails.

Contact
-------

You can notify me about problems and feature requests at the [issue tracker](https://github.com/stenyak/pyrellag/issues)

Feel free to hack the code and send me GitHub pull requests, or traditional patches too; I'll be more than happy to merge them.

For personal praise and negative critics, the author Bruno Gonzalez can be reached at [stenyak@stenyak.com](mailto:stenyak@stenyak.com) and `/dev/null` respectively :-D

