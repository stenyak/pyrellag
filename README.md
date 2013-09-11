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
![alt tag](https://raw.github.com/stenyak/pyrellag/master/gallery_view.png)


Photo view:
![alt tag](https://raw.github.com/stenyak/pyrellag/master/photo_view.png)

Features
--------

 - Support for image files (jpg, jpeg, png and gif).
 - Support for video files (3gp, mov, avi, mpeg4, mpg4, mp4 and mkv).
 - Use your keyboard or mouse wheel for faster browsing.
 - Designed to work straight from your existing filesystem: no need to re-arrange directories into any special structure, or "upload" stuff anywhere, or set up any stinkin database.
 - Automatic thumbnail management, following **freedesktop.org Thumbnail Managing Standard**.
 - Very light on the CPU and network.

Instructions
------------

Quick set up:
 - Create a directory named `my_gallery`, and copy/symlink all your media directories there. Any nesting level is supported (as long as your filesystem can handle it).
 - Run `./scan_gallery.py my_gallery`
 - Open your `my_gallery` directory in your web browser. You can quickly fire up a web server using `python -m SimpleHTTPServer`


Autoscan:
 - Create a cronjob that runs `./scan_gallery.py my_gallery` with the appropriate owner and permissions.


ToDo
----

Some stuff I'd like to do in the future:
 - Support for user & group access permissions.
 - Use an animated gif with select frames for video thumbnails.

Contact
-------

You can notify me about problems and feature requests at the [issue tracker](https://github.com/stenyak/pyrellag/issues)

Feel free to hack the code and send me GitHub pull requests, or traditional patches too; I'll be more than happy to merge them.

For personal praise and negative critics, the author Bruno Gonzalez can be reached at [stenyak@stenyak.com](mailto:stenyak@stenyak.com) and `/dev/null` respectively :-D

