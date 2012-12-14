Juque
=====

A personal jukebox server written in Python.

Quick Start
===========

    * Create a virtualenv and activate it
    * pip install -r requirements.txt
    * Edit settings.py (especially the JUQUE_ settings at the bottom)
    * manage.py syncdb (create a superuser if you want to use the admin)
    * manage.py scan <directory> (this can take a while, start small)
    * manage.py runserver
