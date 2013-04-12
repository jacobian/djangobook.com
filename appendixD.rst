====================
Appendix D: Settings
====================

Your Django settings file contains all the configuration of your Django
installation. This appendix explains how settings work and which settings are
available.

What's a Settings File?
=======================

A *settings file* is just a Python module with module-level variables.

Here are a couple of example settings::

    DEBUG = False
    DEFAULT_FROM_EMAIL = 'webmaster@example.com'
    TEMPLATE_DIRS = ('/home/templates/mike', '/home/templates/john')

Because a settings file is a Python module, the following apply:

* It must be valid Python code; syntax errors aren't allowed.

* It can assign settings dynamically using normal Python syntax,
  for example::

      MY_SETTING = [str(i) for i in range(30)]

* It can import values from other settings files.

Default Settings
----------------

A Django settings file doesn't have to define any settings if it doesn't need
to. Each setting has a sensible default value. These defaults live in the file
``django/conf/global_settings.py``.

Here's the algorithm Django uses in compiling settings:

* Load settings from ``global_settings.py``.
* Load settings from the specified settings file, overriding the global
  settings as necessary.

Note that a settings file should *not* import from ``global_settings``, because
that's redundant.

Seeing Which Settings You've Changed
------------------------------------

There's an easy way to view which of your settings deviate from the default
settings. The command ``manage.py diffsettings`` displays differences between
the current settings file and Django's default settings.

``manage.py`` is described in more detail in Appendix F.

Using Settings in Python Code
-----------------------------

In your Django applications, use settings by importing the object
``django.conf.settings``, for example::

    from django.conf import settings

    if settings.DEBUG:
        # Do something

Note that ``django.conf.settings`` isn't a module -- it's an object. So
importing individual settings is not possible::

    from django.conf.settings import DEBUG  # This won't work.

Also note that your code should *not* import from either ``global_settings`` or
your own settings file. ``django.conf.settings`` abstracts the concepts of
default settings and site-specific settings; it presents a single interface.
It also decouples the code that uses settings from the location of your
settings.

Altering Settings at Runtime
----------------------------

You shouldn't alter settings in your applications at runtime. For example,
don't do this in a view::

    from django.conf import settings

    settings.DEBUG = True   # Don't do this!

The only place that settings should be defined in is a settings file.

Security
--------

Because a settings file contains sensitive information, such as the database
password, you should make every attempt to limit access to it. For example,
change its file permissions so that only you and your Web server's user can
read it. This is especially important in a shared-hosting environment.

Creating Your Own Settings
--------------------------

There's nothing stopping you from creating your own settings, for your own
Django applications. Just follow these conventions:

* Use all uppercase for setting names.

* For settings that are sequences, use tuples instead of lists. Settings
  should be considered immutable and shouldn't be changed once they're
  defined. Using tuples mirrors these semantics.

* Don't reinvent an already existing setting.

Designating the Settings: DJANGO_SETTINGS_MODULE
================================================

When you use Django, you have to tell it which settings you're using. Do this
by using the environment variable ``DJANGO_SETTINGS_MODULE``.

The value of ``DJANGO_SETTINGS_MODULE`` should be in Python path syntax (e.g.,
``mysite.settings``). Note that the settings module should be on the
Python import search path (``PYTHONPATH``).

.. admonition:: Tip:

    A good guide to ``PYTHONPATH`` can be found at
    http://diveintopython.org/getting_to_know_python/everything_is_an_object.html.

The django-admin.py Utility
---------------------------

When using ``django-admin.py`` (see Appendix F), you can either set the
environment variable once or explicitly pass in the settings module each time
you run the utility.

Here's an example using the Unix Bash shell::

    export DJANGO_SETTINGS_MODULE=mysite.settings
    django-admin.py runserver

Here's an example using the Windows shell::

    set DJANGO_SETTINGS_MODULE=mysite.settings
    django-admin.py runserver

Use the ``--settings`` command-line argument to specify the settings manually::

    django-admin.py runserver --settings=mysite.settings

The ``manage.py`` utility created by ``startproject`` as part of the project
skeleton sets ``DJANGO_SETTINGS_MODULE`` automatically; see Appendix F for more
about ``manage.py``.

On the Server (mod_python)
--------------------------

In your live server environment, you'll need to tell Apache/mod_python which
settings file to use. Do that with ``SetEnv``::

    <Location "/mysite/">
        SetHandler python-program
        PythonHandler django.core.handlers.modpython
        SetEnv DJANGO_SETTINGS_MODULE mysite.settings
    </Location>

For more information, read the Django mod_python documentation online at
http://docs.djangoproject.com/en/dev/howto/deployment/modpython/.

Using Settings Without Setting DJANGO_SETTINGS_MODULE
=====================================================

In some cases, you might want to bypass the ``DJANGO_SETTINGS_MODULE``
environment variable. For example, if you're using the template system by
itself, you likely don't want to have to set up an environment variable
pointing to a settings module.

In these cases, you can configure Django's settings manually. Do this by
calling ``django.conf.settings.configure()``. Here's an example::

    from django.conf import settings

    settings.configure(
        DEBUG = True,
        TEMPLATE_DEBUG = True,
        TEMPLATE_DIRS = [
            '/home/web-apps/myapp',
            '/home/web-apps/base',
        ]
    )

Pass ``configure()`` as many keyword arguments as you'd like, with each keyword
argument representing a setting and its value. Each argument name should be all
uppercase, with the same name as the settings described earlier. If a particular
setting is not passed to ``configure()`` and is needed at some later point,
Django will use the default setting value.

Configuring Django in this fashion is mostly necessary -- and, indeed,
recommended -- when you're using a piece of the framework inside a larger
application.

Consequently, when configured via ``settings.configure()``, Django will not
make any modifications to the process environment variables. (See the
explanation of ``TIME_ZONE`` later in this appendix for why this would normally occur.)
It's assumed that you're already in full control of your environment in these cases.

Custom Default Settings
-----------------------

If you'd like default values to come from somewhere other than
``django.conf.global_settings``, you can pass in a module or class that
provides the default settings as the ``default_settings`` argument (or as the
first positional argument) in the call to ``configure()``.

In this example, default settings are taken from ``myapp_defaults``, and the
``DEBUG`` setting is set to ``True``, regardless of its value in
``myapp_defaults``::

    from django.conf import settings
    from myapp import myapp_defaults

    settings.configure(default_settings=myapp_defaults, DEBUG=True)

The following example, which uses ``myapp_defaults`` as a positional argument,
is equivalent::

    settings.configure(myapp_defaults, DEBUG = True)

Normally, you will not need to override the defaults in this fashion. The
Django defaults are sufficiently tame that you can safely use them. Be aware
that if you do pass in a new default module, it entirely *replaces* the Django
defaults, so you must specify a value for every possible setting that might be
used in that code you are importing. Check in
``django.conf.settings.global_settings`` for the full list.

Either configure() or DJANGO_SETTINGS_MODULE Is Required
--------------------------------------------------------

If you're not setting the ``DJANGO_SETTINGS_MODULE`` environment variable, you
*must* call ``configure()`` at some point before using any code that reads
settings.

If you don't set ``DJANGO_SETTINGS_MODULE`` and don't call ``configure()``,
Django will raise an ``EnvironmentError`` exception the first time a setting
is accessed.

If you set ``DJANGO_SETTINGS_MODULE``, access settings values somehow, and *then*
call ``configure()``, Django will raise an ``EnvironmentError`` stating that settings
have already been configured.

Also, it's an error to call ``configure()`` more than once, or to call
``configure()`` after any setting has been accessed.

It boils down to this: use exactly one of either ``configure()`` or
``DJANGO_SETTINGS_MODULE``, and only once.

Available Settings
==================

The following sections consist of a list of the main available settings,
in alphabetical order, and their default values.

ABSOLUTE_URL_OVERRIDES
----------------------

*Default*: ``{}`` (empty dictionary)

This is a dictionary mapping ``"app_label.model_name"`` strings to functions that take
a model object and return its URL. This is a way of overriding
``get_absolute_url()`` methods on a per-installation basis. Here's an example::

    ABSOLUTE_URL_OVERRIDES = {
        'blogs.weblog': lambda o: "/blogs/%s/" % o.slug,
        'news.story': lambda o: "/stories/%s/%s/" % (o.pub_year, o.slug),
    }

Note that the model name used in this setting should be all lowercase, regardless
of the case of the actual model class name.

ADMIN_MEDIA_PREFIX
------------------

*Default*: ``'/media/'``

This setting is the URL prefix for admin media: CSS, JavaScript, and images.
Make sure to use a trailing slash.

ADMINS
------

*Default*: ``()`` (empty tuple)

This is a tuple that lists people who get code error notifications. When
``DEBUG=False`` and a view raises an exception, Django will email these people
with the full exception information. Each member of the tuple should be a tuple
of (Full name, e-mail address), for example::

    (('John', 'john@example.com'), ('Mary', 'mary@example.com'))

Note that Django will email *all* of these people whenever an error happens.

ALLOWED_INCLUDE_ROOTS
---------------------

*Default*: ``()`` (empty tuple)

This is a tuple of strings representing allowed prefixes for the ``{% ssi %}`` template
tag. This is a security measure, so that template authors can't access files
that they shouldn't be accessing.

For example, if ``ALLOWED_INCLUDE_ROOTS`` is ``('/home/html', '/var/www')``,
then ``{% ssi /home/html/foo.txt %}`` would work, but ``{% ssi /etc/passwd %}``
wouldn't.

APPEND_SLASH
------------

*Default*: ``True``

This setting indicates whether to append trailing slashes to URLs. This is used only if
``CommonMiddleware`` is installed (see Chapter 17). See also ``PREPEND_WWW``.

CACHE_BACKEND
-------------

*Default*: ``'locmem://'``

This is the cache back-end to use (see Chapter 15).

CACHE_MIDDLEWARE_KEY_PREFIX
---------------------------

*Default*: ``''`` (empty string)

This is the cache key prefix that the cache middleware should use (see Chapter 15).

DATABASE_ENGINE
---------------

*Default*: ``''`` (empty string)

This setting indicates which database back-end to use, e.g.
``'postgresql_psycopg2'``, or ``'mysql'``.

DATABASE_HOST
-------------

*Default*: ``''`` (empty string)

This setting indicates which host to use when connecting to the database.
An empty string means ``localhost``. This is not used with SQLite.

If this value starts with a forward slash (``'/'``) and you're using MySQL,
MySQL will connect via a Unix socket to the specified socket::

    DATABASE_HOST = '/var/run/mysql'

If you're using MySQL and this value *doesn't* start with a forward slash, then
this value is assumed to be the host.

DATABASE_NAME
-------------

*Default*: ``''`` (empty string)

This is the name of the database to use. For SQLite, it's the full path to the database
file.

DATABASE_OPTIONS
----------------

*Default*: ``{}`` (empty dictionary)

This is extra parameters to use when connecting to the database. Consult the back-end
module's document for available keywords.

DATABASE_PASSWORD
-----------------

*Default*: ``''`` (empty string)

This setting is the password to use when connecting to the database. It is not used with SQLite.

DATABASE_PORT
-------------

*Default*: ``''`` (empty string)

This is the port to use when connecting to the database. An empty string means the
default port. It is not used with SQLite.

DATABASE_USER
-------------

*Default*: ``''`` (empty string)

This setting is the username to use when connecting to the database. It is not used with SQLite.

DATE_FORMAT
-----------

*Default*: ``'N j, Y'`` (e.g., ``Feb. 4, 2003``)

This is the default formatting to use for date fields on Django admin change-list pages
-- and, possibly, by other parts of the system. It accepts the same format as the
``now`` tag (see Appendix E, Table E-2).

See also ``DATETIME_FORMAT``, ``TIME_FORMAT``, ``YEAR_MONTH_FORMAT``, and
``MONTH_DAY_FORMAT``.

DATETIME_FORMAT
---------------

*Default*: ``'N j, Y, P'`` (e.g., ``Feb. 4, 2003, 4 p.m.``)

This is the default formatting to use for datetime fields on Django admin change-list
pages -- and, possibly, by other parts of the system. It accepts the same format as the
``now`` tag (see Appendix E, Table E-2).

See also ``DATE_FORMAT``, ``DATETIME_FORMAT``, ``TIME_FORMAT``,
``YEAR_MONTH_FORMAT``, and ``MONTH_DAY_FORMAT``.

DEBUG
-----

*Default*: ``False``

This setting is a Boolean that turns debug mode on and off.

If you define custom settings, ``django/views/debug.py`` has a ``HIDDEN_SETTINGS``
regular expression that will hide from the ``DEBUG`` view anything that contains
``'SECRET``, ``PASSWORD``, or ``PROFANITIES'``. This allows untrusted users to
be able to give backtraces without seeing sensitive (or offensive) settings.

Still, note that there are always going to be sections of your debug output that
are inappropriate for public consumption. File paths, configuration options, and
the like all give attackers extra information about your server. Never deploy a
site with ``DEBUG`` turned on.

DEFAULT_CHARSET
---------------

*Default*: ``'utf-8'``

This is the default charset to use for all ``HttpResponse`` objects, if a MIME type isn't
manually specified. It is used with ``DEFAULT_CONTENT_TYPE`` to construct the
``Content-Type`` header. See Appendix G for more about ``HttpResponse`` objects.

DEFAULT_CONTENT_TYPE
--------------------

*Default*: ``'text/html'``

This is the default content type to use for all ``HttpResponse`` objects, if a MIME type
isn't manually specified. It is used with ``DEFAULT_CHARSET`` to construct the
``Content-Type`` header. See Appendix G for more about ``HttpResponse`` objects.

DEFAULT_FROM_EMAIL
------------------

*Default*: ``'webmaster@localhost'``

This is the default email address to use for various automated correspondence from the
site manager(s).

DISALLOWED_USER_AGENTS
----------------------

*Default*: ``()`` (empty tuple)

This is a list of compiled regular expression objects representing User-Agent strings
that are not allowed to visit any page, systemwide. Use this for bad
robots/crawlers. This is used only if ``CommonMiddleware`` is installed (see
Chapter 17).

EMAIL_HOST
----------

*Default*: ``'localhost'``

This is the host to use for sending email. See also ``EMAIL_PORT``.

EMAIL_HOST_PASSWORD
-------------------

*Default*: ``''`` (empty string)

This is the password to use for the SMTP server defined in ``EMAIL_HOST``. This setting is
used in conjunction with ``EMAIL_HOST_USER`` when authenticating to the SMTP
server. If either of these settings is empty, Django won't attempt
authentication.

See also ``EMAIL_HOST_USER``.

EMAIL_HOST_USER
---------------

*Default*: ``''`` (empty string)

This is the username to use for the SMTP server defined in ``EMAIL_HOST``. If it's empty,
Django won't attempt authentication. See also ``EMAIL_HOST_PASSWORD``.

EMAIL_PORT
----------

*Default*: ``25``

This is the port to use for the SMTP server defined in ``EMAIL_HOST``.

EMAIL_SUBJECT_PREFIX
--------------------

*Default*: ``'[Django] '``

This is the subject-line prefix for email messages sent with ``django.core.mail.mail_admins``
or ``django.core.mail.mail_managers``. You'll probably want to include the
trailing space.

FIXTURE_DIRS
-------------

*Default*: ``()`` (empty tuple)

This is a list of locations of the fixture data files, in search order. Note that these
paths should use Unix-style forward slashes, even on Windows. It is used by Django's
testing framework, which is covered online at
http://docs.djangoproject.com/en/dev/topics/testing/.

IGNORABLE_404_ENDS
------------------

*Default*: ``('mail.pl', 'mailform.pl', 'mail.cgi', 'mailform.cgi', 'favicon.ico',
'.php')``

This is a tuple of strings that specify beginnings of URLs that should be
ignored by the 404 e-mailer. (See Chapter 12 for more on the 404 e-mailer.)

No errors will be sent for URLs end with strings from this sequence.

See also ``IGNORABLE_404_STARTS`` and ``SEND_BROKEN_LINK_EMAILS``.

IGNORABLE_404_STARTS
--------------------

*Default*: ``('/cgi-bin/', '/_vti_bin', '/_vti_inf')``

See also ``SEND_BROKEN_LINK_EMAILS`` and ``IGNORABLE_404_ENDS``.

INSTALLED_APPS
--------------

*Default*: ``()`` (empty tuple)

A tuple of strings designating all applications that are enabled in this Django
installation. Each string should be a full Python path to a Python package that
contains a Django application. See Chapter 5 for more about applications.

LANGUAGE_CODE
-------------

*Default*: ``'en-us'``

This is a string representing the language code for this installation. This should be
in standard language format -- for example, U.S. English is ``"en-us"``. See
Chapter 19.

LANGUAGES
---------

*Default*: A tuple of all available languages. This list is continually growing
and any copy included here would inevitably become rapidly out of date. You can
see the current list of translated languages by looking in
``django/conf/global_settings.py``.

The list is a tuple of two-tuples in the format (language code, language name)
-- for example, ``('ja', 'Japanese')``. This specifies which languages are
available for language selection. See Chapter 19 for more on language selection.

Generally, the default value should suffice. Only set this setting if you want
to restrict language selection to a subset of the Django-provided languages.

If you define a custom ``LANGUAGES`` setting, it's OK to mark the languages as
translation strings, but you should *never* import ``django.utils.translation``
from within your settings file, because that module in itself depends on the
settings, and that would cause a circular import.

The solution is to use a "dummy" ``gettext()`` function. Here's a sample
settings file::

    gettext = lambda s: s

    LANGUAGES = (
        ('de', gettext('German')),
        ('en', gettext('English')),
    )

With this arrangement, ``make-messages.py`` will still find and mark these
strings for translation, but the translation won't happen at runtime -- so
you'll have to remember to wrap the languages in the *real* ``gettext()`` in
any code that uses ``LANGUAGES`` at runtime.

MANAGERS
--------

*Default*: ``()`` (empty tuple)

This tuple is in the same format as ``ADMINS`` that specifies who should get
broken-link notifications when ``SEND_BROKEN_LINK_EMAILS=True``.

MEDIA_ROOT
----------

*Default*: ``''`` (empty string)

This is an absolute path to the directory that holds media for this installation (e.g.,
``"/home/media/media.lawrence.com/"``). See also ``MEDIA_URL``.

MEDIA_URL
---------

*Default*: ``''`` (empty string)

This URL handles the media served from ``MEDIA_ROOT`` (e.g.,
``"http://media.lawrence.com"``).

Note that this should have a trailing slash if it has a path component:

* *Correct*: ``"http://www.example.com/static/"``
* *Incorrect*: ``"http://www.example.com/static"``

See Chapter 12 for more on deployment and serving media.

MIDDLEWARE_CLASSES
------------------

*Default*::

    ("django.contrib.sessions.middleware.SessionMiddleware",
     "django.contrib.auth.middleware.AuthenticationMiddleware",
     "django.middleware.common.CommonMiddleware",
     "django.middleware.doc.XViewMiddleware")

This is a tuple of middleware classes to use. See Chapter 17.

MONTH_DAY_FORMAT
----------------

*Default*: ``'F j'``

This is the default formatting to use for date fields on Django admin change-list
pages -- and, possibly, by other parts of the system -- in cases when only the
month and day are displayed. It accepts the same format as the
``now`` tag (see Appendix E, Table E-2).

For example, when a Django admin change-list page is being filtered by a date,
the header for a given day displays the day and month. Different locales have
different formats. For example, U.S. English would have "January 1," whereas
Spanish might have "1 Enero."

See also ``DATE_FORMAT``, ``DATETIME_FORMAT``, ``TIME_FORMAT``, and
``YEAR_MONTH_FORMAT``.

PREPEND_WWW
-----------

*Default*: ``False``

This setting indicates whether to prepend the "www." subdomain to URLs that don't have it.
This is used only if ``CommonMiddleware`` is installed (see the Chapter 17). See also
``APPEND_SLASH``.

ROOT_URLCONF
------------

*Default*: Not defined

This is a string representing the full Python import path to your root URLconf (e.g.,
``"mydjangoapps.urls"``). See Chapter 3.

SECRET_KEY
----------

*Default*: (Generated automatically when you start a project)

This is a secret key for this particular Django installation. It is used to provide a seed in
secret-key hashing algorithms. Set this to a random string -- the longer, the
better. ``django-admin.py startproject`` creates one automatically and most
of the time you won't need to change it

SEND_BROKEN_LINK_EMAILS
-----------------------

*Default*: ``False``

This setting indicates whether to send an email to the ``MANAGERS`` each time somebody visits a
Django-powered page that is 404-ed with a nonempty referer (i.e., a broken
link). This is only used if ``CommonMiddleware`` is installed (see Chapter 17).
See also ``IGNORABLE_404_STARTS`` and ``IGNORABLE_404_ENDS``.

SERIALIZATION_MODULES
---------------------

*Default*: Not defined.

Serialization is a feature still under heavy development. Refer to the online
documentation at http://docs.djangoproject.com/en/dev/topics/serialization/
for more information.

SERVER_EMAIL
------------

*Default*: ``'root@localhost'``

This is the email address that error messages come from, such as those sent to
``ADMINS`` and ``MANAGERS``.

SESSION_COOKIE_AGE
------------------

*Default*: ``1209600`` (two weeks, in seconds)

This is the age of session cookies, in seconds. See Chapter 14.

SESSION_COOKIE_DOMAIN
---------------------

*Default*: ``None``

This is the domain to use for session cookies. Set this to a string such as
``".lawrence.com"`` for cross-domain cookies, or use ``None`` for a standard
domain cookie. See Chapter 14.

SESSION_COOKIE_NAME
-------------------

*Default*: ``'sessionid'``

This is the name of the cookie to use for sessions; it can be whatever you want.
See Chapter 14.

SESSION_COOKIE_SECURE
---------------------

*Default*: ``False``

This setting indicates whether to use a secure cookie for the session cookie.
If this is set to ``True``, the cookie will be marked as "secure,"
which means browsers may ensure that the cookie is only sent under an HTTPS connection.
See Chapter 14.

SESSION_EXPIRE_AT_BROWSER_CLOSE
-------------------------------

*Default*: ``False``

This setting indicates whether to expire the session when the user closes
his browser. See Chapter 14.

SESSION_SAVE_EVERY_REQUEST
--------------------------

*Default*: ``False``

This setting indicates whether to save the session data on every request. See Chapter 14.

SITE_ID
-------

*Default*: Not defined

This is the ID, as an integer, of the current site in the ``django_site`` database
table. It is used so that application data can hook into specific site(s)
and a single database can manage content for multiple sites. See Chapter 16.

TEMPLATE_CONTEXT_PROCESSORS
---------------------------

*Default*::

    ("django.core.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media")

This is a tuple of callables that are used to populate the context in ``RequestContext``.
These callables take a request object as their argument and return a dictionary
of items to be merged into the context. See Chapter 9.

TEMPLATE_DEBUG
--------------

*Default*: ``False``

This Boolean turns template debug mode on and off. If it is ``True``, the fancy
error page will display a detailed report for any ``TemplateSyntaxError``. This
report contains the relevant snippet of the template, with the appropriate line
highlighted.

Note that Django only displays fancy error pages if ``DEBUG`` is ``True``, so
you'll want to set that to take advantage of this setting.

See also ``DEBUG``.

TEMPLATE_DIRS
-------------

*Default*: ``()`` (empty tuple)

This is a list of locations of the template source files, in search order. Note that these
paths should use Unix-style forward slashes, even on Windows. See Chapters 4 and
9.

TEMPLATE_LOADERS
----------------

*Default*::

    ('django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source')

This is a tuple of callables (as strings) that know how to import templates from
various sources. See Chapter 9.

TEMPLATE_STRING_IF_INVALID
--------------------------

*Default*: ``''`` (Empty string)

This is output, as a string, that the template system should use for invalid (e.g.,
misspelled) variables. See Chapter 9.

TEST_RUNNER
-----------

*Default*: ``'django.test.simple.run_tests'``

This is the name of the method to use for starting the test suite. It is used by Django's
testing framework, which is covered online at
http://docs.djangoproject.com/en/dev/topics/testing/.

TEST_DATABASE_NAME
------------------

*Default*: ``None``

This is the name of database to use when running the test suite. If a value of ``None``
is specified, the test database will use the name ``'test_' +
settings.DATABASE_NAME``. See the documentation for Django's testing framework,
which is covered online at http://docs.djangoproject.com/en/dev/topics/testing/.

TIME_FORMAT
-----------

*Default*: ``'P'`` (e.g., ``4 p.m.``)

This is the default formatting to use for time fields on Django admin change-list pages
-- and, possibly, by other parts of the system. It accepts the same format as the
``now`` tag (see Appendix E, Table E-2).

See also ``DATE_FORMAT``, ``DATETIME_FORMAT``, ``TIME_FORMAT``,
``YEAR_MONTH_FORMAT``, and ``MONTH_DAY_FORMAT``.

TIME_ZONE
---------

*Default*: ``'America/Chicago'``

This is a string representing the time zone for this installation. Time zones are in the
Unix-standard ``zic`` format. One relatively complete list of time zone strings
can be found at
http://www.postgresql.org/docs/8.1/static/datetime-keywords.html#DATETIME-TIMEZONE-SET-TABLE.

This is the time zone to which Django will convert all dates/times --
not necessarily the time zone of the server. For example, one server may serve
multiple Django-powered sites, each with a separate time-zone setting.

Normally, Django sets the ``os.environ['TZ']`` variable to the time zone you
specify in the ``TIME_ZONE`` setting. Thus, all your views and models will
automatically operate in the correct time zone. However, if you're using the
manually configuring settings (described above in the section titled "Using
Settings Without Setting DJANGO_SETTINGS_MODULE"), Django will *not* touch the
``TZ`` environment variable, and it will be up to you to ensure your processes
are running in the correct environment.

.. note::
    Django cannot reliably use alternate time zones in a Windows environment. If
    you're running Django on Windows, this variable must be set to match the
    system time zone.

URL_VALIDATOR_USER_AGENT
------------------------

*Default*: ``Django/<version> (http://www.djangoproject.com/)``

This is the string to use as the ``User-Agent`` header when checking to see if URLs
exist (see the ``verify_exists`` option on ``URLField``; see Appendix A).

USE_ETAGS
---------

*Default*: ``False``

This Boolean specifies whether to output the ETag header. It saves
bandwidth but slows down performance. This is only used if ``CommonMiddleware``
is installed (see Chapter 17).

USE_I18N
--------

*Default*: ``True``

This Boolean specifies whether Django's internationalization system (see
Chapter 19) should be enabled. It provides an easy way to turn off internationalization, for
performance. If this is set to ``False``, Django will make some optimizations so
as not to load the internationalization machinery.

YEAR_MONTH_FORMAT
-----------------

*Default*: ``'F Y'``

This is the default formatting to use for date fields on Django admin change-list pages
-- and, possibly, by other parts of the system -- in cases when only the year
and month are displayed. It accepts the same format as the ``now`` tag (see
Appendix E).

For example, when a Django admin change-list page is being filtered by a date
drill-down, the header for a given month displays the month and the year.
Different locales have different formats. For example, U.S. English would use
"January 2006," whereas another locale might use "2006/January."

See also ``DATE_FORMAT``, ``DATETIME_FORMAT``, ``TIME_FORMAT``, and
``MONTH_DAY_FORMAT``.