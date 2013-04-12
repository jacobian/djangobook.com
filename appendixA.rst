======================================
Appendix A: Model Definition Reference
======================================

Chapter 5 explains the basics of defining models, and we use them throughout
the rest of the book. There is, however, a *huge* range of model options
available not covered elsewhere. This appendix explains each possible model
definition option.

Note that although these APIs are considered stable, the Django developers
consistently add new shortcuts and conveniences to the model definition. It's a
good idea to always check the latest documentation online at
http://docs.djangoproject.com/.

Fields
======

The most important part of a model -- and the only required part of a model --
is the list of database fields it defines.

.. admonition:: Field Name Restrictions

    Django places only two restrictions on model field names:

    1. A field name cannot be a Python reserved word, because that would result
       in a Python syntax error. For example::

           class Example(models.Model):
               pass = models.IntegerField() # 'pass' is a reserved word!

    2. A field name cannot contain more than one underscore in a row, due to
       the way Django's query lookup syntax works. For example::

           class Example(models.Model):
               foo__bar = models.IntegerField() # 'foo__bar' has two underscores!

    These limitations can be worked around, though, because your field name
    doesn't necessarily have to match your database column name. See
    "db_column", below.

    SQL reserved words, such as ``join``, ``where``, or ``select``, *are* allowed
    as model field names, because Django escapes all database table names and
    column names in every underlying SQL query. It uses the quoting syntax of your
    particular database engine.

Each field in your model should be an instance of the appropriate ``Field``
class. Django uses the field class types to determine a few things:

* The database column type (e.g., ``INTEGER``, ``VARCHAR``).

* The widget to use in Django's forms and admin site, if you care to use it
  (e.g., ``<input type="text">``, ``<select>``).

* The minimal validation requirements, which are used in Django's admin
  interface and by forms.

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

.. admonition:: MySQL users...

    A boolean field in MySQL is stored as a ``TINYINT`` column with a value of
    either 0 or 1 (most databases have a proper ``BOOLEAN`` type instead). So,
    for MySQL, only, when a ``BooleanField`` is retrieved from the database
    and stored on a model attribute, it will have the values 1 or 0, rather
    than ``True`` or ``False``. Normally, this shouldn't be a problem, since
    Python guarantees that ``1 == True`` and ``0 == False`` are both true.
    Just be careful if you're writing something like ``obj is True`` when
    ``obj`` is a value from a boolean attribute on a model. If that model was
    constructed using the ``mysql`` backend, the "``is``" test will fail.
    Prefer an equality test (using "``==``") in cases like this.

CharField
---------

A string field, for small- to large-sized strings.

For very large amounts of text, use ``TextField``.

``CharField`` has one extra required argument: ``max_length``. This is the
maximum length (in characters) of the field. The ``max_length`` is enforced
at the database level and in Django's validation.

CommaSeparatedIntegerField
--------------------------

A field of integers separated by commas. As in ``CharField``, the
``max_length`` argument is required.

DateField
---------

A date, represented in Python by a ``datetime.date`` instance.

DateTimeField
-------------

A date and time, represented in Python by a ``datetime.datetime`` instance.

DecimalField
------------

A fixed-precision decimal number, represented in Python by a
``decimal.Decimal`` instance. Has two **required** arguments:

``max_digits``
    The maximum number of digits allowed in the number

``decimal_places``
    The number of decimal places to store with the number

For example, to store numbers up to 999 with a resolution of 2 decimal places,
you'd use::

    models.DecimalField(..., max_digits=5, decimal_places=2)

And to store numbers up to approximately one billion with a resolution of 10
decimal places::

    models.DecimalField(..., max_digits=19, decimal_places=10)

When assigning to a ``DecimalField``, use either a ``decimal.Decimal`` object
or a string -- not a Python float.

EmailField
----------

A ``CharField`` that checks that the value is a valid e-mail address.

FileField
---------

A file-upload field.

.. note::
    The ``primary_key`` and ``unique`` arguments are not supported, and will
    raise a ``TypeError`` if used.

Has one **required** argument:

``upload_to``
    A local filesystem path that will be appended to your ``MEDIA_ROOT``
    setting to determine the value of the ``django.core.files.File.url``
    attribute.

    This path may contain "strftime formatting" (see the Python docs for the
    ``time`` standard library module), which will be replaced using the
    date/time of the file upload (so that uploaded files don't fill up the given
    directory).

    This may also be a callable, such as a function, which will be called to
    obtain the upload path, including the filename. This callable must be able
    to accept two arguments, and return a Unix-style path (with forward slashes)
    to be passed along to the storage system. The two arguments that will be
    passed are:

    ======================  ===============================================
    Argument                Description
    ======================  ===============================================
    ``instance``            An instance of the model where the
                            ``FileField`` is defined. More specifically,
                            this is the particular instance where the
                            current file is being attached.

                            In most cases, this object will not have been
                            saved to the database yet, so if it uses the
                            default ``AutoField``, *it might not yet have a
                            value for its primary key field*.

    ``filename``            The filename that was originally given to the
                            file. This may or may not be taken into account
                            when determining the final destination path.
    ======================  ===============================================

Also has one optional argument:

``storage``
    Optional. A storage object, which handles the storage and retrieval of your
    files.

Using a ``FileField`` or an ``ImageField`` (see below) in a model
takes a few steps:

1. In your settings file, you'll need to define ``MEDIA_ROOT`` as the
   full path to a directory where you'd like Django to store uploaded files.
   (For performance, these files are not stored in the database.) Define
   ``MEDIA_URL`` as the base public URL of that directory. Make sure
   that this directory is writable by the Web server's user account.

2. Add the ``FileField`` or ``ImageField`` to your model, making
   sure to define the ``upload_to`` option to tell Django
   to which subdirectory of ``MEDIA_ROOT`` it should upload files.

3. All that will be stored in your database is a path to the file
   (relative to ``MEDIA_ROOT``). You'll most likely want to use the
   convenience ``url`` function provided by
   Django. For example, if your ``ImageField`` is called ``mug_shot``,
   you can get the absolute URL to your image in a template with
   ``{{ object.mug_shot.url }}``.

For example, say your ``MEDIA_ROOT`` is set to ``'/home/media'``, and
``upload_to`` is set to ``'photos/%Y/%m/%d'``. The ``'%Y/%m/%d'``
part of ``upload_to`` is strftime formatting; ``'%Y'`` is the
four-digit year, ``'%m'`` is the two-digit month and ``'%d'`` is the two-digit
day. If you upload a file on Jan. 15, 2007, it will be saved in the directory
``/home/media/photos/2007/01/15``.

If you want to retrieve the upload file's on-disk filename, or a URL that refers
to that file, or the file's size, you can use the
``name``, ``url`` and ``size`` attributes.

Note that whenever you deal with uploaded files, you should pay close attention
to where you're uploading them and what type of files they are, to avoid
security holes. *Validate all uploaded files* so that you're sure the files are
what you think they are. For example, if you blindly let somebody upload files,
without validation, to a directory that's within your Web server's document
root, then somebody could upload a CGI or PHP script and execute that script by
visiting its URL on your site. Don't allow that.

By default, ``FileField`` instances are
created as ``varchar(100)`` columns in your database. As with other fields, you
can change the maximum length using the ``max_length`` argument.

FilePathField
-------------

A ``CharField`` whose choices are limited to the filenames in a certain
directory on the filesystem. Has three special arguments, of which the first is
**required**:

``path``
    Required. The absolute filesystem path to a directory from which this
    ``FilePathField`` should get its choices. Example: ``"/home/images"``.

``match``
    Optional. A regular expression, as a string, that ``FilePathField``
    will use to filter filenames. Note that the regex will be applied to the
    base filename, not the full path. Example: ``"foo.*\.txt$"``, which will
    match a file called ``foo23.txt`` but not ``bar.txt`` or ``foo23.gif``.

``recursive``
    Optional. Either ``True`` or ``False``. Default is ``False``. Specifies
    whether all subdirectories of ``path`` should be included.

Of course, these arguments can be used together.

The one potential gotcha is that ``match`` applies to the
base filename, not the full path. So, this example::

    FilePathField(path="/home/images", match="foo.*", recursive=True)

...will match ``/home/images/bar/foo.gif`` but not ``/home/images/foo/bar.gif``
because the ``match`` applies to the base filename
(``foo.gif`` and ``bar.gif``).

By default, ``FilePathField`` instances are
created as ``varchar(100)`` columns in your database. As with other fields, you
can change the maximum length using the ``max_length`` argument.

FloatField
----------

A floating-point number represented in Python by a ``float`` instance.

ImageField
----------

Like ``FileField``, but validates that the uploaded object is a valid
image. Has two extra optional arguments:

``height_field``
    Name of a model field which will be auto-populated with the height of the
    image each time the model instance is saved.

``width_field``
    Name of a model field which will be auto-populated with the width of the
    image each time the model instance is saved.

In addition to the special attributes that are available for FileField``,
an ``ImageField`` also has ``height`` and ``width`` attributes, both of which
correspond to the image's height and width in pixels.

Requires the Python Imaging Library, available at http://www.pythonware.com/products/pil/.

By default, ``ImageField`` instances are
created as ``varchar(100)`` columns in your database. As with other fields, you
can change the maximum length using the ``max_length`` argument.

IntegerField
------------

An integer.

IPAddressField
--------------

An IP address, in string format (e.g. ``'192.0.2.30'``).

NullBooleanField
----------------

Like a ``BooleanField``, but allows ``NULL`` as one of the options. Use
this instead of a ``BooleanField`` with ``null=True``.

PositiveIntegerField
--------------------

Like an ``IntegerField``, but must be positive.

PositiveSmallIntegerField
-------------------------

Like a ``PositiveIntegerField``, but only allows values under a certain
(database-dependent) point.

SlugField
---------

"Slug" is a newspaper term. A slug is a short label for something,
containing only letters, numbers, underscores or hyphens. They're generally used
in URLs.

Like a ``CharField``, you can specify ``max_length``. If ``max_length`` is not
specified, Django will use a default length of 50.

Implies setting ``db_index`` to ``True``.

SmallIntegerField
-----------------

Like an ``IntegerField``, but only allows values under a certain
(database-dependent) point.

TextField
---------

A large text field.

Also see ``CharField`` for storing smaller bits of text.

TimeField
---------

A time, represented in Python by a ``datetime.time`` instance. Accepts the same
auto-population options as ``DateField``.

URLField
--------

A ``CharField`` for a URL. Has one extra optional argument:

``verify_exists``
    If ``True`` (the default), the URL given will be checked for existence
    (i.e., the URL actually loads and doesn't give a 404 response). It should
    be noted that when using the single-threaded development server, validating
    a url being served by the same server will hang.
    This should not be a problem for multithreaded servers.

Like all ``CharField`` subclasses, ``URLField`` takes the optional
``max_length`` argument. If you don't specify
``max_length``, a default of 200 is used.

XMLField
--------

A ``TextField`` that checks that the value is valid XML that matches a
given schema. Takes one required argument:

``schema_path``
    The filesystem path to a RelaxNG schema against which to validate the
    field. For more on RelaxNG, see http://www.relaxng.org/.

Universal Field Options
=======================

The following arguments are available to all field types. All are optional.

null
----

If ``True``, Django will store empty values as ``NULL`` in the database. If
``False``, saving empty values will likely result in a database error. Default
is ``False``.

Note that empty string values will always get stored as empty strings, not as
``NULL``. Only use ``null=True`` for non-string fields such as integers,
booleans and dates. For both types of fields, you will also need to set
``blank=True`` if you wish to permit empty values in forms, as the
``null`` parameter only affects database storage (see
``blank``).

Avoid using ``null`` on string-based fields such as
``CharField`` and ``TextField`` unless you have an excellent reason.
If a string-based field has ``null=True``, that means it has two possible values
for "no data": ``NULL``, and the empty string. In most cases, it's redundant to
have two possible values for "no data;" Django's convention is to use the empty
string, not ``NULL``.

.. note::

    When using the Oracle database backend, the ``null=True`` option will be
    coerced for string-based fields that have the empty string as a possible
    value, and the value ``NULL`` will be stored to denote the empty string.

For more on this, see the section "Making Date and Numeric Fields Optional" in
Chapter 6.

blank
-----

If ``True``, the field is allowed to be blank. Default is ``False``.

Note that this is different than ``null``. ``null`` is
purely database-related, whereas ``blank`` is validation-related. If
a field has ``blank=True``, validation on Django's admin site will allow entry
of an empty value. If a field has ``blank=False``, the field will be required.

choices
-------

An iterable (e.g., a list or tuple) of 2-tuples to use as choices for this
field.

A choices list looks like this::

    YEAR_IN_SCHOOL_CHOICES = (
        ('FR', 'Freshman'),
        ('SO', 'Sophomore'),
        ('JR', 'Junior'),
        ('SR', 'Senior'),
        ('GR', 'Graduate'),
    )

The first element in each tuple is the actual value to be stored. The second
element is the human-readable name for the option.

The choices list can be defined either as part of your model class::

    class Foo(models.Model):
        GENDER_CHOICES = (
            ('M', 'Male'),
            ('F', 'Female'),
        )
        gender = models.CharField(max_length=1, choices=GENDER_CHOICES)

or outside your model class altogether::

    GENDER_CHOICES = (
        ('M', 'Male'),
        ('F', 'Female'),
    )
    class Foo(models.Model):
        gender = models.CharField(max_length=1, choices=GENDER_CHOICES)

You can also collect your available choices into named groups that can
be used for organizational purposes in a form::

    MEDIA_CHOICES = (
        ('Audio', (
                ('vinyl', 'Vinyl'),
                ('cd', 'CD'),
            )
        ),
        ('Video', (
                ('vhs', 'VHS Tape'),
                ('dvd', 'DVD'),
            )
        ),
        ('unknown', 'Unknown'),
    )

The first element in each tuple is the name to apply to the group. The
second element is an iterable of 2-tuples, with each 2-tuple containing
a value and a human-readable name for an option. Grouped options may be
combined with ungrouped options within a single list (such as the
`unknown` option in this example).

Finally, note that choices can be any iterable object -- not necessarily a list
or tuple. This lets you construct choices dynamically. But if you find yourself
hacking ``choices`` to be dynamic, you're probably better off using a
proper database table with a `ForeignKey``. ``choices`` is
meant for static data that doesn't change much, if ever.

db_column
---------

The name of the database column to use for this field. If this isn't given,
Django will use the field's name.

If your database column name is an SQL reserved word, or contains
characters that aren't allowed in Python variable names -- notably, the
hyphen -- that's OK. Django quotes column and table names behind the
scenes.

db_index
--------

If ``True``, ``django-admin.py sqlindexes`` will output a
``CREATE INDEX`` statement for this field.

db_tablespace
-------------

The name of the database tablespace to use for this field's index, if this field
is indexed. The default is the project's ``DEFAULT_INDEX_TABLESPACE``
setting, if set, or the ``db_tablespace`` of the model, if any. If
the backend doesn't support tablespaces, this option is ignored.

default
-------

The default value for the field. This can be a value or a callable object. If
callable it will be called every time a new object is created.

editable
--------

If ``False``, the field will not be editable in the admin or via forms
automatically generated from the model class. Default is ``True``.

help_text
---------

Extra "help" text to be displayed under the field on the object's admin form.
It's useful for documentation even if your object doesn't have an admin form.

Note that this value is *not* HTML-escaped when it's displayed in the admin
interface. This lets you include HTML in ``help_text`` if you so
desire. For example::

    help_text="Please use the following format: <em>YYYY-MM-DD</em>."

Alternatively you can use plain text and
``django.utils.html.escape()`` to escape any HTML special characters.

primary_key
-----------

If ``True``, this field is the primary key for the model.

If you don't specify ``primary_key=True`` for any fields in your model, Django
will automatically add an ``AutoField`` to hold the primary key, so you
don't need to set ``primary_key=True`` on any of your fields unless you want to
override the default primary-key behavior.

``primary_key=True`` implies ``null=False`` and ``unique=True``.
Only one primary key is allowed on an object.

unique
------

If ``True``, this field must be unique throughout the table.

This is enforced at the database level and at the level of forms created with
``ModelForm`` (including forms in the Django admin site). If
you try to save a model with a duplicate value in a ``unique``
field, an ``IntegrityError`` will be raised by the model's
``save`` method.

This option is valid on all field types except ``ManyToManyField``,
``FileField`` and ``ImageField``.

unique_for_date
---------------

Set this to the name of a ``DateField`` or ``DateTimeField`` to
require that this field be unique for the value of the date field.

For example, if you have a field ``title`` that has
``unique_for_date="pub_date"``, then Django wouldn't allow the entry of two
records with the same ``title`` and ``pub_date``.

This is enforced at the level of forms created with ``ModelForm`` (including
forms in the Django admin site) but not at the database level.

unique_for_month
----------------

Like ``unique_for_date``, but requires the field to be unique with
respect to the month.

unique_for_year
---------------

Like ``unique_for_date`` and ``unique_for_month``.

verbose_name
------------

A human-readable name for the field. If the verbose name isn't given, Django
will automatically create it using the field's attribute name, converting
underscores to spaces.

Relationships
=============

Clearly, the power of relational databases lies in relating tables to each
other. Django offers ways to define the three most common types of database
relationships: many-to-one, many-to-many, and one-to-one.

ForeignKey
----------

A many-to-one relationship. Requires a positional argument: the class to which
the model is related.

To create a recursive relationship -- an object that has a many-to-one
relationship with itself -- use ``models.ForeignKey('self')``.

If you need to create a relationship on a model that has not yet been defined,
you can use the name of the model, rather than the model object itself::

    class Car(models.Model):
        manufacturer = models.ForeignKey('Manufacturer')
        # ...

    class Manufacturer(models.Model):
        # ...

Note, however, that this only refers to models in the same ``models.py`` file.

To refer to models defined in another
application, you must instead explicitly specify the application label. For
example, if the ``Manufacturer`` model above is defined in another application
called ``production``, you'd need to use::

    class Car(models.Model):
        manufacturer = models.ForeignKey('production.Manufacturer')

Behind the scenes, Django appends ``"_id"`` to the field name to create its
database column name. In the above example, the database table for the ``Car``
model will have a ``manufacturer_id`` column. (You can change this explicitly by
specifying ``db_column``) However, your code should never have to
deal with the database column name, unless you write custom SQL. You'll always
deal with the field names of your model object.

``ForeignKey`` accepts an extra set of arguments -- all optional -- that
define the details of how the relation works.

``limit_choices_to``
    A dictionary of lookup arguments and values
    that limit the available admin choices for this object. Use this with
    functions from the Python ``datetime`` module to limit choices of objects by
    date. For example::

        limit_choices_to = {'pub_date__lte': datetime.now}

    only allows the choice of related objects with a ``pub_date`` before the
    current date/time to be chosen.

    ``limit_choices_to`` has no effect on the inline FormSets that are created
    to display related objects in the admin.

``related_name``
    The name to use for the relation from the related object back to this one.

``to_field``
    The field on the related object that the relation is to. By default, Django
    uses the primary key of the related object.

ManyToManyField
---------------

A many-to-many relationship. Requires a positional argument: the class to which
the model is related. This works exactly the same as it does for
``ForeignKey``, including all the options regarding recursive relationships
and lazy relationships.

Behind the scenes, Django creates an intermediary join table to represent the
many-to-many relationship. By default, this table name is generated using the
names of the two tables being joined. Since some databases don't support table
names above a certain length, these table names will be automatically
truncated to 64 characters and a uniqueness hash will be used. This means you
might see table names like ``author_books_9cdf4``; this is perfectly normal.
You can manually provide the name of the join table using the
``db_table`` option.

``ManyToManyField`` accepts an extra set of arguments -- all optional --
that control how the relationship functions.

``related_name``
    Same as ``related_name`` in ``ForeignKey``.

``limit_choices_to``
    Same as ``limit_choices_to`` in ``ForeignKey``.

    ``limit_choices_to`` has no effect when used on a ``ManyToManyField`` with a
    custom intermediate table specified using the
    ``through`` paramter.

``symmetrical``
    Only used in the definition of ManyToManyFields on self. Consider the
    following model::

        class Person(models.Model):
            friends = models.ManyToManyField("self")

    When Django processes this model, it identifies that it has a
    ``ManyToManyField`` on itself, and as a result, it doesn't add a
    ``person_set`` attribute to the ``Person`` class. Instead, the
    ``ManyToManyField`` is assumed to be symmetrical -- that is, if I am
    your friend, then you are my friend.

    If you do not want symmetry in many-to-many relationships with ``self``, set
    ``symmetrical`` to ``False``. This will force Django to
    add the descriptor for the reverse relationship, allowing
    ``ManyToManyField`` relationships to be non-symmetrical.

``through``
    Django will automatically generate a table to manage many-to-many
    relationships. However, if you want to manually specify the intermediary
    table, you can use the ``through`` option to specify
    the Django model that represents the intermediate table that you want to
    use.

    The most common use for this option is when you want to associate
    extra data with a many-to-many relationship.

``db_table``
    The name of the table to create for storing the many-to-many data. If this
    is not provided, Django will assume a default name based upon the names of
    the two tables being joined.

OneToOneField
-------------

A one-to-one relationship. Conceptually, this is similar to a
``ForeignKey`` with ``unique=True``, but the
"reverse" side of the relation will directly return a single object.

This is most useful as the primary key of a model which "extends"
another model in some way; multi-table-inheritance is
implemented by adding an implicit one-to-one relation from the child
model to the parent model, for example.

One positional argument is required: the class to which the model will be
related. This works exactly the same as it does for ``ForeignKey``,
including all the options regarding recursive relationships and lazy
relationships.

Additionally, ``OneToOneField`` accepts all of the extra arguments
accepted by ``ForeignKey``, plus one extra argument:

``parent_link``
    When ``True`` and used in a model which inherits from another
    (concrete) model, indicates that this field should be used as the
    link back to the parent class, rather than the extra
    ``OneToOneField`` which would normally be implicitly created by
    subclassing.

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

abstract
--------

If ``True``, this model will be an abstract base class. See the Django
documentation for more on abstract base classes.

db_table
--------

The name of the database table to use for the model::

    db_table = 'music_album'

Table names
~~~~~~~~~~~

To save you time, Django automatically derives the name of the database table
from the name of your model class and the app that contains it. A model's
database table name is constructed by joining the model's "app label" -- the
name you used in ``manage.py startapp`` -- to the model's class name, with an
underscore between them.

For example, if you have an app ``bookstore`` (as created by
``manage.py startapp bookstore``), a model defined as ``class Book`` will have
a database table named ``bookstore_book``.

To override the database table name, use the ``db_table`` parameter in
``class Meta``.

If your database table name is an SQL reserved word, or contains characters that
aren't allowed in Python variable names -- notably, the hyphen -- that's OK.
Django quotes column and table names behind the scenes.

db_tablespace
-------------

The name of the database tablespace to use for the model. If the backend doesn't
support tablespaces, this option is ignored.

get_latest_by
-------------

The name of a ``DateField`` or ``DateTimeField`` in the model. This
specifies the default field to use in your model ``Manager``'s
``latest`` method.

Example::

    get_latest_by = "order_date"

managed
-------

Defaults to ``True``, meaning Django will create the appropriate database
tables in ``django-admin.py syncdb`` and remove them as part of a ``reset``
management command. That is, Django *manages* the database tables' lifecycles.

If ``False``, no database table creation or deletion operations will be
performed for this model. This is useful if the model represents an existing
table or a database view that has been created by some other means. This is
the *only* difference when ``managed`` is ``False``. All other aspects of
model handling are exactly the same as normal. This includes

1. Adding an automatic primary key field to the model if you don't declare
   it. To avoid confusion for later code readers, it's recommended to
   specify all the columns from the database table you are modeling when
   using unmanaged models.

2. If a model with ``managed=False`` contains a
   ``ManyToManyField`` that points to another
   unmanaged model, then the intermediary table for the many-to-many join
   will also not be created. However, the intermediary table between one
   managed and one unmanaged model *will* be created.

   If you need to change this default behavior, create the intermediary
   table as an explicit model (with ``managed`` set as needed) and use the
   ``through`` attribute to make the relation use your
   custom model.

For tests involving models with ``managed=False``, it's up to you to ensure
the correct tables are created as part of the test setup.

If you're interested in changing the Python-level behavior of a model class,
you *could* use ``managed=False`` and create a copy of an existing model.
However, there's a better approach for that situation: proxy-models.

ordering
--------

The default ordering for the object, for use when obtaining lists of objects::

    ordering = ['-order_date']

This is a tuple or list of strings. Each string is a field name with an optional
"-" prefix, which indicates descending order. Fields without a leading "-" will
be ordered ascending. Use the string "?" to order randomly.

.. note::

    Regardless of how many fields are in ``ordering``, the admin
    site uses only the first field.

For example, to order by a ``pub_date`` field ascending, use this::

    ordering = ['pub_date']

To order by ``pub_date`` descending, use this::

    ordering = ['-pub_date']

To order by ``pub_date`` descending, then by ``author`` ascending, use this::

    ordering = ['-pub_date', 'author']

proxy
-----

If set to ``True``, a model which subclasses another model will be treated as
a proxy model. For more on proxy models, see the Django documentation.

unique_together
---------------

Sets of field names that, taken together, must be unique::

    unique_together = (("driver", "restaurant"),)

This is a list of lists of fields that must be unique when considered together.
It's used by ``ModelForm`` forms (including forms in the Django admin site) and
is enforced at the database level (i.e., the appropriate ``UNIQUE`` statements
are included in the ``CREATE TABLE`` statement).

For convenience, unique_together can be a single sequence when dealing with a single
set of fields::

    unique_together = ("driver", "restaurant")

verbose_name
------------

A human-readable name for the object, singular::

    verbose_name = "pizza"

If this isn't given, Django will use a munged version of the class name:
``CamelCase`` becomes ``camel case``.

verbose_name_plural
-------------------

The plural name for the object::

    verbose_name_plural = "stories"

If this isn't given, Django will use ``verbose_name`` + ``"s"``.