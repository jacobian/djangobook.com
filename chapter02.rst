==========================
Chapter 2: Getting Started
==========================

We think it's best to get a running start. The details and extent of
the Django framework will be fleshed out in the later chapters, but for now,
trust us, this chapter will be fun.

Installing Django is easy. Because Django runs anywhere Python does,
Django can be configured in many ways. We cover the common
scenarios for Django installations in this chapter. Chapter 20
covers deploying Django to production.

Installing Python
=================

Django is written in 100% pure Python code, so you'll need to install Python
on your system. Django requires Python 2.3 or higher.

If you're on Linux or Mac OS X, you probably already have Python installed.
Type ``python`` at a command prompt (or in Terminal, in OS X). If you see
something like this, then Python is installed::

    Python 2.4.1 (#2, Mar 31 2005, 00:05:10)
    [GCC 3.3 20030304 (Apple Computer, Inc. build 1666)] on darwin
    Type "help", "copyright", "credits" or "license" for more information.
    >>>
    
Otherwise, if you see an error such as ``"command not found"``, you'll have to
download and install Python. See http://www.python.org/download/ to get
started. The installation is fast and easy.

Installing Django
=================

In this section, we cover two installation options: installing an official
release and installing from Subversion.

Installing an Official Release
------------------------------

Most people will want to install the latest official release from
http://www.djangoproject.com/download/. Django uses the standard Python
``distutils`` installation method, which in Linux land looks like this:

    #. Download the tarball, which will be named something like
       ``Django-0.96.tar.gz``.
    #. ``tar xzvf Django-*.tar.gz``.
    #. ``cd Django-*``.
    #. ``sudo python setup.py install``.

On Windows, we recommend using 7-Zip to handle all manner of compressed files,
including ``.tar.gz``. You can download 7-Zip from
http://www.djangoproject.com/r/7zip/.

Change into some other directory and start ``python``. If everything worked, you
should be able to import the module ``django``:

    >>> import django
    >>> django.VERSION
    (0, 96, None)

.. note::

    The Python interactive interpreter is a command-line program that lets you
    write a Python program interactively. To start it, just run the command
    ``python`` at the command line. Throughout this book, we feature example
    Python code that's printed as if it's being entered in the interactive
    interpreter. The triple greater-than signs (``>>>``) signify a Python
    prompt.

Installing Django from Subversion
---------------------------------

If you want to work on the bleeding edge, or if you want to contribute code to
Django itself, you should install Django from its Subversion repository.

Subversion is a free, open source revision-control system similar to CVS, and
the Django team uses it to manage changes to the Django codebase. You can 
use a Subversion client to grab the very latest Django source code and, 
at any given time, you can update your local version of the Django code, 
known as your *local checkout*, to get the latest changes and
improvements made by Django developers.

The latest and greatest Django development code is referred to as the
*trunk*. The Django team runs production sites on trunk and strives to
keep it stable.

To grab the latest Django trunk, follow these steps:

    #. Make sure you have a Subversion client installed. You can get the
       software free from http://subversion.tigris.org/, and you can find
       excellent documentation at http://svnbook.red-bean.com/.

    #. Check out the trunk using the command ``svn co
       http://code.djangoproject.com/svn/django/trunk djtrunk``.

    #. Create ``site-packages/django.pth`` and add the ``djtrunk``
       directory to it, or update your ``PYTHONPATH`` to point to ``djtrunk``.

    #. Place ``djtrunk/django/bin`` on your system PATH. This directory
       includes management utilities such as ``django-admin.py``.

.. admonition:: Tip:

    If ``.pth`` files are new to you, you can learn more about them at 
    http://www.djangoproject.com/r/python/site-module/.

After downloading from Subversion and following the preceding steps, there's no
need to ``python setup.py install``--you've just done the work by hand!

Because the Django trunk changes often with bug fixes and feature additions,
you'll probably want to update it every once in a while -- or hourly, if you're
really obsessed. To update the code, just run the command ``svn update`` from
within the ``djtrunk`` directory. When you run that command, Subversion will
contact http://code.djangoproject.com, determine if any code has changed, and
update your local version of the code with any changes that have been made since
you last updated. It's quite slick.

Setting Up a Database
=====================

Django's only prerequisite is a working installation of Python. However, this
book focuses on one of Django's sweet spots, which is developing
*database-backed* Web sites, so you'll need to install a database server of some
sort, for storing your data.

If you just want to get started playing with Django, skip ahead to the "Starting
a Project" section--but trust us, you'll want to install a database eventually.
All of the examples in the book assume you have a database set up.

As of the time of this writing, Django supports three database engines:

    * PostgreSQL (http://www.postgresql.org/)
    * SQLite 3 (http://www.sqlite.org/)
    * MySQL (http://www.mysql.com/)

Work is in progress to support Microsoft SQL Server and Oracle. The Django
Web site will always have the latest information about supported databases.

We're quite fond of PostgreSQL ourselves, for reasons outside the scope of this
book, so we mention it first. However, all the engines listed here will work
equally well with Django.

SQLite deserves special notice as a development tool. It's an extremely
simple in-process database engine that doesn't require any sort of server setup
or configuration. It's by far the easiest to set up if you just want to play
around with Django, and it's even included in the standard library of Python
2.5.

On Windows, obtaining database driver binaries is sometimes an involved process.
Since you're just getting started with Django, we recommend using Python 2.5 and
its built-in support for SQLite. Compiling driver binaries is a downer.

Using Django with PostgreSQL
----------------------------

If you're using PostgreSQL, you'll need the ``psycopg`` package available from
http://www.djangoproject.com/r/python-pgsql/. Take note of whether you're using
version 1 or 2; you'll need this information later.

If you're using PostgreSQL on Windows, you can find precompiled binaries of
``psycopg`` at http://www.djangoproject.com/r/python-pgsql/windows/.

Using Django with SQLite 3
--------------------------

If you're using a Python version over 2.5, you already have SQLite. If you're
working with Python 2.4 or older, you'll need SQLite 3-- not version 2--from
http://www.djangoproject.com/r/sqlite/ and the ``pysqlite`` package from
http://www.djangoproject.com/r/python-sqlite/. Make sure you have ``pysqlite``
version 2.0.3 or higher.

On Windows, you can skip installing the separate SQLite binaries, since they're
statically linked into the ``pysqlite`` binaries.

Using Django with MySQL
-----------------------

Django requires MySQL 4.0 or above; the 3.x versions don't support nested
subqueries and some other fairly standard SQL statements. You'll also need the
``MySQLdb`` package from http://www.djangoproject.com/r/python-mysql/.

Using Django Without a Database
-------------------------------

As mentioned earlier, Django doesn't actually require a database. If you just
want to use it to serve dynamic pages that don't hit a database, that's
perfectly fine.

With that said, bear in mind that some of the extra tools bundled with Django
*do* require a database, so if you choose not to use a database, you'll miss
out on those features. (We highlight these features throughout this book.)

Starting a Project
==================

.. The below (down to "The rest of this section") is adapted from "Initial
.. setup" in tutorial01.txt.

A *project* is a collection of settings for an instance of Django, including
database configuration, Django-specific options, and application-specific
settings.

If this is your first time using Django, you'll have to take care of some
initial setup. Create a new directory to start working in, perhaps something
like ``/home/username/djcode/``, and change into that directory.

.. note::

    ``django-admin.py`` should be on your system path if you installed Django
    via its ``setup.py`` utility. If you checked out from Subversion, you can
    find it in ``djtrunk/django/bin``. Since you'll be using ``django-admin.py``
    often, consider adding it to your path. On Unix, you can do so by symlinking
    from ``/usr/local/bin``, using a command such as ``sudo ln -s
    /path/to/django/bin/django-admin.py /usr/local/bin/django-admin.py``. On
    Windows, you'll need to update your ``PATH`` environment variable.

Run the command ``django-admin.py startproject mysite`` to create a ``mysite``
directory in your current directory.

Let's look at what ``startproject`` created::

    mysite/
        __init__.py
        manage.py
        settings.py
        urls.py

These files are as follows:

    * ``__init__.py``: A file required for Python treat the directory as a
      package (i.e., a group of modules)

    * ``manage.py``: A command-line utility that lets you interact with this
      Django project in various ways

    * ``settings.py``: Settings/configuration for this Django project

    * ``urls.py``: The URL declarations for this Django project; a "table of
      contents" of your Django-powered site
 
.. admonition:: Where Should This Directory Live?

    If your background is in PHP, you're probably used to putting code under the
    Web server's document root (in a place such as ``/var/www``). With Django,
    you don't do that. It's not a good idea to put any of this Python code
    within your Web server's document root, because in doing so you risk the
    possibility that people will be able to view your code over the Web. That's
    not good for security.
    
    Put your code in some directory **outside** of the document root.

The Development Server
----------------------

Django includes a built-in, lightweight Web server you can use while developing
your site. We've included this server so you can develop your site rapidly,
without having to deal with configuring your production Web server (e.g.,
Apache) until you're ready for production. This development server watches your
code for changes and automatically reloads, helping you make many rapid changes
to your project without needing to restart anything.

Change into the ``mysite`` directory, if you haven't already, and run the
command ``python manage.py runserver``. You'll see something like this::

    Validating models...
    0 errors found.

    Django version 1.0, using settings 'mysite.settings'
    Development server is running at http://127.0.0.1:8000/
    Quit the server with CONTROL-C.

Although the development server is extremely nice for, well, development, resist
the temptation to use this server in anything resembling a production
environment. The development server can handle only a single request at a time
reliably, and it has not gone through a security audit of any sort. When the
time comes to launch your site, see Chapter 20 for information on how to deploy
Django.

.. admonition:: Changing the Host or the Port

    By default, the ``runserver`` command starts the development server on port
    8000, listening only for local connections. If you want to change the
    server's port, pass it as a command-line argument::

        python manage.py runserver 8080

    You can also change the IP address that the server listens on. This is
    especially helpful if you'd like to share a development site with other
    developers. The following::

        python manage.py runserver 0.0.0.0:8080

    will make Django listen on any network interface, thus allowing other
    computers to connect to the development server.

Now that the server's running, visit http://127.0.0.1:8000/ with your Web
browser. You'll see a "Welcome to Django" page shaded a pleasant pastel blue. It
worked!

What's Next?
============

Now that you have everything installed and the development server running, in
the `next chapter`_ you'll write some basic code that demonstrates how to serve Web
pages using Django.

.. _next chapter: ../chapter03/
