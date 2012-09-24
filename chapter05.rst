==============================================
Chapter 5: Interacting with a Database: Models
==============================================

In Chapter 3, we covered the fundamentals of building dynamic Web sites
with Django: setting up views and URLconfs. As we explained, a view is
responsible for doing *some arbitrary logic*, and then returning a response. In the
example, our arbitrary logic was to calculate the current date and time.

In modern Web applications, the arbitrary logic often involves interacting
with a database. Behind the scenes, a *database-driven Web site* connects to
a database server, retrieves some data out of it, and displays that data, nicely
formatted, on a Web page. Or, similarly, the site could provide functionality
that lets site visitors populate the database on their own.

Many complex Web sites provide some combination of the two. Amazon.com, for
instance, is a great example of a database-driven site. Each product page is
essentially a query into Amazon's product database formatted as HTML, and when
you post a customer review, it gets inserted into the database of reviews.

Django is well suited for making database-driven Web sites, as it comes
with easy yet powerful ways of performing database queries using Python. This
chapter explains that functionality: Django's database layer.

(Note: While it's not strictly necessary to know basic database theory and SQL
in order to use Django's database layer, it's highly recommended. An
introduction to those concepts is beyond the scope of this book, but keep
reading even if you're a database newbie. You'll probably be able to follow
along and grasp concepts based on the context.)

The "Dumb" Way to Do Database Queries in Views
==============================================

Just as Chapter 3 detailed a "dumb" way to produce output within a
view (by hard-coding the text directly within the view), there's a "dumb" way to
retrieve data from a database in a view. It's simple: just use any existing
Python library to execute an SQL query and do something with the results.

In this example view, we use the ``MySQLdb`` library (available at
http://www.djangoproject.com/r/python-mysql/) to connect to a MySQL database,
retrieve some records, and feed them to a template for display as a Web page::

    from django.shortcuts import render_to_response
    import MySQLdb

    def book_list(request):
        db = MySQLdb.connect(user='me', db='mydb', passwd='secret', host='localhost')
        cursor = db.cursor()
        cursor.execute('SELECT name FROM books ORDER BY name')
        names = [row[0] for row in cursor.fetchall()]
        db.close()
        return render_to_response('book_list.html', {'names': names})

This approach works, but some problems should jump out at you immediately:

    * We're hard-coding the database connection parameters. Ideally, these
      parameters would be stored in the Django configuration.

    * We're having to write a fair bit of boilerplate code: creating a
      connection, creating a cursor, executing a statement, and closing the
      connection. Ideally, all we'd have to do is specify which results we
      wanted.

    * It ties us to MySQL. If, down the road, we switch from MySQL to
      PostgreSQL, we'll have to use a different database adapter (e.g.,
      ``psycopg`` rather than ``MySQLdb``), alter the connection parameters,
      and -- depending on the nature of the SQL statement -- possibly rewrite
      the SQL. Ideally, the database server we're using would be abstracted, so
      that a database server change could be made in a single place.

As you might expect, Django's database layer aims to solve these problems.
Here's a sneak preview of how the previous view can be rewritten using Django's
database API::

    from django.shortcuts import render_to_response
    from mysite.books.models import Book

    def book_list(request):
        books = Book.objects.order_by('name')
        return render_to_response('book_list.html', {'books': books})

We'll explain this code a little later in the chapter. For now, just get a
feel for how it looks.

The MTV Development Pattern
===========================

Before we delve into any more code, let's take a moment to consider the overall
design of a database-driven Django Web application.

As we mentioned in previous chapters, Django is designed to encourage loose
coupling and strict separation between pieces of an application. If you follow
this philosophy, it's easy to make changes to one particular piece of the
application without affecting the other pieces. In view
functions, for instance, we discussed the importance of separating the business
logic from the presentation logic by using a template system. With the database
layer, we're applying that same philosophy to data access logic.

Those three pieces together -- data access logic, business logic, and presentation
logic -- comprise a concept that's sometimes called the *Model-View-Controller*
(MVC) pattern of software architecture. In this pattern, "Model" refers to the
data access layer, "View" refers to the part of the system that selects what to
display and how to display it, and "Controller" refers to the part of the
system that decides which view to use, depending on user input, accessing the
model as needed.

.. admonition:: Why the Acronym?

    The goal of explicitly defining patterns such as MVC is mostly to
    streamline communication among developers. Instead of having to tell your
    coworkers, "Let's make an abstraction of the data access, then let's have a
    separate layer that handles data display, and let's put a layer in the
    middle that regulates this," you can take advantage of a shared vocabulary
    and say, "Let's use the MVC pattern here."

Django follows this MVC pattern closely enough that it can be called an MVC
framework. Here's roughly how the M, V, and C break down in Django:

    * *M*, the data-access portion, is handled by Django's database layer,
      which is described in this chapter.

    * *V*, the portion that selects which data to display and how to display
      it, is handled by views and templates.

    * *C*, the portion that delegates to a view depending on user input, is
      handled by the framework itself by following your URLconf and calling the
      appropriate Python function for the given URL.

Because the "C" is handled by the framework itself and most of the excitement
in Django happens in models, templates, and views, Django has been referred to
as an *MTV framework*. In the MTV development pattern,

    * *M* stands for "Model," the data access layer. This layer contains
      anything and everything about the data: how to access it, how to validate
      it, which behaviors it has, and the relationships between the data. 

    * *T* stands for "Template," the presentation layer. This layer contains
      presentation-related decisions: how something should be displayed on a
      Web page or other type of document.

    * *V* stands for "View," the business logic layer. This layer contains the
      logic that access the model and defers to the appropriate template(s).
      You can think of it as the bridge between models and templates.

If you're familiar with other MVC Web-development frameworks, such as Ruby on
Rails, you may consider Django views to be the "controllers" and Django
templates to be the "views." This is an unfortunate confusion brought about by
differing interpretations of MVC. In Django's interpretation of MVC, the "view"
describes the data that gets presented to the user; it's not necessarily just
*how* the data looks, but *which* data is presented. In contrast, Ruby on Rails
and similar frameworks suggest that the controller's job includes deciding
which data gets presented to the user, whereas the view is strictly *how* the
data looks, not *which* data is presented.

Neither interpretation is more "correct" than the other. The important thing is
to understand the underlying concepts.

Configuring the Database
========================

With all of that philosophy in mind, let's start exploring Django's database
layer. First, we need to take care of some initial configuration: we need to
tell Django which database server to use and how to connect to it.

We'll assume you've set up a database server, activated it, and created a
database within it (e.g., using a ``CREATE DATABASE`` statement). SQLite is a
special case; in that case, there's no database to create, because SQLite uses
standalone files on the filesystem to store its data.

As with ``TEMPLATE_DIRS`` in the previous chapter, database configuration lives in
the Django settings file, called ``settings.py`` by default. Edit that file and
look for the database settings::

    DATABASE_ENGINE = ''
    DATABASE_NAME = ''
    DATABASE_USER = ''
    DATABASE_PASSWORD = ''
    DATABASE_HOST = ''
    DATABASE_PORT = ''

Here's a rundown of each setting.

    * ``DATABASE_ENGINE`` tells Django which database engine to use. If you're
      using a database with Django, ``DATABASE_ENGINE`` must be set to one of
      the strings shown in Table 5-1.
      
      .. table:: Table 5-1. Database Engine Settings

          =======================  ====================  ==============================================
          Setting                  Database              Required Adapter
          =======================  ====================  ==============================================
          ``postgresql``           PostgreSQL            ``psycopg`` version 1.x,
                                                         http://www.djangoproject.com/r/python-pgsql/1/.

          ``postgresql_psycopg2``  PostgreSQL            ``psycopg`` version 2.x,
                                                         http://www.djangoproject.com/r/python-pgsql/.

          ``mysql``                MySQL                 ``MySQLdb``,
                                                         http://www.djangoproject.com/r/python-mysql/.

          ``sqlite3``              SQLite                No adapter needed if using Python 2.5+.
                                                         Otherwise, ``pysqlite``,
                                                         http://www.djangoproject.com/r/python-sqlite/.

          ``ado_mssql``            Microsoft SQL Server  ``adodbapi`` version 2.0.1+,
                                                         http://www.djangoproject.com/r/python-ado/.

          ``oracle``               Oracle                ``cx_Oracle``,
                                                         http://www.djangoproject.com/r/python-oracle/.
          =======================  ====================  ==============================================

      Note that for whichever database back-end you use, you'll need to download
      and install the appropriate database adapter. Each one is available for
      free on the Web; just follow the links in the "Required Adapter" column
      in Table 5-1.

    * ``DATABASE_NAME`` tells Django the name of your database. If
      you're using SQLite, specify the full filesystem path to the database
      file on your filesystem (e.g., ``'/home/django/mydata.db'``).

    * ``DATABASE_USER`` tells Django which username to use when connecting to
      your database. If you're using SQLite, leave this blank.

    * ``DATABASE_PASSWORD`` tells Django which password to use when connecting
      to your database. If you're using SQLite or have an empty password, leave
      this blank.

    * ``DATABASE_HOST`` tells Django which host to use when connecting to your
      database. If your database is on the same computer as your Django
      installation (i.e., localhost), leave this blank. If you're using SQLite,
      leave this blank.

      MySQL is a special case here. If this value starts with a forward slash
      (``'/'``) and you're using MySQL, MySQL will connect via a Unix socket to
      the specified socket, for example::

          DATABASE_HOST = '/var/run/mysql'

      If you're using MySQL and this value *doesn't* start with a forward
      slash, then this value is assumed to be the host.

    * ``DATABASE_PORT`` tells Django which port to use when connecting to your
      database. If you're using SQLite, leave this blank. Otherwise, if you
      leave this blank, the underlying database adapter will use whichever
      port is default for your given database server. In most cases, the
      default port is fine, so you can leave this blank.

Once you've entered those settings, test your configuration. First, from within
the ``mysite`` project directory you created in Chapter 2, run the command
``python manage.py shell``.

You'll notice this starts a Python interactive interpreter. Looks can be
deceiving, though! There's an important difference between running the command
``python manage.py shell`` within your Django project directory and the more
generic ``python``. The latter is the basic Python shell, but the former tells
Django which settings file to use before it starts the shell. This is a key
requirement for doing database queries: Django needs to know which settings
file to use in order to get your database connection information.

Behind the scenes, ``python manage.py shell`` simply assumes that your settings
file is in the same directory as ``manage.py``.  There are other ways to tell
Django which settings module to use, but these subtleties will be covered later.
For now, use ``python manage.py shell`` whenever you need to drop into the 
Python interpreter to do Django-specific tinkering.

Once you've entered the shell, type these commands to test your database
configuration::

    >>> from django.db import connection
    >>> cursor = connection.cursor()

If nothing happens, then your database is configured properly. Otherwise, check
the error message for clues about what's wrong. Table 5-2 shows some common errors.

.. table:: Table 5-2. Database Configuration Error Messages

    =========================================================  ===============================================
    Error Message                                              Solution
    =========================================================  ===============================================
    You haven't set the DATABASE_ENGINE setting yet.           Set the ``DATABASE_ENGINE`` setting to
                                                               something other than an empty string.
    Environment variable DJANGO_SETTINGS_MODULE is undefined.  Run the command ``python manage.py shell``
                                                               rather than ``python``.
    Error loading _____ module: No module named _____.         You haven't installed the appropriate
                                                               database-specific adapter (e.g., ``psycopg``
                                                               or ``MySQLdb``).
    _____ isn't an available database backend.                 Set your ``DATABASE_ENGINE`` setting to
                                                               one of the valid engine settings described
                                                               previously. Perhaps you made a typo?
    database _____ does not exist                              Change the ``DATABASE_NAME`` setting to
                                                               point to a database that exists, or
                                                               execute the appropriate
                                                               ``CREATE DATABASE`` statement in order to
                                                               create it.
    role _____ does not exist                                  Change the ``DATABASE_USER`` setting to point
                                                               to a user that exists, or create the user
                                                               in your database.
    could not connect to server                                Make sure ``DATABASE_HOST`` and
                                                               ``DATABASE_PORT`` are set correctly, and
                                                               make sure the server is running.
    =========================================================  ===============================================

Your First App
==============

Now that you've verified the connection is working, it's time to create a
*Django app* -- a bundle of Django code, including models and views, that
lives together in a single Python package and represents a full Django
application.

It's worth explaining the terminology here, because this tends to trip up
beginners. We'd already created a *project*, in Chapter 2, so what's the
difference between a *project* and an *app*? The difference is that of
configuration vs. code:

    * A project is an instance of a certain set of Django apps, plus the
      configuration for those apps.

      Technically, the only requirement of a project is that it supplies a
      settings file, which defines the database connection information, the
      list of installed apps, the ``TEMPLATE_DIRS``, and so forth.

    * An app is a portable set of Django functionality, usually including
      models and views, that lives together in a single Python package.

      For example, Django comes with a number of apps, such as a commenting
      system and an automatic admin interface. A key thing to note about these
      apps is that they're portable and reusable across multiple projects.

There are very few hard-and-fast rules about how you fit your Django code into
this scheme; it's flexible. If you're building a simple Web site, you may 
use only a single app. If you're building a complex Web site with several unrelated
pieces such as an e-commerce system and a message board, you'll probably want
to split those into separate apps so that you'll be able to reuse them
individually in the future.

Indeed, you don't necessarily need to create apps at all, as evidenced by the
example view functions we've created so far in this book. In those cases, we
simply created a file called ``views.py``, filled it with view functions, and
pointed our URLconf at those functions. No "apps" were needed.

However, there's one requirement regarding the app convention: if you're using
Django's database layer (models), you must create a Django app. Models must
live within apps. Thus, in order to start writing our models, we'll need to
create a new app.

Within the ``mysite`` project directory you created in Chapter 2, type this
command to create a new app named books::

    python manage.py startapp books

This command does not produce any output, but it does create a
``books`` directory within the ``mysite`` directory. Let's look at the contents
of that directory::

    books/
        __init__.py
        models.py
        views.py

These files will contain the models and views for this app.

Have a look at ``models.py`` and ``views.py`` in your favorite text editor.
Both files are empty, except for an import in ``models.py``. This is the blank
slate for your Django app.

Defining Models in Python
=========================

As we discussed earlier in this chapter, the "M" in "MTV" stands for "Model." A Django model is a
description of the data in your database, represented as Python code. It's your
data layout -- the equivalent of your SQL ``CREATE TABLE`` statements -- except
it's in Python instead of SQL, and it includes more than just database column
definitions. Django uses a model to execute SQL code behind the scenes and
return convenient Python data structures representing the rows in your database
tables. Django also uses models to represent higher-level concepts that SQL
can't necessarily handle.

If you're familiar with databases, your immediate thought might be, "Isn't it
redundant to define data models in Python *and* in SQL?" Django works the way
it does for several reasons:

    * Introspection requires overhead and is imperfect. In order to provide 
      convenient data-access APIs, Django needs to know the
      database layout *somehow*, and there are two ways of accomplishing this.
      The first way would be to explicitly describe the data in Python, and the
      second way would be to introspect the database at runtime to determine
      the data models.

      This second way seems cleaner, because the metadata about your tables
      lives in only one place, but it introduces a few problems. First,
      introspecting a database at runtime obviously requires overhead. If the
      framework had to introspect the database each time it processed a
      request, or even when the Web server was initialized, this would incur an
      unacceptable level of overhead. (While some believe that level of
      overhead is acceptable, Django's developers aim to trim as much framework
      overhead as possible, and this approach has succeeded in making Django
      faster than its high-level framework competitors in benchmarks.) Second,
      some databases, notably older versions of MySQL, do not store sufficient
      metadata for accurate and complete introspection.

    * Writing Python is fun, and keeping everything in Python limits the number
      of times your brain has to do a "context switch." It helps productivity
      if you keep yourself in a single programming environment/mentality for as
      long as possible. Having to write SQL, then Python, and then SQL again is
      disruptive.

    * Having data models stored as code rather than in your database makes it
      easier to keep your models under version control. This way, you can
      easily keep track of changes to your data layouts.

    * SQL allows for only a certain level of metadata about a data layout. Most
      database systems, for example, do not provide a specialized data type for
      representing email addresses or URLs. Django models do. The advantage of
      higher-level data types is higher productivity and more reusable code.

    * SQL is inconsistent across database platforms. If you're distributing a
      Web application, for example, it's much more pragmatic to distribute a
      Python module that describes your data layout than separate sets of
      ``CREATE TABLE`` statements for MySQL, PostgreSQL, and SQLite.

A drawback of this approach, however, is that it's possible for the Python code
to get out of sync with what's actually in the database. If you make changes to
a Django model, you'll need to make the same changes inside your database to
keep your database consistent with the model. We'll detail some strategies for
handling this problem later in this chapter.

Finally, we should note that Django includes a utility that can generate models
by introspecting an existing database. This is useful for quickly getting up
and running with legacy data.

Your First Model
================

As an ongoing example in this chapter and the next chapter, we'll focus on a
basic book/author/publisher data layout. We use this as our example because the
conceptual relationships between books, authors, and publishers are well known,
and this is a common data layout used in introductory SQL textbooks. You're
also reading a book that was written by authors and produced by a publisher!

We'll suppose the following concepts, fields, and relationships:

    * An author has a salutation (e.g., Mr. or Mrs.), a first name, a last
      name, an email address, and a headshot photo.

    * A publisher has a name, a street address, a city, a state/province, a
      country, and a Web site.

    * A book has a title and a publication date. It also has one or more
      authors (a many-to-many relationship with authors) and a single publisher
      (a one-to-many relationship -- aka foreign key -- to publishers).

The first step in using this database layout with Django is to express it as
Python code. In the ``models.py`` file that was created by the ``startapp``
command, enter the following::

    from django.db import models

    class Publisher(models.Model):
        name = models.CharField(maxlength=30)
        address = models.CharField(maxlength=50)
        city = models.CharField(maxlength=60)
        state_province = models.CharField(maxlength=30)
        country = models.CharField(maxlength=50)
        website = models.URLField()

    class Author(models.Model):
        salutation = models.CharField(maxlength=10)
        first_name = models.CharField(maxlength=30)
        last_name = models.CharField(maxlength=40)
        email = models.EmailField()
        headshot = models.ImageField(upload_to='/tmp')

    class Book(models.Model):
        title = models.CharField(maxlength=100)
        authors = models.ManyToManyField(Author)
        publisher = models.ForeignKey(Publisher)
        publication_date = models.DateField()

Let's quickly examine this code to cover the basics. The first thing to notice
is that each model is represented by a Python class that is a subclass of
``django.db.models.Model``. The parent class, ``Model``, contains all the
machinery necessary to make these objects capable of interacting with a
database -- and that leaves our models responsible solely for defining their
fields, in a nice and compact syntax. Believe it or not, this is all the code
we need to write to have basic data access with Django.

Each model generally corresponds to a single database table, and each attribute
on a model generally corresponds to a column in that database table. The
attribute name corresponds to the column's name, and the type of field (e.g.,
``CharField``) corresponds to the database column type (e.g., ``varchar``). For
example, the ``Publisher`` model is equivalent to the following table (assuming
PostgreSQL ``CREATE TABLE`` syntax)::

    CREATE TABLE "books_publisher" (
        "id" serial NOT NULL PRIMARY KEY,
        "name" varchar(30) NOT NULL,
        "address" varchar(50) NOT NULL,
        "city" varchar(60) NOT NULL,
        "state_province" varchar(30) NOT NULL,
        "country" varchar(50) NOT NULL,
        "website" varchar(200) NOT NULL
    );

Indeed, Django can generate that ``CREATE TABLE`` statement automatically, as
we'll show in a moment.

The exception to the one-class-per-database-table rule is the case of
many-to-many relationships. In our example models, ``Book`` has a
``ManyToManyField`` called ``authors``. This designates that a book has one or
many authors, but the ``Book`` database table doesn't get an ``authors``
column. Rather, Django creates an additional table -- a many-to-many "join
table" -- that handles the mapping of books to authors.

For a full list of field types and model syntax options, see Appendix B.

Finally, note we haven't explicitly defined a primary key in any of these
models. Unless you instruct it otherwise, Django automatically gives every
model an integer primary key field called ``id``. Each Django model is required
to have a single-column primary key.

Installing the Model
====================

We've written the code; now let's create the tables in our database. In order
to do that, the first step is to *activate* these models in our Django project.
We do that by adding the ``books`` app to the list of installed apps in the
settings file.

Edit the ``settings.py`` file again, and look for the ``INSTALLED_APPS``
setting. ``INSTALLED_APPS`` tells Django which apps are activated for a given
project. By default, it looks something like this::

    INSTALLED_APPS = (
        'django.contrib.auth',
        'django.contrib.contenttypes',
        'django.contrib.sessions',
        'django.contrib.sites',
    )

Temporarily comment out all four of those strings by putting a hash character
(``#``) in front of them. (They're included by default as a common-case
convenience, but we'll activate and discuss them later.) 
While you're at it, modify the default ``MIDDLEWARE_CLASSES`` and 
``TEMPLATE_CONTEXT_PROCESSORS`` settings.  These depend on some of the apps we 
just commented out.  Then, add  ``'mysite.books'`` to the ``INSTALLED_APPS`` 
list, so the setting ends up looking like this::

    MIDDLEWARE_CLASSES = (
    #    'django.middleware.common.CommonMiddleware',
    #    'django.contrib.sessions.middleware.SessionMiddleware',
    #    'django.contrib.auth.middleware.AuthenticationMiddleware',
    #    'django.middleware.doc.XViewMiddleware',
    )
    
    TEMPLATE_CONTEXT_PROCESSORS = ()
    #...
    
    INSTALLED_APPS = (
        #'django.contrib.auth',
        #'django.contrib.contenttypes',
        #'django.contrib.sessions',
        #'django.contrib.sites',
        'mysite.books',
    )

(As we're dealing with a single-element tuple here, don't forget the trailing
comma. By the way, this book's authors prefer to put a comma after *every*
element of a tuple, regardless of whether the tuple has only a single element.
This avoids the issue of forgetting commas, and there's no penalty for using
that extra comma.)
    
``'mysite.books'`` refers to the ``books`` app we're working on. Each app in
``INSTALLED_APPS`` is represented by its full Python path -- that is, the path
of packages, separated by dots, leading to the app package.

Now that the Django app has been activated in the settings file, we can create
the database tables in our database. First, let's validate the models by
running this command::

    python manage.py validate

The ``validate`` command checks whether your models' syntax and logic are
correct. If all is well, you'll see the message ``0 errors found``. If you
don't, make sure you typed in the model code correctly. The error output should
give you helpful information about what was wrong with the code.

Any time you think you have problems with your models, run
``python manage.py validate``. It tends to catch all the common model problems.

If your models are valid, run the following command for Django to generate
``CREATE TABLE`` statements for your models in the ``books`` app (with colorful
syntax highlighting available if you're using Unix)::

    python manage.py sqlall books

In this command, ``books`` is the name of the app. It's what you specified when
you ran the command ``manage.py startapp``. When you run the command, you
should see something like this::

    BEGIN;
    CREATE TABLE "books_publisher" (
        "id" serial NOT NULL PRIMARY KEY,
        "name" varchar(30) NOT NULL,
        "address" varchar(50) NOT NULL,
        "city" varchar(60) NOT NULL,
        "state_province" varchar(30) NOT NULL,
        "country" varchar(50) NOT NULL,
        "website" varchar(200) NOT NULL
    );
    CREATE TABLE "books_book" (
        "id" serial NOT NULL PRIMARY KEY,
        "title" varchar(100) NOT NULL,
        "publisher_id" integer NOT NULL REFERENCES "books_publisher" ("id"),
        "publication_date" date NOT NULL
    );
    CREATE TABLE "books_author" (
        "id" serial NOT NULL PRIMARY KEY,
        "salutation" varchar(10) NOT NULL,
        "first_name" varchar(30) NOT NULL,
        "last_name" varchar(40) NOT NULL,
        "email" varchar(75) NOT NULL,
        "headshot" varchar(100) NOT NULL
    );
    CREATE TABLE "books_book_authors" (
        "id" serial NOT NULL PRIMARY KEY,
        "book_id" integer NOT NULL REFERENCES "books_book" ("id"),
        "author_id" integer NOT NULL REFERENCES "books_author" ("id"),
        UNIQUE ("book_id", "author_id")
    );
    CREATE INDEX books_book_publisher_id ON "books_book" ("publisher_id");
    COMMIT;

Note the following:

    * Table names are automatically generated by combining the name of the app
      (``books``) and the lowercase name of the model (``publisher``,
      ``book``, and ``author``). You can override this behavior, as detailed 
      in Appendix B.

    * As we mentioned earlier, Django adds a primary key for each table
      automatically -- the ``id`` fields. You can override this, too.

    * By convention, Django appends ``"_id"`` to the foreign key field name. As
      you might have guessed, you can override this behavior, too.

    * The foreign key relationship is made explicit by a ``REFERENCES``
      statement.

    * These ``CREATE TABLE`` statements are tailored to the database you're
      using, so database-specific field types such as ``auto_increment``
      (MySQL), ``serial`` (PostgreSQL), or ``integer primary key`` (SQLite) are
      handled for you automatically. The same goes for quoting of column names
      (e.g., using double quotes or single quotes). This example output is in
      PostgreSQL syntax.

The ``sqlall`` command doesn't actually create the tables or otherwise touch
your database -- it just prints output to the screen so you can see what SQL
Django would execute if you asked it. If you wanted to, you could copy and
paste this SQL into your database client, or use Unix pipes to pass it
directly. However, Django provides an easier way of committing the SQL to the
database. Run the ``syncdb`` command, like so::

    python manage.py syncdb

You'll see something like this::

    Creating table books_publisher
    Creating table books_book
    Creating table books_author
    Installing index for books.Book model

The ``syncdb`` command is a simple "sync" of your models to your database. It
looks at all of the models in each app in your ``INSTALLED_APPS`` setting,
checks the database to see whether the appropriate tables exist yet, and
creates the tables if they don't yet exist. Note that ``syncdb`` does *not*
sync changes in models or deletions of models; if you make a change to a model
or delete a model, and you want to update the database, ``syncdb`` will not
handle that. (More on this later.)

If you run ``python manage.py syncdb`` again, nothing happens, because you
haven't added any models to the ``books`` app or added any apps to
``INSTALLED_APPS``. Ergo, it's always safe to run ``python manage.py syncdb``
-- it won't clobber things.

If you're interested, take a moment to dive into your database server's
command-line client and see the database tables Django created. You can
manually run the command-line client (e.g., ``psql`` for PostgreSQL) or
you can run the command ``python manage.py dbshell``, which will figure out
which command-line client to run, depending on your ``DATABASE_SERVER``
setting. The latter is almost always more convenient.

Basic Data Access
=================

Once you've created a model, Django automatically provides a high-level Python
API for working with those models. Try it out by running
``python manage.py shell`` and typing the following::

    >>> from books.models import Publisher
    >>> p1 = Publisher(name='Addison-Wesley', address='75 Arlington Street',
    ...     city='Boston', state_province='MA', country='U.S.A.',
    ...     website='http://www.apress.com/')
    >>> p1.save()
    >>> p2 = Publisher(name="O'Reilly", address='10 Fawcett St.',
    ...     city='Cambridge', state_province='MA', country='U.S.A.',
    ...     website='http://www.oreilly.com/')
    >>> p2.save()
    >>> publisher_list = Publisher.objects.all()
    >>> publisher_list
    [<Publisher: Publisher object>, <Publisher: Publisher object>]

These few lines of code accomplish quite a bit. Here are the highlights:

    * To create an object, just import the appropriate model class and
      instantiate it by passing in values for each field.

    * To save the object to the database, call the ``save()`` method on the
      object. Behind the scenes, Django executes an SQL ``INSERT`` statement
      here.

    * To retrieve objects from the database, use the attribute
      ``Publisher.objects``. Fetch a list of all ``Publisher`` objects in the
      database with the statement ``Publisher.objects.all()``. Behind the
      scenes, Django executes an SQL ``SELECT`` statement here.

Naturally, you can do quite a lot with the Django database API -- but first,
let's take care of a small annoyance.

Adding Model String Representations
===================================

When we printed out the list of publishers, all we got was this
unhelpful display that makes it difficult to tell the ``Publisher`` objects
apart::

    [<Publisher: Publisher object>, <Publisher: Publisher object>]

We can fix this easily by adding a method called ``__str__()`` to our
``Publisher`` object. A ``__str__()`` method tells Python how to display the
"string" representation of an object. You can see this in action by adding a
``__str__()`` method to the three models:

.. parsed-literal::

    from django.db import models
    
    class Publisher(models.Model):
        name = models.CharField(maxlength=30)
        address = models.CharField(maxlength=50)
        city = models.CharField(maxlength=60)
        state_province = models.CharField(maxlength=30)
        country = models.CharField(maxlength=50)
        website = models.URLField()

        **def __str__(self):**
            **return self.name**

    class Author(models.Model):
        salutation = models.CharField(maxlength=10)
        first_name = models.CharField(maxlength=30)
        last_name = models.CharField(maxlength=40)
        email = models.EmailField()
        headshot = models.ImageField(upload_to='/tmp')

        **def __str__(self):**
            **return '%s %s' % (self.first_name, self.last_name)**

    class Book(models.Model):
        title = models.CharField(maxlength=100)
        authors = models.ManyToManyField(Author)
        publisher = models.ForeignKey(Publisher)
        publication_date = models.DateField()

        **def __str__(self):**
            **return self.title**

As you can see, a ``__str__()`` method can do whatever it needs to do in order
to return a string representation. Here, the ``__str__()`` methods for
``Publisher`` and ``Book`` simply return the object's name and title,
respectively, but the ``__str__()`` for ``Author`` is slightly more complex --
it pieces together the ``first_name`` and ``last_name`` fields. The only
requirement for ``__str__()`` is that it return a string. If ``__str__()``
doesn't return a string -- if it returns, say, an integer -- then Python will
raise a ``TypeError`` with a message like ``"__str__ returned non-string"``.

For the changes to take effect, exit out of the Python shell and enter it again
with ``python manage.py shell``. (This is the simplest way to make code changes
take effect.) Now the list of ``Publisher`` objects is much easier to
understand::

    >>> from books.models import Publisher
    >>> publisher_list = Publisher.objects.all()
    >>> publisher_list
    [<Publisher: Addison-Wesley>, <Publisher: O'Reilly>]

Make sure any model you define has a ``__str__()`` method -- not only for your
own convenience when using the interactive interpreter, but also because Django
uses the output of ``__str__()`` in several places when it needs to display
objects.

Finally, note that ``__str__()`` is a good example of adding *behavior* to
models. A Django model describes more than the database table layout for an
object; it also describes any functionality that object knows how to do.
``__str__()`` is one example of such functionality -- a model knows how to
display itself.

Inserting and Updating Data
===========================

You've already seen this done: to insert a row into your database, first create
an instance of your model using keyword arguments, like so::

    >>> p = Publisher(name='Apress',
    ...         address='2855 Telegraph Ave.',
    ...         city='Berkeley',
    ...         state_province='CA',
    ...         country='U.S.A.',
    ...         website='http://www.apress.com/')

This act of instantiating a model class does *not* touch the database.

To save the record into the database (i.e., to perform the SQL ``INSERT``
statement), call the object's ``save()`` method::

    >>> p.save()

In SQL, this can roughly be translated into the following::

    INSERT INTO book_publisher
        (name, address, city, state_province, country, website)
    VALUES
        ('Apress', '2855 Telegraph Ave.', 'Berkeley', 'CA',
         'U.S.A.', 'http://www.apress.com/');

Because the ``Publisher`` model uses an autoincrementing primary key ``id``,
the initial call to ``save()`` does one more thing: it calculates the primary
key value for the record and sets it to the ``id`` attribute on the instance::

    >>> p.id
    52    # this will differ based on your own data

Subsequent calls to ``save()`` will save the record in place, without creating
a new record (i.e., performing an SQL ``UPDATE`` statement instead of an
``INSERT``)::

    >>> p.name = 'Apress Publishing'
    >>> p.save()

The preceding ``save()`` statement will result in roughly the following SQL::

    UPDATE book_publisher SET
        name = 'Apress Publishing',
        address = '2855 Telegraph Ave.',
        city = 'Berkeley',
        state_province = 'CA',
        country = 'U.S.A.',
        website = 'http://www.apress.com'
    WHERE id = 52;

Selecting Objects
=================

Creating and updating data sure is fun, but it is also useless without a way to
sift through that data. We've already seen a way to look up all the data
for a certain model::

    >>> Publisher.objects.all()
    [<Publisher: Addison-Wesley>, <Publisher: O'Reilly>, <Publisher: Apress Publishing>]

This roughly translates to this SQL::

    SELECT 
        id, name, address, city, state_province, country, website 
    FROM book_publisher;
    
.. note::

    Notice that Django doesn't use ``SELECT *`` when looking up data and instead
    lists all fields explicitly. This is by design: in certain circumstances
    ``SELECT *`` can be slower, and (more important) listing fields more closely
    follows one tenet of the Zen of Python: "Explicit is better than implicit."
    
    For more on the Zen of Python, try typing ``import this`` at a Python
    prompt.

Let's take a close look at each part of this ``Publisher.objects.all()`` line:

    * First, we have the model we defined, ``Publisher``. No surprise here: when
      you want to look up data, you use the model for that data.
      
    * Next, we have this ``objects`` business. Technically, this is a
      *manager*. Managers are discussed in detail in Appendix B. For now, all
      you need to know is that managers take care of all "table-level"
      operations on data including, most important, data lookup.
      
      All models automatically get a ``objects`` manager; you'll use it
      any time you want to look up model instances.
      
    * Finally, we have ``all()``. This is a method on the ``objects`` manager
      that returns all the rows in the database. Though this object *looks*
      like a list, it's actually a *QuerySet* -- an object that represents some
      set of rows from the database. Appendix C deals with QuerySets in detail.
      For the rest of this chapter, we'll just treat them like the lists they
      emulate.

Any database lookup is going to follow this general pattern -- we'll call methods on
the manager attached to the model we want to query against.

Filtering Data
--------------

While fetching all objects certainly has its uses, most of the time we're going
to want to deal with a subset of the data. We'll do this with the ``filter()``
method::

    >>> Publisher.objects.filter(name="Apress Publishing")
    [<Publisher: Apress Publishing>]
    
``filter()`` takes keyword arguments that get translated into the appropriate
SQL ``WHERE`` clauses. The preceding example would get translated into something like this::

    SELECT 
        id, name, address, city, state_province, country, website 
    FROM book_publisher
    WHERE name = 'Apress Publishing';
    
You can pass multiple arguments into ``filter()`` to narrow down things further::

    >>> Publisher.objects.filter(country="U.S.A.", state_province="CA")
    [<Publisher: Apress Publishing>]
    
Those multiple arguments get translated into SQL ``AND`` clauses. Thus, the example
in the code snippet translates into the following::

    SELECT 
        id, name, address, city, state_province, country, website 
    FROM book_publisher
    WHERE country = 'U.S.A.' AND state_province = 'CA';

Notice that by default the lookups use the SQL ``=`` operator to do exact match
lookups. Other lookup types are available::

    >>> Publisher.objects.filter(name__contains="press")
    [<Publisher: Apress Publishing>]
    
That's a double underscore there between ``name`` and ``contains``. Like Python itself,
Django uses the double underscore to signal that something "magic" is happening -- here,
the ``__contains`` part gets translated by Django into a SQL ``LIKE`` statement::

    SELECT 
        id, name, address, city, state_province, country, website 
    FROM book_publisher
    WHERE name LIKE '%press%';
    
Many other types of lookups are available, including ``icontains``
(case-insensitive ``LIKE``), ``startswith`` and ``endswith``, and ``range`` (SQL
``BETWEEN`` queries). Appendix C describes all of these lookup types in detail.

Retrieving Single Objects
-------------------------

Sometimes you want to fetch only a single object. That's what the ``get()`` method is for::

    >>> Publisher.objects.get(name="Apress Publishing")
    <Publisher: Apress Publishing>
    
Instead of a list (rather, QuerySet), only a single object is returned. Because of
that, a query resulting in multiple objects will cause an exception::

    >>> Publisher.objects.get(country="U.S.A.")
    Traceback (most recent call last):
        ...
    AssertionError: get() returned more than one Publisher -- it returned 2!

A query that returns no objects also causes an exception::

    >>> Publisher.objects.get(name="Penguin")
    Traceback (most recent call last):
        ...
    DoesNotExist: Publisher matching query does not exist.

Ordering Data
-------------

As you play around with the previous examples, you might discover that the objects
are being returned in a seemingly random order. You aren't imagining things; so
far we haven't told the database how to order its results, so we're simply
getting back data in some arbitrary order chosen by the database.

That's obviously a bit silly; we wouldn't want a Web page listing publishers to
be ordered randomly. So, in practice, we'll probably want to use ``order_by()``
to reorder our data into a useful list::

    >>> Publisher.objects.order_by("name")
    [<Publisher: Apress Publishing>, <Publisher: Addison-Wesley>, <Publisher: O'Reilly>]
    
This doesn't look much different from the earlier ``all()`` example, but the SQL
now includes a specific ordering::

    SELECT 
        id, name, address, city, state_province, country, website 
    FROM book_publisher
    ORDER BY name;
    
We can order by any field we like::

    >>> Publisher.objects.order_by("address")
    [<Publisher: O'Reilly>, <Publisher: Apress Publishing>, <Publisher: Addison-Wesley>]

    >>> Publisher.objects.order_by("state_province")
    [<Publisher: Apress Publishing>, <Publisher: Addison-Wesley>, <Publisher: O'Reilly>]

and by multiple fields::

    >>> Publisher.objects.order_by("state_provice", "address")
     [<Publisher: Apress Publishing>, <Publisher: O'Reilly>, <Publisher: Addison-Wesley>]
     
We can also specify reverse ordering by prefixing the field name with a ``-``
(that's a minus character)::

    >>> Publisher.objects.order_by("-name")
    [<Publisher: O'Reilly>, <Publisher: Apress Publishing>, <Publisher: Addison-Wesley>]
    
While this flexibility is useful, using ``order_by()`` all the time can be quite 
repetitive. Most of the time you'll have a particular field you usually want
to order by. In these cases, Django lets you attach a default ordering to the model:

.. parsed-literal::

    class Publisher(models.Model):
        name = models.CharField(maxlength=30)
        address = models.CharField(maxlength=50)
        city = models.CharField(maxlength=60)
        state_province = models.CharField(maxlength=30)
        country = models.CharField(maxlength=50)
        website = models.URLField()
        
        def __str__(self):
            return self.name
    
        **class Meta:**
            **ordering = ["name"]**
            
This ``ordering = ["name"]`` bit tells Django that unless an ordering is given
explicitly with ``order_by()``, all publishers should be ordered by name.

.. admonition:: What's This Meta Thing?

    Django uses this internal ``class Meta`` as a place to specify additional
    metadata about a model. It's completely optional, but it can do some very
    useful things. See Appendix B for the options you can put under ``Meta``.

Chaining Lookups
----------------

You've seen how you can filter data, and you've seen how you can order it. At times, of course, 
you're going to want to do both. In these cases, you simply "chain" the lookups together::

    >>> Publisher.objects.filter(country="U.S.A.").order_by("-name")
    [<Publisher: O'Reilly>, <Publisher: Apress Publishing>, <Publisher: Addison-Wesley>]
    
As you might expect, this translates to a SQL query with both a ``WHERE`` and an
``ORDER BY``::

    SELECT 
        id, name, address, city, state_province, country, website 
    FROM book_publisher
    WHERE country = 'U.S.A'
    ORDER BY name DESC;

You can keep chaining queries as long as you like. There's no limit. 
    
Slicing Data
------------

Another common need is to look up only a fixed number of rows. Imagine you have thousands
of publishers in your database, but you want to display only the first one. You can do this
using Python's standard list slicing syntax::

    >>> Publisher.objects.all()[0]
    <Publisher: Addison-Wesley>
    
This translates roughly to::

    SELECT 
        id, name, address, city, state_province, country, website 
    FROM book_publisher
    ORDER BY name
    LIMIT 1;


.. admonition:: And More...

    We've only just scratched the surface of dealing with models, but you should
    now know enough to understand all the examples in the rest of the book. When
    you're ready to learn the complete details behind object lookups, turn to
    Appendix C.

Deleting Objects
================

To delete objects, simply call the ``delete()`` method on your object::

    >>> p = Publisher.objects.get(name="Addison-Wesley")
    >>> p.delete()
    >>> Publisher.objects.all()
    [<Publisher: Apress Publishing>, <Publisher: O'Reilly>]
    
You can also delete objects in bulk by calling ``delete()`` on the result of
some lookup::

    >>> publishers = Publisher.objects.all()
    >>> publishers.delete()
    >>> Publisher.objects.all()
    []

.. note::

    Deletions are *permanent*, so be careful! In fact, it's usually a 
    good idea to avoid deleting objects unless you
    absolutely have to -- relational databases don't do "undo" so well,
    and restoring from backups is painful.
    
    It's often a good idea to add "active" flags to your data models. You can
    look up only "active" objects, and simply set the active field to ``False``
    instead of deleting the object. Then, if you realize you've made a mistake,
    you can simply flip the flag back.

Making Changes to a Database Schema
===================================

When we introduced the ``syncdb`` command earlier in this chapter, we noted
that ``syncdb`` merely creates tables that don't yet exist in your database --
it does *not* sync changes in models or perform deletions of models. If you
add or change a model's field, or if you delete a model, you'll need to make
the change in your database manually. This section explains how to do that.

When dealing with schema changes, it's important to keep a few things in mind
about how Django's database layer works:

    * Django will complain loudly if a model contains a field that has not yet
      been created in the database table. This will cause an error the first
      time you use the Django database API to query the given table (i.e., it
      will happen at code execution time, not at compilation time).

    * Django does *not* care if a database table contains columns that are not
      defined in the model.

    * Django does *not* care if a database contains a table that is not
      represented by a model.

Making schema changes is a matter of changing the various pieces -- the Python
code and the database itself -- in the right order.

Adding Fields
-------------

When adding a field to a table/model in a production setting, the trick is to
take advantage of the fact that Django doesn't care if a table contains columns
that aren't defined in the model. The strategy is to add the column in the
database, and then update the Django model to include the new field.

However, there's a bit of a chicken-and-egg problem here, because in order to
know how the new database column should be expressed in SQL, you need to look
at the output of Django's ``manage.py sqlall`` command, which requires that the
field exist in the model. (Note that you're not *required* to create your
column with exactly the same SQL that Django would, but it's a good idea to do
so, just to be sure everything's in sync.)

The solution to the chicken-and-egg problem is to use a development environment
instead of making the changes on a production server. (You *are* using a
testing/development environment, right?) Here are the detailed steps to take.

First, take these steps in the development environment (i.e., not on the production server):

    1. Add the field to your model.

    2. Run ``manage.py sqlall [yourapp]`` to see the new ``CREATE TABLE``
       statement for the model. Note the column definition for the new field.

    3. Start your database's interactive shell (e.g., ``psql`` or ``mysql``, or
       you can use ``manage.py dbshell``). Execute an ``ALTER TABLE`` statement
       that adds your new column.

    4. (Optional.) Launch the Python interactive shell with ``manage.py shell``
       and verify that the new field was added properly by importing the model
       and selecting from the table (e.g., ``MyModel.objects.all()[:5]``).

Then on the production server perform these steps:

    1. Start your database's interactive shell.
    
    2. Execute the ``ALTER TABLE`` statement you used in step 3 of the
       development environment steps.

    3. Add the field to your model. If you're using source-code revision
       control and you checked in your change in development environment step
       1, now is the time to update the code (e.g., ``svn update``, with
       Subversion) on the production server.

    4. Restart the Web server for the code changes to take effect.

For example, let's walk through what we'd do if we added a ``num_pages`` field
to the ``Book`` model described earlier in this chapter. First, we'd alter the
model in our development environment to look like this:

.. parsed-literal::

    class Book(models.Model):
        title = models.CharField(maxlength=100)
        authors = models.ManyToManyField(Author)
        publisher = models.ForeignKey(Publisher)
        publication_date = models.DateField()
        **num_pages = models.IntegerField(blank=True, null=True)**

        def __str__(self):
            return self.title

(Note: Read the "Adding NOT NULL Columns" sidebar for important details
on why we included ``blank=True`` and ``null=True``.)

Then we'd run the command ``manage.py sqlall books`` to see the
``CREATE TABLE`` statement. It would look something like this::

    CREATE TABLE "books_book" (
        "id" serial NOT NULL PRIMARY KEY,
        "title" varchar(100) NOT NULL,
        "publisher_id" integer NOT NULL REFERENCES "books_publisher" ("id"),
        "publication_date" date NOT NULL,
        "num_pages" integer NULL
    );

The new column is represented like this::

    "num_pages" integer NULL

Next, we'd start the database's interactive shell for our development database
by typing ``psql`` (for PostgreSQL), and we'd execute the following statements::

    ALTER TABLE books_book ADD COLUMN num_pages integer;

.. admonition:: Adding NOT NULL Columns

    There's a subtlety here that deserves mention. When we added the
    ``num_pages`` field to our model, we included the ``blank=True`` and
    ``null=True`` options. We did this because a database column will contain
    NULL values when you first create it.

    However, it's also possible to add columns that cannot contain NULL values.
    To do this, you have to create the column as ``NULL``, then populate the
    column's values using some default(s), and then alter the column to set the
    ``NOT NULL`` modifier. For example::

        BEGIN;
        ALTER TABLE books_book ADD COLUMN num_pages integer;
        UPDATE books_book SET num_pages=0;
        ALTER TABLE books_book ALTER COLUMN num_pages SET NOT NULL;
        COMMIT;

    If you go down this path, remember that you should leave off
    ``blank=True`` and ``null=True`` in your model.

After the ``ALTER TABLE`` statement, we'd verify that the change worked
properly by starting the Python shell and running this code::

    >>> from mysite.books.models import Book
    >>> Book.objects.all()[:5]

If that code didn't cause errors, we'd switch to our production server and
execute the ``ALTER TABLE`` statement on the production database. Then, we'd
update the model in the production environment and restart the Web server.

Removing Fields
---------------

Removing a field from a model is a lot easier than adding one. To remove a
field, just follow these steps:

    1. Remove the field from your model and restart the Web server.

    2. Remove the column from your database, using a command like this::

           ALTER TABLE books_book DROP COLUMN num_pages;

Removing Many-to-Many Fields
----------------------------

Because many-to-many fields are different than normal fields, the removal
process is different:

    1. Remove the ``ManyToManyField`` from your model and restart the Web
       server.

    2. Remove the many-to-many table from your database, using a command like
       this::
       
           DROP TABLE books_books_publishers;

Removing Models
---------------

Removing a model entirely is as easy as removing a field. To remove a model,
just follow these steps:

    1. Remove the model from your ``models.py`` file and restart the Web server.
    
    2. Remove the table from your database, using a command like this::
    
           DROP TABLE books_book;

What's Next?
============

Once you've defined your models, the next step is to populate your database
with data. You might have legacy data, in which case Chapter 16 will give you
advice about integrating with legacy databases. You might rely on site users
to supply your data, in which case Chapter 7 will teach you how to process
user-submitted form data.

But in some cases, you or your team might need to enter data manually, in which
case it would be helpful to have a Web-based interface for entering and
managing data. The `next chapter`_ covers Django's admin interface, which exists
precisely for that reason.

.. _next chapter: ../chapter06/
