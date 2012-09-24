======================================
Appendix B: Model Definition Reference
======================================

Chapter 5 explains the basics of defining models, and we use them throughout
the rest of the book. There is, however, a *huge* range of model options
available not covered elsewhere. This appendix explains each possible model
definition option.

Note that although these APIs are considered very stable, the Django developers
consistently add new shortcuts and conveniences to the model definition. It's a good
idea to always check the latest documentation online at
http://www.djangoproject.com/documentation/0.96/model-api/.

Fields
======

The most important part of a model -- and the only required part of a model --
is the list of database fields it defines.

.. admonition:: Field Name Restrictions

    Django places only two restrictions on model field names:

        1. A field name cannot be a Python reserved word, because that would result
           in a Python syntax error, for example::

               class Example(models.Model):
                   pass = models.IntegerField() # 'pass' is a reserved word!

        2. A field name cannot contain more than one underscore in a row, due to
           the way Django's query lookup syntax works, for example::

               class Example(models.Model):
                   foo__bar = models.IntegerField() # 'foo__bar' has two underscores!

    These limitations can be worked around, though, because your field name
    doesn't necessarily have to match your database column name. See
    "db_column", below. below.

    SQL reserved words, such as ``join``, ``where``, or ``select``, *are* allowed
    as model field names, because Django escapes all database table names and
    column names in every underlying SQL query. It uses the quoting syntax of your
    particular database engine.

Each field in your model should be an instance of the appropriate ``Field``
class. Django uses the field class types to determine a few things:

    * The database column type (e.g., ``INTEGER``, ``VARCHAR``).
    
    * The widget to use in Django's admin interface, if you care to use it
      (e.g., ``<input type="text">``, ``<select>``).
    
    * The minimal validation requirements, which are used in Django's admin interface.
        
A complete list of field classes follows, sorted alphabetically. Note that
relationship fields (``ForeignKey``, etc.) are handled in the next section.

AutoField
---------

An ``IntegerField`` that automatically increments according to available IDs.
You usually won't need to use this directly; a primary key field will
automatically be added to your model if you don't specify otherwise.

BooleanField
------------

A true/false field.

CharField
---------

A string field, for small- to large-sized strings. For large amounts of text,
use ``TextField``.

``CharField`` has an extra required argument, ``maxlength``, which is the
maximum length (in characters) of the field. This maximum length is enforced
at the database level and in Django's validation.

CommaSeparatedIntegerField
--------------------------

A field of integers separated by commas. As in ``CharField``, the
``maxlength`` argument is required.

DateField
---------

A date field. ``DateField`` has a few extra optional arguments, as shown in Table B-1.

.. table:: Table B-1. Extra DateField Options

    ======================  ===================================================
    Argument                Description
    ======================  ===================================================
    ``auto_now``            Automatically sets the field to now every time the
                            object is saved. It's useful for "last-modified"
                            timestamps. Note that the current date is *always*
                            used; it's not just a default value that you can
                            override.

    ``auto_now_add``        Automatically sets the field to now when the object
                            is first created. It's useful for creation of
                            timestamps. Note that the current date is *always*
                            used; it's not just a default value that you can
                            override.
    ======================  ===================================================

DateTimeField
-------------

A date and time field. It takes the same extra options as ``DateField``.

EmailField
----------

A ``CharField`` that checks that the value is a valid email address. This
doesn't accept ``maxlength``; its ``maxlength`` is automatically set to 75.

FileField
---------

A file-upload field. It has one *required* argument, as shown in Table B-3.

.. table:: Table B-2. Extra FileField Option

    ======================  ===================================================
    Argument                Description
    ======================  ===================================================
    ``upload_to``           A local filesystem path that will be appended to
                            your ``MEDIA_ROOT`` setting to determine the
                            output of the ``get_<fieldname>_url()`` helper
                            function
    ======================  ===================================================

This path may contain ``strftime`` formatting (see
http://www.djangoproject.com/r/python/strftime/), which will be replaced by the
date/time of the file upload (so that uploaded files don't fill up the given
directory).

Using a ``FileField`` or an ``ImageField`` in a model takes a few
steps:

    1. In your settings file, you'll need to define ``MEDIA_ROOT`` as the
       full path to a directory where you'd like Django to store uploaded
       files. (For performance, these files are not stored in the database.)
       Define ``MEDIA_URL`` as the base public URL of that directory. Make
       sure that this directory is writable by the Web server's user
       account.

    2. Add the ``FileField`` or ``ImageField`` to your model, making sure
       to define the ``upload_to`` option to tell Django to which
       subdirectory of ``MEDIA_ROOT`` it should upload files.

    3. All that will be stored in your database is a path to the file
       (relative to ``MEDIA_ROOT``). You'll most likely want to use the
       convenience ``get_<fieldname>_url`` function provided by Django. For
       example, if your ``ImageField`` is called ``mug_shot``, you can get
       the absolute URL to your image in a template with ``{{
       object.get_mug_shot_url }}``.

For example, say your ``MEDIA_ROOT`` is set to ``'/home/media'``, and
``upload_to`` is set to ``'photos/%Y/%m/%d'``. The ``'%Y/%m/%d'`` part of
``upload_to`` is strftime formatting; ``'%Y'`` is the four-digit year,
``'%m'`` is the two-digit month, and ``'%d'`` is the two-digit day. If you
upload a file on January 15, 2007, it will be saved in the directory
``/home/media/photos/2007/01/15``.

If you want to retrieve the upload file's on-disk file name, or a URL that
refers to that file, or the file's size, you can use the
``get_FIELD_filename()``, ``get_FIELD_url()``, and ``get_FIELD_size()`` methods. See
Appendix C for a complete explanation of these methods.

.. note::

    Whenever you deal with uploaded files, you should pay close attention to
    where you're uploading them and what type of files they are, to avoid
    security holes. *Validate all uploaded files* so that you're sure the
    files are what you think they are. 
    
    For example, if you blindly let somebody upload files, without validation,
    to a directory that's within your Web server's document root, then
    somebody could upload a CGI or PHP script and execute that script by
    visiting its URL on your site. Don't let that happen!

FilePathField
-------------

A field whose choices are limited to the file names in a certain directory on
the filesystem. It has three special arguments, as shown in Table B-4.

.. table:: Table B-3. Extra FilePathField Options

    ======================  ===================================================
    Argument                Description
    ======================  ===================================================
    ``path``                *Required*; the absolute filesystem path to a
                            directory from which this ``FilePathField`` should
                            get its choices (e.g., ``"/home/images"``).

    ``match``               Optional; a regular expression, as a string, that
                            ``FilePathField`` will use to filter file names.
                            Note that the regex will be applied to the
                            base file name, not the full path (e.g.,
                            ``"foo.*\.txt^"``, which will match a file called
                            ``foo23.txt``, but not ``bar.txt`` or ``foo23.gif``).

    ``recursive``           Optional; either ``True`` or ``False``. The default is
                            ``False``. It specifies whether all subdirectories of
                            ``path`` should be included.
    ======================  ===================================================

Of course, these arguments can be used together.

The one potential gotcha is that ``match`` applies to the base file name,
not the full path. So, this example::

    FilePathField(path="/home/images", match="foo.*", recursive=True)

will match ``/home/images/foo.gif`` but not ``/home/images/foo/bar.gif``
because the ``match`` applies to the base file name (``foo.gif`` and
``bar.gif``).

FloatField
----------

A floating-pint number, represented in Python by a ``float`` instance. It has
two *required* arguments, as shown in Table B-2.

.. table:: Table B-4. Extra FloatField Options

    ======================  ===================================================
    Argument                Description
    ======================  ===================================================
    ``max_digits``          The maximum number of digits allowed in the number

    ``decimal_places``      The number of decimal places to store with the
                            number
    ======================  ===================================================

For example, to store numbers up to 999 with a resolution of two decimal places,
you'd use the following::

    models.FloatField(..., max_digits=5, decimal_places=2)

And to store numbers up to approximately 1 billion with a resolution of ten
decimal places, you would use this::

    models.FloatField(..., max_digits=19, decimal_places=10)

ImageField
----------

Like ``FileField``, but validates that the uploaded object is a valid image.
It has two extra optional arguments, ``height_field`` and ``width_field``, which,
if set, will be autopopulated with the height and width of the image each
time a model instance is saved.

In addition to the special ``get_FIELD_*`` methods that are available for
``FileField``, an ``ImageField`` also has ``get_FIELD_height()`` and
``get_FIELD_width()`` methods. These are documented in Appendix C.

``ImageField`` requires the Python Imaging Library
(http://www.pythonware.com/products/pil/).

IntegerField
------------

An integer.

IPAddressField
--------------

An IP address, in string format (e.g., ``"24.124.1.30"``).

NullBooleanField
----------------

Like a ``BooleanField``, but allows ``None``/``NULL`` as one of the options.
Use this instead of a ``BooleanField`` with ``null=True``.

PhoneNumberField
----------------

A ``CharField`` that checks that the value is a valid U.S.-style phone
number (in the format ``XXX-XXX-XXXX``).

.. note::

    If you need to represent a phone number from another country, check the
    ``django.contrib.localflavor`` package to see if field definitions for
    your country are included.

PositiveIntegerField
--------------------

Like an ``IntegerField``, but must be positive.

PositiveSmallIntegerField
-------------------------

Like a ``PositiveIntegerField``, but only allows values under a certain point.
The maximum value allowed by these fields is database dependent, but since
databases have a 2-byte small integer field, the maximum positive small
integer is usually 65,535.

SlugField
---------

"Slug" is a newspaper term. A *slug* is a short label for something, containing
only letters, numbers, underscores, or hyphens. They're generally used in URLs.

Like a ``CharField``, you can specify ``maxlength``. If ``maxlength`` is not
specified, Django will use a default length of 50.

A ``SlugField`` implies ``db_index=True`` since slugs are primarily used for
database lookups.

``SlugField`` accepts an extra option, ``prepopulate_from``, which is a list of fields
from which to autopopulate the slug, via JavaScript, in the object's admin
form::

    models.SlugField(prepopulate_fpom=("pre_name", "name"))

``prepopulate_from`` doesn't accept ``DateTimeField`` names as arguments.

SmallIntegerField
-----------------

Like an ``IntegerField``, but only allows values in a certain
database-dependent range (usually -32,768 to +32,767).

TextField
---------

An unlimited-length text field.

TimeField
---------

A time of day. It accepts the same autopopulation options as ``DateField`` and
``DateTimeField``.

URLField
--------

A field for a URL. If the ``verify_exists`` option is ``True`` (the default),
the URL given will be checked for existence (i.e., the URL actually loads
and doesn't give a 404 response).

Like other character fields, ``URLField`` takes the ``maxlength`` argument. If
you don't specify ``maxlength``, a default of 200 is used.

USStateField
------------

A two-letter U.S. state abbreviation.

.. note::

    If you need to represent other countries or states, look first in the
    ``django.contrib.localflavor`` package to see if Django already includes
    fields for your locale.


XMLField
--------

A ``TextField`` that checks that the value is valid XML that matches a given
schema. It takes one required argument, ``schema_path``, which is the filesystem
path to a RELAX NG (http://www.relaxng.org/) schema against which to validate the field.

Requires ``jing`` (http://thaiopensource.com/relaxng/jing.html) to validate
the XML.

Universal Field Options
=======================

The following arguments are available to all field types. All are optional.

null
----

If ``True``, Django will store empty values as ``NULL`` in the database.
The default is ``False``.

Note that empty string values will always get stored as empty strings, not as
``NULL``. Only use ``null=True`` for nonstring fields such as integers,
Booleans, and dates. For both types of fields, you will also need to set
``blank=True`` if you wish to permit empty values in forms, as the ``null``
parameter only affects database storage (see the following section, titled "blank").

Avoid using ``null`` on string-based fields such as ``CharField`` and
``TextField`` unless you have an excellent reason. If a string-based field has
``null=True``, that means it has two possible values for "no data": ``NULL``
and the empty string. In most cases, it's redundant to have two possible
values for "no data"; Django's convention is to use the empty string, not
``NULL``.

blank
-----

If ``True``, the field is allowed to be blank. The default is ``False``.

Note that this is different from ``null``. ``null`` is purely
database related, whereas ``blank`` is validation related. If a field has
``blank=True``, validation on Django's admin site will allow entry of an empty
value. If a field has ``blank=False``, the field will be required.

choices
-------

An iterable (e.g., a list, tuple, or other iterable Python object) of two tuples
to use as choices for this field.

If this is given, Django's admin interface will use a select box instead of the
standard text field and will limit choices to the choices given.

A choices list looks like this::

    YEAR_IN_SCHOOL_CHOICES = (
        ('FR', 'Freshman'),
        ('SO', 'Sophomore'),
        ('JR', 'Junior'),
        ('SR', 'Senior'),
        ('GR', 'Graduate'),
    )

The first element in each tuple is the actual value to be stored. The
second element is the human-readable name for the option.

The choices list can be defined either as part of your model class::

    class Foo(models.Model):
        GENDER_CHOICES = (
            ('M', 'Male'),
            ('F', 'Female'),
        )
        gender = models.CharField(maxlength=1, choices=GENDER_CHOICES)

or outside your model class altogether::

    GENDER_CHOICES = (
        ('M', 'Male'),
        ('F', 'Female'),
    )
    class Foo(models.Model):
        gender = models.CharField(maxlength=1, choices=GENDER_CHOICES)

For each model field that has ``choices`` set, Django will add a method to
retrieve the human-readable name for the field's current value. See Appendix
C for more details.

db_column
---------

The name of the database column to use for this field. If this isn't given,
Django will use the field's name. This is useful when you're defining a model
around a database that already exists.

If your database column name is an SQL reserved word, or if it contains characters
that aren't allowed in Python variable names (notably the hyphen), that's
OK. Django quotes column and table names behind the scenes.

db_index
--------

If ``True``, Django will create a database index on this column when creating
the table (i.e., when running ``manage.py syncdb``).
ta
default
-------

The default value for the field.

editable
--------

If ``False``, the field will not be editable in the admin interface or via form
processing. The default is ``True``.

help_text
---------

Extra "help" text to be displayed under the field on the object's admin form.
It's useful for documentation even if your object doesn't have an admin form.

primary_key
-----------

If ``True``, this field is the primary key for the model.

If you don't specify ``primary_key=True`` for any fields in your model, Django
will automatically add this field::

    id = models.AutoField('ID', primary_key=True)

Thus, you don't need to set ``primary_key=True`` on any of your fields unless
you want to override the default primary-key behavior.

``primary_key=True`` implies ``blank=False``, ``null=False``, and
``unique=True``. Only one primary key is allowed on an object.

radio_admin
-----------

By default, Django's admin uses a select-box interface (<select>) for fields
that are ``ForeignKey`` or have ``choices`` set. If ``radio_admin`` is set to
``True``, Django will use a radio-button interface instead.

Don't use this for a field unless it's a ``ForeignKey`` or has ``choices``
set.

unique
------

If ``True``, the value for this field must be unique throughout the table.

unique_for_date
---------------

Set to the name of a ``DateField`` or ``DateTimeField`` to require that
this field be unique for the value of the date field, for example::

    class Story(models.Model):
        pub_date = models.DateTimeField()
        slug = models.SlugField(unique_for_date="pub_date")
        ...

In the preceding code, Django won't allow the creation of two stories with the same
slug published on the same date. This differs from using a ``unique_together``
constraint in that only the date of the ``pub_date`` field is
taken into account; the time doesn't matter.

unique_for_month
----------------

Like ``unique_for_date``, but requires the field to be unique with respect to
the month of the given field.

unique_for_year
---------------

Like ``unique_for_date`` and ``unique_for_month``, but for an entire year.

verbose_name
------------

Each field type, except for ``ForeignKey``, ``ManyToManyField``, and
``OneToOneField``, takes an optional first positional argument -- a
verbose name. If the verbose name isn't given, Django will automatically create
it using the field's attribute name, converting underscores to spaces.

In this example, the verbose name is ``"Person's first name"``::

    first_name = models.CharField("Person's first name", maxlength=30)

In this example, the verbose name is ``"first name"``::

    first_name = models.CharField(maxlength=30)

``ForeignKey``, ``ManyToManyField``, and ``OneToOneField`` require the first
argument to be a model class, so use the ``verbose_name`` keyword argument::

    poll = models.ForeignKey(Poll, verbose_name="the related poll")
    sites = models.ManyToManyField(Site, verbose_name="list of sites")
    place = models.OneToOneField(Place, verbose_name="related place")

The convention is not to capitalize the first letter of the ``verbose_name``.
Django will automatically capitalize the first letter where it needs to.

Relationships
=============

Clearly, the power of relational databases lies in relating tables to each
other. Django offers ways to define the three most common types of database
relationships: many-to-one, many-to-many, and one-to-one.

However, the semantics of one-to-one relationships are being revisited as this
book goes to print, so they're not covered in this section. Check the online
documentation for the latest information.

Many-to-One Relationships
-------------------------

To define a many-to-one relationship, use ``ForeignKey``. You use it just like
any other ``Field`` type: by including it as a class attribute of your model.

``ForeignKey`` requires a positional argument: the class to which the model is
related. 

For example, if a ``Car`` model has a ``Manufacturer`` -- that is, a
``Manufacturer`` makes multiple cars but each ``Car`` only has one
``Manufacturer`` -- use the following definitions::

    class Manufacturer(models.Model):
        ...

    class Car(models.Model):
        manufacturer = models.ForeignKey(Manufacturer)
        ...

To create a *recursive* relationship -- an object that has a many-to-one
relationship with itself -- use ``models.ForeignKey('self')``::

    class Employee(models.Model):
        manager = models.ForeignKey('self')

If you need to create a relationship on a model that has not yet been defined,
you can use the name of the model, rather than the model object itself::

    class Car(models.Model):
        manufacturer = models.ForeignKey('Manufacturer')
        ...

    class Manufacturer(models.Model):
        ...

Note, however, that you can only use strings to refer to models in the same
``models.py`` file -- you cannot use a string to reference a model in a
different application, or to reference a model that has been imported from
elsewhere.

Behind the scenes, Django appends ``"_id"`` to the field name to create its
database column name. In the preceding example, the database table for the ``Car``
model will have a ``manufacturer_id`` column. (You can change this explicitly
by specifying ``db_column``; see the earlier "db_column" section.) However, your code
should never have to deal with the database column name, unless you write
custom SQL. You'll always deal with the field names of your model object.

It's suggested, but not required, that the name of a ``ForeignKey`` field
(``manufacturer`` in the example) be the name of the model, in lowercase letters.
You can, of course, call the field whatever you want, for example::

    class Car(models.Model):
        company_that_makes_it = models.ForeignKey(Manufacturer)
        # ...

``ForeignKey`` fields take a number of extra arguments for defining how the
relationship should work (see Table B-5). All are optional.

.. table:: Table B-5. ForeignKey Options

    =======================  ============================================================
    Argument                 Description
    =======================  ============================================================
    ``edit_inline``          If not ``False``, this related object is edited
                             "inline" on the related object's page. This means
                             that the object will not have its own admin
                             interface. Use either ``models.TABULAR`` or ``models.STACKED``,
                             which, respectively, designate whether the inline-editable
                             objects are displayed as a table or as a "stack" of
                             fieldsets.

    ``limit_choices_to``     A dictionary of lookup arguments and values (see
                             Appendix C) that limit the
                             available admin choices for this object. Use this
                             with functions from the Python ``datetime`` module
                             to limit choices of objects by date. For example, the following::

                                limit_choices_to = {'pub_date__lte': datetime.now}

                             only allows the choice of related objects with a
                             ``pub_date`` before the current date/time to be
                             chosen.

                             Instead of a dictionary, this can be a ``Q``
                             object (see Appendix C) for more complex queries.

                             This is not compatible with ``edit_inline``.

    ``max_num_in_admin``     For inline-edited objects, this is the maximum
                             number of related objects to display in the admin interface.
                             Thus, if a pizza could have only up to ten
                             toppings, ``max_num_in_admin=10`` would ensure
                             that a user never enters more than ten toppings.

                             Note that this doesn't ensure more than ten related
                             toppings ever get created. It simply controls the
                             admin interface; it doesn't enforce things at the
                             Python API level or database level.

    ``min_num_in_admin``     The minimum number of related objects displayed in
                             the admin interface. Normally, at the creation stage,
                             ``num_in_admin`` inline objects are shown, and at
                             the edit stage, ``num_extra_on_change`` blank
                             objects are shown in addition to all pre-existing
                             related objects. However, no fewer than
                             ``min_num_in_admin`` related objects will ever be
                             displayed.

    ``num_extra_on_change``  The number of extra blank related-object fields to
                             show at the change stage.

    ``num_in_admin``         The default number of inline objects to display
                             on the object page at the add stage.

    ``raw_id_admin``         Only display a field for the integer to be entered
                             instead of a drop-down menu. This is useful when
                             related to an object type that will have too many
                             rows to make a select box practical.

                             This is not used with ``edit_inline``.

    ``related_name``         The name to use for the relation from the related
                             object back to this one. See Appendix C for
                             more information.

    ``to_field``             The field on the related object that the relation
                             is to. By default, Django uses the primary key of
                             the related object.
    =======================  ============================================================

Many-to-Many Relationships
--------------------------

To define a many-to-many relationship, use ``ManyToManyField``. Like
``ForeignKey``, ``ManyToManyField`` requires a positional argument: the class
to which the model is related.

For example, if a ``Pizza`` has multiple ``Topping`` objects -- that is, a
``Topping`` can be on multiple pizzas and each ``Pizza`` has multiple toppings --
here's how you'd represent that::

    class Topping(models.Model):
        ...

    class Pizza(models.Model):
        toppings = models.ManyToManyField(Topping)
        ...
        
As with ``ForeignKey``, a relationship to self can be defined by using the
string ``'self'`` instead of the model name, and you can refer to as-yet
undefined models by using a string containing the model name. However, you
can only use strings to refer to models in the same ``models.py`` file -- you
cannot use a string to reference a model in a different application, or to
reference a model that has been imported from elsewhere.

It's suggested, but not required, that the name of a ``ManyToManyField``
(``toppings`` in the example) be a plural term describing the set of related
model objects.

Behind the scenes, Django creates an intermediary join table to represent the
many-to-many relationship.

It doesn't matter which model gets the ``ManyToManyField``, but you need
it in only one of the models -- not in both.

If you're using the admin interface, ``ManyToManyField`` instances should go
in the object that's going to be edited in the admin interface. In the preceding example,
``toppings`` is in ``Pizza`` (rather than ``Topping`` having a ``pizzas``
``ManyToManyField`` ) because it's more natural to think about a ``Pizza``
having toppings than a topping being on multiple pizzas. The way it's set up 
in the example, the ``Pizza`` admin form would let users select the toppings.

``ManyToManyField`` objects take a number of extra arguments for defining how
the relationship should work (see Table B-6). All are optional.

.. table:: Table B-6. ManyToManyField Options

    =======================  ============================================================
    Argument                 Description
    =======================  ============================================================
    ``related_name``         The name to use for the relation from the related
                             object back to this one. See Appendix C for
                             more information.

    ``filter_interface``     Use a nifty, unobtrusive JavaScript "filter" interface
                             instead of the usability-challenged ``<select multiple>``
                             in the admin form for this object. The value should be
                             ``models.HORIZONTAL`` or ``models.VERTICAL`` (i.e.,
                             should the interface be stacked horizontally or
                             vertically).

    ``limit_choices_to``     See the description under ``ForeignKey``.

    ``symmetrical``          Only used in the definition of ``ManyToManyField`` on self.
                             Consider the following model::

                                class Person(models.Model):
                                    friends = models.ManyToManyField("self")

                             When Django processes this model, it identifies that it has
                             a ``ManyToManyField`` on itself, and as a result, it
                             doesn't add a ``person_set`` attribute to the ``Person``
                             class. Instead, the ``ManyToManyField`` is assumed to be
                             symmetrical -- that is, if I am your friend, then you are
                             my friend.

                             If you do not want symmetry in ``ManyToMany`` relationships
                             with ``self``, set ``symmetrical`` to ``False``. This will
                             force Django to add the descriptor for the reverse
                             relationship, allowing ``ManyToMany`` relationships to be
                             nonsymmetrical.

    ``db_table``             The name of the table to create for storing the many-to-many
                             data. If this is not provided, Django will assume a default
                             name based upon the names of the two tables being joined.

    =======================  ============================================================

Model Metadata Options
======================

Model-specific metadata lives in a ``class Meta`` defined in the body of your
model class::

    class Book(models.Model):
        title = models.CharField(maxlength=100)

        class Meta:
            # model metadata options go here
            ...

Model metadata is "anything that's not a field," such as ordering options and so forth.

The sections that follow present a list of all possible ``Meta`` options. 
No options are required. Adding ``class Meta`` to a model is completely optional.

db_table
--------

The name of the database table to use for the model.

To save you time, Django automatically derives the name of the database table
from the name of your model class and the application that contains it. A model's
database table name is constructed by joining the model's "app label" -- the
name you used in ``manage.py startapp`` -- to the model's class name, with an
underscore between them.

For example, if you have an application ``books`` (as created by
``manage.py startapp books``), a model defined as ``class Book`` will have
a database table named ``books``.

To override the database table name, use the ``db_table`` parameter in
``class Meta``::

    class Book(models.Model):
        ...

        class Meta:
            db_table = 'things_to_read'

If this isn't given, Django will use ``app_label + '_' + model_class_name``.
See the section "Table Names" for more information.

If your database table name is an SQL reserved word, or it contains characters
that aren't allowed in Python variable names (notably the hyphen), that's
OK. Django quotes column and table names behind the scenes.

get_latest_by
-------------

The name of a ``DateField`` or ``DateTimeField`` in the model. This specifies
the default field to use in your model ``Manager``'s ``latest()`` method.

Here's an example::

    class CustomerOrder(models.Model):
        order_date = models.DateTimeField()
        ...
        
        class Meta:
            get_latest_by = "order_date"

See Appendix C for more information on the ``latest()`` method.

order_with_respect_to
---------------------

Marks this object as "orderable" with respect to the given field. This is
almost always used with related objects to allow them to be ordered with
respect to a parent object. For example, if an ``Answer`` relates to a
``Question`` object, and a question has more than one answer, and the order of
answers matters, you'd do this::

    class Answer(models.Model):
        question = models.ForeignKey(Question)
        # ...

        class Meta:
            order_with_respect_to = 'question'

ordering
--------

The default ordering for the object, for use when obtaining lists of objects::

    class Book(models.Model):
        title = models.CharField(maxlength=100)

        class Meta:
            ordering = ['title']

This is a tuple or list of strings. Each string is a field name with an
optional ``-`` prefix, which indicates descending order. Fields without a
leading ``-`` will be ordered ascending. Use the string ``"?"`` to order randomly.

For example, to order by a ``title`` field in ascending order (i.e., A-Z), use this::

    ordering = ['title']

To order by ``title`` in descending order (i.e., Z-A), use this::

    ordering = ['-title']

To order by ``title`` in descending order, and then by ``title`` in ascending order, 
use this::

    ordering = ['-title', 'author']

Note that, regardless of how many fields are in ``ordering``, the admin
site uses only the first field.

permissions
-----------

Extra permissions to enter into the permissions table when creating this
object. Add, delete, and change permissions are automatically created for each
object that has ``admin`` set. This example specifies an extra permission,
``can_deliver_pizzas``::

    class Employee(models.Model):
        ...
        
        class Meta:
            permissions = (
                ("can_deliver_pizzas", "Can deliver pizzas"),
            )

This is a list or tuple of two tuples in the format ``(permission_code,
human_readable_permission_name)``.

See Chapter 12 for more on permissions.

unique_together
---------------

Sets of field names that, taken together, must be unique::

    class Employee(models.Model):
        department = models.ForeignKey(Department)
        extension = models.CharField(maxlength=10)
        ...
    
        class Meta:
            unique_together = [("department", "extension")]

This is a list of lists of fields that must be unique when considered
together. It's used in the Django admin interface and is enforced at the database level
(i.e., the appropriate ``UNIQUE`` statements are included in the ``CREATE
TABLE`` statement).

verbose_name
------------

A human-readable name for the object, singular::

    class CustomerOrder(models.Model):
        order_date = models.DateTimeField()
        ...
    
        class Meta:
            verbose_name = "order"

If this isn't given, Django will use a adapted version of the class name in
which ``CamelCase`` becomes ``camel case``.

verbose_name_plural
-------------------

The plural name for the object::

    class Sphynx(models.Model):
        ...
        
        class Meta:
            verbose_name_plural = "sphynges"

If this isn't given, Django will add an "s" to the ``verbose_name``.

Managers
========

A ``Manager`` is the interface through which database query operations are
provided to Django models. At least one ``Manager`` exists for every model in
a Django application.

The way ``Manager`` classes work is documented in Appendix C. This section
specifically touches on model options that customize ``Manager`` behavior.

Manager Names
-------------

By default, Django adds a ``Manager`` with the name ``objects`` to every
Django model class. However, if you want to use ``objects`` as a field name,
or if you want to use a name other than ``objects`` for the ``Manager``, you
can rename it on a per-model basis. To rename the ``Manager`` for a given
class, define a class attribute of type ``models.Manager()`` on that model,
for example::

    from django.db import models

    class Person(models.Model):
        ...
        
        people = models.Manager()

Using this example model, ``Person.objects`` will generate an
``AttributeError`` exception (since ``Person`` doesn't have a ``objects``
attribute), but ``Person.people.all()`` will provide a list of all ``Person``
objects.

Custom Managers
---------------

You can use a custom ``Manager`` in a particular model by extending the base
``Manager`` class and instantiating your custom ``Manager`` in your model.

There are two reasons you might want to customize a ``Manager``: to add extra
``Manager`` methods, and/or to modify the initial ``QuerySet`` the ``Manager``
returns.

Adding Extra Manager Methods
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Adding extra ``Manager`` methods is the preferred way to add "table-level"
functionality to your models. (For "row-level" functionality -- that is,
functions that act on a single instance of a model object -- use model
methods (see below), not custom ``Manager`` methods.)

A custom ``Manager`` method can return anything you want. It doesn't have to
return a ``QuerySet``.

For example, this custom ``Manager`` offers a method ``with_counts()``, which
returns a list of all ``OpinionPoll`` objects, each with an extra
``num_responses`` attribute that is the result of an aggregate query::

    from django.db import connection

    class PollManager(models.Manager):
        
        def with_counts(self):
            cursor = connection.cursor()
            cursor.execute("""
                SELECT p.id, p.question, p.poll_date, COUNT(*)
                FROM polls_opinionpoll p, polls_response r
                WHERE p.id = r.poll_id
                GROUP BY 1, 2, 3
                ORDER BY 3 DESC""")
            result_list = []
            for row in cursor.fetchall():
                p = self.model(id=row[0], question=row[1], poll_date=row[2])
                p.num_responses = row[3]
                result_list.append(p)
            return result_list

    class OpinionPoll(models.Model):
        question = models.CharField(maxlength=200)
        poll_date = models.DateField()
        objects = PollManager()

    class Response(models.Model):
        poll = models.ForeignKey(Poll)
        person_name = models.CharField(maxlength=50)
        response = models.TextField()

With this example, you'd use ``OpinionPoll.objects.with_counts()`` to return
that list of ``OpinionPoll`` objects with ``num_responses`` attributes.

Another thing to note about this example is that ``Manager`` methods can
access ``self.model`` to get the model class to which they're attached.

Modifying Initial Manager QuerySets
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A ``Manager``'s base ``QuerySet`` returns all objects in the system. For
example, using this model::

    class Book(models.Model):
        title = models.CharField(maxlength=100)
        author = models.CharField(maxlength=50)

the statement ``Book.objects.all()`` will return all books in the database.

You can override the base ``QuerySet`` by overriding the
``Manager.get_query_set()`` method. ``get_query_set()`` should return a
``QuerySet`` with the properties you require.

For example, the following model has *two* managers -- one that returns all
objects, and one that returns only the books by Roald Dahl::

    # First, define the Manager subclass.
    class DahlBookManager(models.Manager):
        def get_query_set(self):
            return super(DahlBookManager, self).get_query_set().filter(author='Roald Dahl')

    # Then hook it into the Book model explicitly.
    class Book(models.Model):
        title = models.CharField(maxlength=100)
        author = models.CharField(maxlength=50)

        objects = models.Manager() # The default manager.
        dahl_objects = DahlBookManager() # The Dahl-specific manager.

With this sample model, ``Book.objects.all()`` will return all books in the
database, but ``Book.dahl_objects.all()`` will return only the ones written by
Roald Dahl.

Of course, because ``get_query_set()`` returns a ``QuerySet`` object, you can
use ``filter()``, ``exclude()``, and all the other ``QuerySet`` methods on it.
So these statements are all legal::

    Book.dahl_objects.all()
    Book.dahl_objects.filter(title='Matilda')
    Book.dahl_objects.count()

This example also points out another interesting technique: using multiple
managers on the same model. You can attach as many ``Manager()`` instances to
a model as you'd like. This is an easy way to define common "filters" for your
models. Here's an example::

    class MaleManager(models.Manager):
        def get_query_set(self):
            return super(MaleManager, self).get_query_set().filter(sex='M')

    class FemaleManager(models.Manager):
        def get_query_set(self):
            return super(FemaleManager, self).get_query_set().filter(sex='F')

    class Person(models.Model):
        first_name = models.CharField(maxlength=50)
        last_name = models.CharField(maxlength=50)
        sex = models.CharField(maxlength=1, choices=(('M', 'Male'), ('F', 'Female')))
        people = models.Manager()
        men = MaleManager()
        women = FemaleManager()

This example allows you to request ``Person.men.all()``,
``Person.women.all()``, and ``Person.people.all()``, yielding predictable
results.

If you use custom ``Manager`` objects, take note that the first ``Manager``
Django encounters (in order by which they're defined in the model) has a
special status. Django interprets the first ``Manager`` defined in a class as
the "default" ``Manager``. Certain operations -- such as Django's admin site
-- use the default ``Manager`` to obtain lists of objects, so it's generally a
good idea for the first ``Manager`` to be relatively unfiltered. In the last
example, the ``people`` ``Manager`` is defined first -- so it's the default
``Manager``.

Model Methods
=============

Define custom methods on a model to add custom "row-level" functionality to
your objects. Whereas ``Manager`` methods are intended to do "tablewide"
things, model methods should act on a particular model instance.

This is a valuable technique for keeping business logic in one place: the
model. For example, this model has a few custom methods::

    class Person(models.Model):
        first_name = models.CharField(maxlength=50)
        last_name = models.CharField(maxlength=50)
        birth_date = models.DateField()
        address = models.CharField(maxlength=100)
        city = models.CharField(maxlength=50)
        state = models.USStateField() # Yes, this is America-centric...

        def baby_boomer_status(self):
            """Returns the person's baby-boomer status."""
            import datetime
            if datetime.date(1945, 8, 1) <= self.birth_date <= datetime.date(1964, 12, 31):
                return "Baby boomer"
            if self.birth_date < datetime.date(1945, 8, 1):
                return "Pre-boomer"
            return "Post-boomer"

        def is_midwestern(self):
            """Returns True if this person is from the Midwest."""
            return self.state in ('IL', 'WI', 'MI', 'IN', 'OH', 'IA', 'MO')

        @property
        def full_name(self):
            """Returns the person's full name."""
            return '%s %s' % (self.first_name, self.last_name)

The last method in this example is a *property* -- an attribute implemented by
custom getter/setter user code. Properties are a nifty trick added to Python
2.2; you can read more about them at
http://www.python.org/download/releases/2.2/descrintro/#property.

There are also a handful of model methods that have "special" meaning to
Python or Django. These methods are described in the sections that follow.

__str__
-------

``__str__()`` is a Python "magic method" that defines what should be returned
if you call ``str()`` on the object. Django uses ``str(obj)`` (or the related
function, ``unicode(obj)``, described shortly) in a number of places, most notably
as the value displayed to render an object in the Django admin site and as the
value inserted into a template when it displays an object. Thus, you should
always return a nice, human-readable string for the object's ``__str__``.
Although this isn't required, it's strongly encouraged.

Here's an example::

    class Person(models.Model):
        first_name = models.CharField(maxlength=50)
        last_name = models.CharField(maxlength=50)

        def __str__(self):
            return '%s %s' % (self.first_name, self.last_name)

get_absolute_url
----------------

Define a ``get_absolute_url()`` method to tell Django how to calculate the URL
for an object, for example::

    def get_absolute_url(self):
        return "/people/%i/" % self.id

Django uses this in its admin interface. If an object defines
``get_absolute_url()``, the object-editing page will have a "View on site"
link that will take you directly to the object's public view, according to
``get_absolute_url()``.

Also, a couple of other bits of Django, such as the syndication-feed framework,
use ``get_absolute_url()`` as a convenience to reward people who've defined the
method.

It's good practice to use ``get_absolute_url()`` in templates, instead of
hard-coding your objects' URLs. For example, this template code is bad::

    <a href="/people/{{ object.id }}/">{{ object.name }}</a>

But this template code is good::

    <a href="{{ object.get_absolute_url }}">{{ object.name }}</a>

The problem with the way we just wrote ``get_absolute_url()`` is that it
slightly violates the DRY principle: the URL for this object is defined both
in the URLconf file and in the model.

You can further decouple your models from the URLconf using the ``permalink``
decorator. This decorator is passed the view function, a list of positional
parameters, and (optionally) a dictionary of named parameters. Django then
works out the correct full URL path using the URLconf, substituting the
parameters you have given into the URL. For example, if your URLconf
contained a line such as the following::

    (r'^people/(\d+)/$', 'people.views.details'),

your model could have a ``get_absolute_url`` method that looked like this::

    @models.permalink
    def get_absolute_url(self):
        return ('people.views.details', [str(self.id)])

Similarly, if you had a URLconf entry that looked like this::

    (r'/archive/(?P<year>\d{4})/(?P<month>\d{1,2})/(?P<day>\d{1,2})/$', archive_view)

you could reference this using ``permalink()`` as follows::

    @models.permalink
    def get_absolute_url(self):
        return ('archive_view', (), {
            'year': self.created.year,
            'month': self.created.month,
            'day': self.created.day})

Notice that we specify an empty sequence for the second argument in this case,
because we want to pass only keyword arguments, not named arguments.

In this way, you're tying the model's absolute URL to the view that is used
to display it, without repeating the URL information anywhere. You can still
use the ``get_absolute_url`` method in templates, as before.

Executing Custom SQL
--------------------

Feel free to write custom SQL statements in custom model methods and
module-level methods. The object ``django.db.connection`` represents the
current database connection. To use it, call ``connection.cursor()`` to get a
cursor object. Then, call ``cursor.execute(sql, [params])`` to execute the SQL,
and ``cursor.fetchone()`` or ``cursor.fetchall()`` to return the resulting
rows::

    def my_custom_sql(self):
        from django.db import connection
        cursor = connection.cursor()
        cursor.execute("SELECT foo FROM bar WHERE baz = %s", [self.baz])
        row = cursor.fetchone()
        return row

``connection`` and ``cursor`` mostly implement the standard Python DB-API
(http://www.python.org/peps/pep-0249.html). If you're not familiar with the
Python DB-API, note that the SQL statement in ``cursor.execute()`` uses
placeholders, ``"%s"``, rather than adding parameters directly within the SQL.
If you use this technique, the underlying database library will automatically
add quotes and escaping to your parameter(s) as necessary. (Also note that
Django expects the ``"%s"`` placeholder, *not* the ``"?"`` placeholder, which
is used by the SQLite Python bindings. This is for the sake of consistency and
sanity.)

A final note: If all you want to do is use a custom ``WHERE`` clause, you can just
use the ``where``, ``tables``, and ``params`` arguments to the standard lookup
API. See Appendix C.

Overriding Default Model Methods
--------------------------------

As explained in Appendix C, each model gets a few methods automatically
-- most notably, ``save()`` and ``delete()``. You can override these methods
to alter behavior.

A classic use-case for overriding the built-in methods is if you want something
to happen whenever you save an object, for example::

    class Blog(models.Model):
        name = models.CharField(maxlength=100)
        tagline = models.TextField()

        def save(self):
            do_something()
            super(Blog, self).save() # Call the "real" save() method.
            do_something_else()

You can also prevent saving::

    class Blog(models.Model):
        name = models.CharField(maxlength=100)
        tagline = models.TextField()

        def save(self):
            if self.name == "Yoko Ono's blog":
                return # Yoko shall never have her own blog!
            else:
                super(Blog, self).save() # Call the "real" save() method

Admin Options
=============

The ``Admin`` class tells Django how to display the model in the admin site.

The following sections present a list of all possible ``Admin`` options. None of 
these options is required. To use an admin interface without specifying any options, use
``pass``, like so::

    class Admin:
        pass

Adding ``class Admin`` to a model is completely optional.

date_hierarchy
--------------

Set ``date_hierarchy`` to the name of a ``DateField`` or ``DateTimeField`` in
your model, and the change list page will include a date-based navigation
using that field.

Here's an example::

    class CustomerOrder(models.Model):
        order_date = models.DateTimeField()
        ...

        class Admin:
            date_hierarchy = "order_date"

fields
------

Set ``fields`` to control the layout of admin interface "add" and "change" pages.

``fields`` is a pretty complex nested data structure best demonstrated with an example. 
The following is taken from the ``FlatPage`` model that's part of 
``django.contrib.flatpages``::

    class FlatPage(models.Model):
        ...

        class Admin:
            fields = (
                (None, {
                    'fields': ('url', 'title', 'content', 'sites')
                }),
                ('Advanced options', {
                    'classes': 'collapse',
                    'fields' : ('enable_comments', 'registration_required', 'template_name')
                }),
            )

Formally, ``fields`` is a list of two tuples, in which each two-tuple
represents a ``<fieldset>`` on the admin form page. (A ``<fieldset>`` is a
"section" of the form.)

The two-tuples are in the format ``(name, field_options)``, where ``name`` is a
string representing the title of the fieldset and ``field_options`` is a
dictionary of information about the fieldset, including a list of fields to be
displayed in it.

If ``fields`` isn't given, Django will default to displaying each field that
isn't an ``AutoField`` and has ``editable=True``, in a single fieldset, in
the same order as the fields are defined in the model.

The ``field_options`` dictionary can have the keys described in the sections that follow.

fields
~~~~~~

A tuple of field names to display in this fieldset. This key is required.

To display multiple fields on the same line, wrap those fields in their own
tuple. In this example, the ``first_name`` and ``last_name`` fields will
display on the same line::

    'fields': (('first_name', 'last_name'), 'address', 'city', 'state'),

classes
~~~~~~~

A string containing extra CSS classes to apply to the fieldset.

Apply multiple classes by separating them with spaces::

    'classes': 'wide extrapretty',

Two useful classes defined by the default admin site stylesheet are
``collapse`` and ``wide``. Fieldsets with the ``collapse`` style will be
initially collapsed in the admin site and replaced with a small "click to expand"
link. Fieldsets with the ``wide`` style will be given extra horizontal space.

description
~~~~~~~~~~~

A string of optional extra text to be displayed at the top of each fieldset,
under the heading of the fieldset. It's used verbatim, so you can use any HTML
and you must escape any special HTML characters (such as ampersands) yourself.

js
--

A list of strings representing URLs of JavaScript files to link into the admin
screen via ``<script src="">`` tags. This can be used to tweak a given type of
admin page in JavaScript or to provide "quick links" to fill in default values
for certain fields.

If you use relative URLs -- that is, URLs that don't start with ``http://`` or ``/`` --
then the admin site will automatically prefix these links with
``settings.ADMIN_MEDIA_PREFIX``.

list_display
------------

Set ``list_display`` to control which fields are displayed on the change list
page of the admin.

If you don't set ``list_display``, the admin site will display a single column
that displays the ``__str__()`` representation of each object.

Here are a few special cases to note about ``list_display``:

    * If the field is a ``ForeignKey``, Django will display the ``__str__()``
      of the related object.

    * ``ManyToManyField`` fields aren't supported, because that would entail
      executing a separate SQL statement for each row in the table. If you
      want to do this nonetheless, give your model a custom method, and add
      that method's name to ``list_display``. (More information on custom
      methods in ``list_display`` shortly.)

    * If the field is a ``BooleanField`` or ``NullBooleanField``, Django will
      display a pretty "on" or "off" icon instead of ``True`` or ``False``.

    * If the string given is a method of the model, Django will call it and
      display the output. This method should have a ``short_description``
      function attribute, for use as the header for the field.

      Here's a full example model::

          class Person(models.Model):
              name = models.CharField(maxlength=50)
              birthday = models.DateField()

              class Admin:
                  list_display = ('name', 'decade_born_in')

              def decade_born_in(self):
                  return self.birthday.strftime('%Y')[:3] + "0's"
              decade_born_in.short_description = 'Birth decade'

    * If the string given is a method of the model, Django will HTML-escape the
      output by default. If you'd rather not escape the output of the method,
      give the method an ``allow_tags`` attribute whose value is ``True``.

      Here's a full example model::

          class Person(models.Model):
              first_name = models.CharField(maxlength=50)
              last_name = models.CharField(maxlength=50)
              color_code = models.CharField(maxlength=6)

              class Admin:
                  list_display = ('first_name', 'last_name', 'colored_name')

              def colored_name(self):
                  return '<span style="color: #%s;">%s %s</span>' % (self.color_code, self.first_name, self.last_name)
              colored_name.allow_tags = True

    * If the string given is a method of the model that returns ``True`` or ``False``,
      Django will display a pretty "on" or "off" icon if you give the method a
      ``boolean`` attribute whose value is ``True``.

      Here's a full example model::

          class Person(models.Model):
              first_name = models.CharField(maxlength=50)
              birthday = models.DateField()

              class Admin:
                  list_display = ('name', 'born_in_fifties')

              def born_in_fifties(self):
                  return self.birthday.strftime('%Y')[:3] == 5
              born_in_fifties.boolean = True


    * The ``__str__()`` methods are just as valid in ``list_display`` as any 
      other model method, so it's perfectly OK to do this::

          list_display = ('__str__', 'some_other_field')

    * Usually, elements of ``list_display`` that aren't actual database fields
      can't be used in sorting (because Django does all the sorting at the
      database level).

      However, if an element of ``list_display`` represents a certain database
      field, you can indicate this fact by setting the ``admin_order_field``
      attribute of the item, for example::

        class Person(models.Model):
            first_name = models.CharField(maxlength=50)
            color_code = models.CharField(maxlength=6)

            class Admin:
                list_display = ('first_name', 'colored_first_name')

            def colored_first_name(self):
                return '<span style="color: #%s;">%s</span>' % (self.color_code, self.first_name)
            colored_first_name.allow_tags = True
            colored_first_name.admin_order_field = 'first_name'

      The preceding code will tell Django to order by the ``first_name`` field when
      trying to sort by ``colored_first_name`` in the admin site.

list_display_links
------------------

Set ``list_display_links`` to control which fields in ``list_display`` should
be linked to the "change" page for an object.

By default, the change list page will link the first column -- the first field
specified in ``list_display`` -- to the change page for each item. But
``list_display_links`` lets you change which columns are linked. Set
``list_display_links`` to a list or tuple of field names (in the same format as
``list_display``) to link.

``list_display_links`` can specify one or many field names. As long as the
field names appear in ``list_display``, Django doesn't care how many (or how
few) fields are linked. The only requirement is that if you want to use
``list_display_links``, you must define ``list_display``.

In this example, the ``first_name`` and ``last_name`` fields will be linked on
the change list page::

    class Person(models.Model):
        ...

        class Admin:
            list_display = ('first_name', 'last_name', 'birthday')
            list_display_links = ('first_name', 'last_name')

Finally, note that in order to use ``list_display_links``, you must define
``list_display``, too.

list_filter
-----------

Set ``list_filter`` to activate filters in the right sidebar of the change list
page of the admin interface. This should be a list of field names, and each specified
field should be either a ``BooleanField``, ``DateField``, ``DateTimeField``,
or ``ForeignKey``.

This example, taken from the ``django.contrib.auth.models.User`` model, shows
how both ``list_display`` and ``list_filter`` work::

    class User(models.Model):
        ...
        
        class Admin:
            list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff')
            list_filter = ('is_staff', 'is_superuser')

list_per_page
-------------

Set ``list_per_page`` to control how many items appear on each paginated admin
change list page. By default, this is set to ``100``.

list_select_related
-------------------

Set ``list_select_related`` to tell Django to use ``select_related()`` in
retrieving the list of objects on the admin change list page. This can save
you a bunch of database queries if you're using related objects in the admin
change list display.

The value should be either ``True`` or ``False``. The default is ``False``
unless one of the ``list_display`` fields is a ``ForeignKey``.

For more on ``select_related()``, see Appendix C.

ordering
--------

Set ``ordering`` to specify how objects on the admin change list page should
be ordered. This should be a list or tuple in the same format as a model's
``ordering`` parameter.

If this isn't provided, the Django admin interface will use the model's default
ordering.

save_as
-------

Set ``save_as`` to ``True`` to enable a "save as" feature on admin change
forms.

Normally, objects have three save options: "Save," "Save and continue editing,"
and "Save and add another." If ``save_as`` is ``True``, "Save and add another"
will be replaced by a "Save as" button.

"Save as" means the object will be saved as a new object (with a new ID),
rather than the old object.

By default, ``save_as`` is set to ``False``.

save_on_top
-----------

Set ``save_on_top`` to add save buttons across the top of your admin change
forms.

Normally, the save buttons appear only at the bottom of the forms. If you set
``save_on_top``, the buttons will appear both on the top and the bottom.

By default, ``save_on_top`` is set to ``False``.

search_fields
-------------

Set ``search_fields`` to enable a search box on the admin change list page.
This should be set to a list of field names that will be searched whenever
somebody submits a search query in that text box.

These fields should be some kind of text field, such as ``CharField`` or
``TextField``. You can also perform a related lookup on a ``ForeignKey`` with
the lookup API "follow" notation::
    
    class Employee(models.Model):
        department = models.ForeignKey(Department)
        ...
        
        class Admin:
            search_fields = ['department__name']

When somebody does a search in the admin search box, Django splits the search
query into words and returns all objects that contain each of the words, case
insensitive, where each word must be in at least one of ``search_fields``. For
example, if ``search_fields`` is set to ``['first_name', 'last_name']`` and a
user searches for ``john lennon``, Django will do the equivalent of this SQL
``WHERE`` clause::

    WHERE (first_name ILIKE '%john%' OR last_name ILIKE '%john%')
    AND (first_name ILIKE '%lennon%' OR last_name ILIKE '%lennon%')

For faster and/or more restrictive searches, prefix the field name
with an operator, as shown in Table B-7.

.. table:: Table B-7. Operators Allowed in search_fields
    
    ==========  =================================================================
    Operator    Meaning
    ==========  =================================================================
    ``^``       Matches the beginning of the field. For example, if
                ``search_fields`` is set to ``['^first_name', '^last_name']``,
                and a user searches for ``john lennon``, Django will do the
                equivalent of this SQL ``WHERE`` clause::

                    WHERE (first_name ILIKE 'john%' OR last_name ILIKE 'john%')
                    AND (first_name ILIKE 'lennon%' OR last_name ILIKE 'lennon%')

                This query is more efficient than the normal ``'%john%'``
                query, because the database only needs to check the beginning
                of a column's data, rather than seeking through the entire
                column's data. Plus, if the column has an index on it, some
                databases may be able to use the index for this query, even
                though it's a ``LIKE`` query.

    ``=``       Matches exactly, case-insensitive. For example, if
                ``search_fields`` is set to ``['=first_name', '=last_name']``
                and a user searches for ``john lennon``, Django will do the
                equivalent of this SQL ``WHERE`` clause::
                
                     WHERE (first_name ILIKE 'john' OR last_name ILIKE 'john') 
                     AND (first_name ILIKE 'lennon' OR last_name ILIKE 'lennon')
                
                Note that the query input is split by spaces, so, following
                this example, it's currently not possible to search for
                all records in which ``first_name`` is exactly ``'john
                winston'`` (containing a space).

    ``@``       Performs a full-text match. This is like the default search 
                method, but it uses an index. Currently this is available only for
                MySQL.
    ==========  =================================================================
