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

 - Support for jpeg images.
 - Use your keyboard or mouse wheel for faster browsing.
 - Designed to work straight from your existing filesystem: no need to re-arrange directories into any special structure, or "upload" stuff anywhere, or set up any stinkin database.
 - Automatic thumbnail generation/deletion and indices update, using provided script.
 - Very light on the CPU and network.

Instructions
------------

Quick set up:
 - Create a directory named `data`, and copy/symlink all your media directories there. Any nesting level is supported (as long as your filesystem can handle it).
 - Run `./update_thumbs.py data`
 - Open your `data` directory in your web browser. You can quickly fire up a web server using `cd data; python -m SimpleHTTPServer`


Autoscan:
 - Create a cronjob that runs `./update_thumbs.py data` with the appropriate owner and permissions.


ToDo
----

Some stuff I'd like to do in the future:
 - Support for png and gif images.
 - Support for video previews.
 - Support for user & group access permissions.

Contact
-------

You can notify me about problems and feature requests at the [issue tracker](https://github.com/stenyak/pyrellag/issues)

Feel free to hack the code and send me GitHub pull requests, or traditional patches too; I'll be more than happy to merge them.

For personal praise and negative critics, the author Bruno Gonzalez can be reached at [stenyak@stenyak.com](mailto:stenyak@stenyak.com) and `/dev/null` respectively :-D

