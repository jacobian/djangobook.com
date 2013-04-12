==================================
Appendix B: Database API Reference
==================================

Django's database API is the other half of the model API discussed in Appendix
A. Once you've defined a model, you'll use this API any time you need to
access the database. You've seen examples of this API in use throughout the
book; this appendix explains all the various options in detail.

Like the model APIs discussed in Appendix A, though these APIs are considered
very stable, the Django developers consistently add new shortcuts and
conveniences. It's a good idea to always check the latest documentation online,
available at http://docs.djangoproject.com/.

Throughout this reference, we'll refer to the following models, which might form
a simple blog application::

    from django.db import models

    class Blog(models.Model):
        name = models.CharField(max_length=100)
        tagline = models.TextField()

        def __unicode__(self):
            return self.name

    class Author(models.Model):
        name = models.CharField(max_length=50)
        email = models.EmailField()

        def __unicode__(self):
            return self.name

    class Entry(models.Model):
        blog = models.ForeignKey(Blog)
        headline = models.CharField(max_length=255)
        body_text = models.TextField()
        pub_date = models.DateTimeField()
        authors = models.ManyToManyField(Author)

        def __unicode__(self):
            return self.headline

Creating Objects
================

To create an object, instantiate it using keyword arguments to the model class, and
then call ``save()`` to save it to the database::

    >>> from mysite.blog.models import Blog
    >>> b = Blog(name='Beatles Blog', tagline='All the latest Beatles news.')
    >>> b.save()

This performs an ``INSERT`` SQL statement behind the scenes. Django doesn't hit
the database until you explicitly call ``save()``.

The ``save()`` method has no return value.

To create an object and save it all in one step, see the ``create`` manager
method.

What Happens When You Save?
---------------------------

When you save an object, Django performs the following steps:

#. **Emit a pre_save signal.** This provides a notification that
   an object is about to be saved. You can register a listener that
   will be invoked whenever this signal is emitted. Check the online
   documentation for more on signals.

#. **Preprocess the data.** Each field on the object is asked to
   perform any automated data modification that the field may need
   to perform.

   Most fields do *no* preprocessing -- the field data is kept as is.
   Preprocessing is only used on fields that have special behavior,
   like file fields.

#. **Prepare the data for the database.** Each field is asked to provide
   its current value in a data type that can be written to the database.

   Most fields require no data preparation. Simple data types, such as
   integers and strings, are "ready to write" as a Python object. However,
   more complex data types often require some modification. For example,
   ``DateFields`` use a Python ``datetime`` object to store data.
   Databases don't store ``datetime`` objects, so the field value
   must be converted into an ISO-compliant date string for insertion
   into the database.

#. **Insert the data into the database.** The preprocessed, prepared
   data is then composed into an SQL statement for insertion into the
   database.

#. **Emit a post_save signal.** As with the ``pre_save`` signal, this
   is used to provide notification that an object has been successfully
   saved.

Autoincrementing Primary Keys
------------------------------

For convenience, each model is given an autoincrementing primary key field
named ``id`` unless you explicitly specify ``primary_key=True`` on a field (see
the section titled "AutoField" in Appendix A).

If your model has an ``AutoField``, that autoincremented value will be
calculated and saved as an attribute on your object the first time you call
``save()``::

    >>> b2 = Blog(name='Cheddar Talk', tagline='Thoughts on cheese.')
    >>> b2.id     # Returns None, because b doesn't have an ID yet.
    None

    >>> b2.save()
    >>> b2.id     # Returns the ID of your new object.
    14

There's no way to tell what the value of an ID will be before you call
``save()``, because that value is calculated by your database, not by Django.

If a model has an ``AutoField`` but you want to define a new object's ID
explicitly when saving, just define it explicitly before saving, rather than
relying on the autoassignment of the ID::

    >>> b3 = Blog(id=3, name='Cheddar Talk', tagline='Thoughts on cheese.')
    >>> b3.id
    3
    >>> b3.save()
    >>> b3.id
    3

If you assign auto-primary-key values manually, make sure not to use an
already existing primary key value! If you create a new object with an explicit
primary key value that already exists in the database, Django will assume you're
changing the existing record rather than creating a new one.

Given the preceding ``'Cheddar Talk'`` blog example, this example would override the
previous record in the database::

    >>> b4 = Blog(id=3, name='Not Cheddar', tagline='Anything but cheese.')
    >>> b4.save()  # Overrides the previous blog with ID=3!

Explicitly specifying auto-primary-key values is mostly useful for bulk-saving
objects, when you're confident you won't have primary key collision.

Saving Changes to Objects
=========================

To save changes to an object that's already in the database, use ``save()``.

Given a ``Blog`` instance ``b5`` that has already been saved to the database,
this example changes its name and updates its record in the database::

    >>> b5.name = 'New name'
    >>> b5.save()

This performs an ``UPDATE`` SQL statement behind the scenes. Again, Django
doesn't hit the database until you explicitly call ``save()``.

.. admonition:: How Django Knows When to ``UPDATE`` and When to ``INSERT``

    You may have noticed that Django database objects use the same ``save()`` method
    for creating and changing objects. Django abstracts the need to use
    ``INSERT`` or ``UPDATE`` SQL statements. Specifically, when you call
    ``save()``, Django follows this algorithm:

    * If the object's primary key attribute is set to a value that evaluates
      to ``True`` (i.e., a value other than ``None`` or the empty string),
      Django executes a ``SELECT`` query to determine whether a record with
      the given primary key already exists.

    * If the record with the given primary key does already exist, Django
      executes an ``UPDATE`` query.

    * If the object's primary key attribute is *not* set, or if it's set but
      a record doesn't exist, Django executes an ``INSERT``.

    Because of this, you should be careful not to specify a primary key value
    explicitly when saving new objects if you cannot guarantee the primary key
    value is unused.

Updating ``ForeignKey`` fields works exactly the same way; simply assign an
object of the right type to the field in question::

    >>> joe = Author.objects.create(name="Joe")
    >>> entry.author = joe
    >>> entry.save()

Django will complain if you try to assign an object of the wrong type.

Retrieving Objects
==================

Throughout the book you've seen objects retrieved using code like the following::

    >>> blogs = Blog.objects.filter(author__name__contains="Joe")

There are quite a few "moving parts" behind the scenes here: when you
retrieve objects from the database, you're actually constructing a ``QuerySet``
using the model's ``Manager``. This ``QuerySet`` knows how to execute SQL and
return the requested objects.

Appendix A looked at both of these objects from a model-definition point of
view; now we'll look at how they operate.

A ``QuerySet`` represents a collection of objects from your database. It can
have zero, one, or many *filters* -- criteria that narrow down the collection
based on given parameters. In SQL terms, a ``QuerySet`` equates to a ``SELECT``
statement, and a filter is a ``WHERE``.

You get a ``QuerySet`` by using your model's ``Manager``. Each model has at
least one ``Manager``, and it's called ``objects`` by default. Access it
directly via the model class, like so::

    >>> Blog.objects
    <django.db.models.manager.Manager object at 0x137d00d>

``Manager``\s are accessible only via model classes, rather than from model
instances, to enforce a separation between "table-level" operations and
"record-level" operations::

    >>> b = Blog(name='Foo', tagline='Bar')
    >>> b.objects
    Traceback (most recent call last):
      File "<stdin>", line 1, in <module>
    AttributeError: Manager isn't accessible via Blog instances.

The ``Manager`` is the main source of ``QuerySet``\s for a model. It acts as a
"root" ``QuerySet`` that describes all objects in the model's database table.
For example, ``Blog.objects`` is the initial ``QuerySet`` that contains all
``Blog`` objects in the database.

Caching and QuerySets
=====================

Each ``QuerySet`` contains a cache, to minimize database access. It's important
to understand how it works, in order to write the most efficient code.

In a newly created ``QuerySet``, the cache is empty. The first time a
``QuerySet`` is evaluated -- and, hence, a database query happens -- Django
saves the query results in the ``QuerySet``'s cache and returns the results
that have been explicitly requested (e.g., the next element, if the
``QuerySet`` is being iterated over). Subsequent evaluations of the
``QuerySet`` reuse the cached results.

Keep this caching behavior in mind, because it may bite you if you don't use
your ``QuerySet``\s correctly. For example, the following will create two
``QuerySet``\s, evaluate them, and throw them away::

    print [e.headline for e in Entry.objects.all()]
    print [e.pub_date for e in Entry.objects.all()]

That means the same database query will be executed twice, effectively doubling
your database load. Also, there's a possibility the two lists may not include
the same database records, because an ``Entry`` may have been added or deleted
in the split second between the two requests.

To avoid this problem, simply save the ``QuerySet`` and reuse it::

    queryset = Poll.objects.all()
    print [p.headline for p in queryset] # Evaluate the query set.
    print [p.pub_date for p in queryset] # Reuse the cache from the evaluation.

Filtering Objects
=================

The simplest way to retrieve objects from a table is to get all of them.
To do this, use the ``all()`` method on a ``Manager``::

    >>> Entry.objects.all()

The ``all()`` method returns a ``QuerySet`` of all the objects in the database.

Usually, though, you'll need to select only a subset of the complete set of
objects. To create such a subset, you refine the initial ``QuerySet``, adding filter
conditions. You'll usually do this using the ``filter()`` and/or ``exclude()``
methods::

    >>> y2006 = Entry.objects.filter(pub_date__year=2006)
    >>> not2006 = Entry.objects.exclude(pub_date__year=2006)

``filter()`` and ``exclude()`` both take *field lookup* arguments, which are
discussed in detail shortly.

Chaining Filters
----------------

The result of refining a ``QuerySet`` is itself a ``QuerySet``, so it's
possible to chain refinements together, for example::

    >>> qs = Entry.objects.filter(headline__startswith='What')
    >>> qs = qs.exclude(pub_date__gte=datetime.datetime.now())
    >>> qs = qs.filter(pub_date__gte=datetime.datetime(2005, 1, 1))

This takes the initial ``QuerySet`` of all entries in the database, adds a
filter, then an exclusion, and then another filter. The final result is a
``QuerySet`` containing all entries with a headline that starts with "What"
that were published between January 1, 2005, and the current day.

It's important to point out here that ``QuerySets`` are lazy -- the act of creating
a ``QuerySet`` doesn't involve any database activity. In fact, the three preceding lines
don't make *any* database calls; you can chain filters together all day
long and Django won't actually run the query until the ``QuerySet`` is
*evaluated*.

You can evaluate a ``QuerySet`` in any following ways:

* *Iterating*: A ``QuerySet`` is iterable, and it executes its database query the first
  time you iterate over it. For example, the following ``QuerySet`` isn't evaluated
  until it's iterated over in the ``for`` loop::

      qs = Entry.objects.filter(pub_date__year=2006)
      qs = qs.filter(headline__icontains="bill")
      for e in qs:
          print e.headline

  This prints all headlines from 2006 that contain "bill" but causes
  only one database hit.

* *Printing it*: A ``QuerySet`` is evaluated when you call ``repr()`` on it.
  This is for convenience in the Python interactive interpreter, so you can
  immediately see your results when using the API interactively.

* *Slicing*: As explained in the upcoming "Limiting QuerySets" section,
  a ``QuerySet`` can be sliced using Python's array-slicing syntax.
  Usually slicing a ``QuerySet`` returns another (unevaluated)``QuerySet``,
  but Django will execute the database query if you use the "step"
  parameter of slice syntax.

* *Converting to a list*: You can force evaluation of a ``QuerySet`` by calling
  ``list()`` on it, for example::

      >>> entry_list = list(Entry.objects.all())

  Be warned, though, that this could have a large memory overhead, because
  Django will load each element of the list into memory. In contrast,
  iterating over a ``QuerySet`` will take advantage of your database to load
  data and instantiate objects only as you need them.

.. admonition:: Filtered QuerySets Are Unique

    Each time you refine a ``QuerySet``, you get a brand-new ``QuerySet`` that
    is in no way bound to the previous ``QuerySet``. Each refinement creates a
    separate and distinct ``QuerySet`` that can be stored, used, and reused::

        q1 = Entry.objects.filter(headline__startswith="What")
        q2 = q1.exclude(pub_date__gte=datetime.now())
        q3 = q1.filter(pub_date__gte=datetime.now())

    These three ``QuerySets`` are separate. The first is a base ``QuerySet``
    containing all entries that contain a headline starting with "What". The
    second is a subset of the first, with an additional criterion that excludes
    records whose ``pub_date`` is greater than now. The third is a subset of the
    first, with an additional criterion that selects only the records whose
    ``pub_date`` is greater than now. The initial ``QuerySet`` (``q1``) is
    unaffected by the refinement process.

Limiting QuerySets
------------------

Use Python's array-slicing syntax to limit your ``QuerySet`` to a certain number
of results. This is the equivalent of SQL's ``LIMIT`` and ``OFFSET`` clauses.

For example, this returns the first five entries (``LIMIT 5``)::

    >>> Entry.objects.all()[:5]

This returns the sixth through tenth entries (``OFFSET 5 LIMIT 5``)::

    >>> Entry.objects.all()[5:10]

Generally, slicing a ``QuerySet`` returns a new ``QuerySet`` -- it doesn't
evaluate the query. An exception is if you use the "step" parameter
of Python slice syntax. For example, this would actually execute the query in
order to return a list of every *second* object of the first ten::

    >>> Entry.objects.all()[:10:2]

To retrieve a *single* object rather than a list (e.g., ``SELECT foo FROM bar
LIMIT 1``), use a simple index instead of a slice. For example, this returns the
first ``Entry`` in the database, after ordering entries alphabetically by
headline::

    >>> Entry.objects.order_by('headline')[0]

This is roughly equivalent to the following::

    >>> Entry.objects.order_by('headline')[0:1].get()

Note, however, that the first of these will raise ``IndexError`` while the
second will raise ``DoesNotExist`` if no objects match the given criteria.

Query Methods That Return New QuerySets
---------------------------------------

Django provides a range of ``QuerySet`` refinement methods that modify either
the types of results returned by the ``QuerySet`` or the way its SQL query is
executed. These methods are described in the sections that follow. Some of the
methods take field lookup arguments, which are discussed in detail a bit later
on.

filter(\*\*lookup)
~~~~~~~~~~~~~~~~~~

Returns a new ``QuerySet`` containing objects that match the given lookup
parameters.

exclude(\*\*lookup)
~~~~~~~~~~~~~~~~~~~

Returns a new ``QuerySet`` containing objects that do *not* match the given
lookup parameters.

order_by(\*fields)
~~~~~~~~~~~~~~~~~~

By default, results returned by a ``QuerySet`` are ordered by the ordering
tuple given by the ``ordering`` option in the model's metadata (see Appendix A). You can
override this for a particular query using the ``order_by()`` method::

    >> Entry.objects.filter(pub_date__year=2005).order_by('-pub_date', 'headline')

This result will be ordered by ``pub_date`` descending, then by
``headline`` ascending. The negative sign in front of ``"-pub_date"`` indicates
*descending* order. Ascending order is assumed if the ``-`` is absent. To order
randomly, use ``"?"``, like so::

    >>> Entry.objects.order_by('?')

Ordering randomly incurs a performance penalty, though, so you shouldn't use it
for anything with heavy load.

If no ordering is specified in a model's ``class Meta`` and a ``QuerySet`` from
that model doesn't include ``order_by()``, then ordering will be undefined and
may differ from query to query.

distinct()
~~~~~~~~~~

Returns a new ``QuerySet`` that uses ``SELECT DISTINCT`` in its SQL query. This
eliminates duplicate rows from the query results.

By default, a ``QuerySet`` will not eliminate duplicate rows. In practice, this
is rarely a problem, because simple queries such as ``Blog.objects.all()`` don't
introduce the possibility of duplicate result rows.

However, if your query spans multiple tables, it's possible to get duplicate
results when a ``QuerySet`` is evaluated. That's when you'd use ``distinct()``.

values(\*fields)
~~~~~~~~~~~~~~~~

Returns a special ``QuerySet`` that evaluates to a list of dictionaries instead
of model-instance objects. Each of those dictionaries represents an object, with
the keys corresponding to the attribute names of model objects::

    # This list contains a Blog object.
    >>> Blog.objects.filter(name__startswith='Beatles')
    [Beatles Blog]

    # This list contains a dictionary.
    >>> Blog.objects.filter(name__startswith='Beatles').values()
    [{'id': 1, 'name': 'Beatles Blog', 'tagline': 'All the latest Beatles news.'}]

``values()`` takes optional positional arguments, ``*fields``, which specify
field names to which the ``SELECT`` should be limited. If you specify the
fields, each dictionary will contain only the field keys/values for the fields
you specify. If you don't specify the fields, each dictionary will contain a
key and value for every field in the database table::

    >>> Blog.objects.values()
    [{'id': 1, 'name': 'Beatles Blog', 'tagline': 'All the latest Beatles news.'}],
    >>> Blog.objects.values('id', 'name')
    [{'id': 1, 'name': 'Beatles Blog'}]

This method is useful when you know you're only going to need values from a
small number of the available fields and you won't need the functionality of a
model instance object. It's more efficient to select only the fields you need to
use.

dates(field, kind, order)
~~~~~~~~~~~~~~~~~~~~~~~~~

Returns a special ``QuerySet`` that evaluates to a list of ``datetime.datetime``
objects representing all available dates of a particular kind within the
contents of the ``QuerySet``.

The ``field`` argument must be the name of a ``DateField`` or ``DateTimeField``
of your model. The ``kind`` argument must be either ``"year"``, ``"month"``, or
``"day"``. Each ``datetime.datetime`` object in the result list is "truncated"
to the given ``type``:

* ``"year"`` returns a list of all distinct year values for the field.

* ``"month"`` returns a list of all distinct year/month values for the field.

* ``"day"`` returns a list of all distinct year/month/day values for the field.

``order``, which defaults to ``'ASC'``, should be either ``'ASC'`` or
``'DESC'``. This specifies how to order the results.

Here are a few examples::

    >>> Entry.objects.dates('pub_date', 'year')
    [datetime.datetime(2005, 1, 1)]

    >>> Entry.objects.dates('pub_date', 'month')
    [datetime.datetime(2005, 2, 1), datetime.datetime(2005, 3, 1)]

    >>> Entry.objects.dates('pub_date', 'day')
    [datetime.datetime(2005, 2, 20), datetime.datetime(2005, 3, 20)]

    >>> Entry.objects.dates('pub_date', 'day', order='DESC')
    [datetime.datetime(2005, 3, 20), datetime.datetime(2005, 2, 20)]

    >>> Entry.objects.filter(headline__contains='Lennon').dates('pub_date', 'day')
    [datetime.datetime(2005, 3, 20)]

select_related()
~~~~~~~~~~~~~~~~

Returns a ``QuerySet`` that will automatically "follow" foreign key
relationships, selecting that additional related-object data when it executes
its query. This is a performance booster that results in (sometimes much)
larger queries but means later use of foreign key relationships won't require
database queries.

The following examples illustrate the difference between plain lookups and
``select_related()`` lookups. Here's standard lookup::

    # Hits the database.
    >>> e = Entry.objects.get(id=5)

    # Hits the database again to get the related Blog object.
    >>> b = e.blog

And here's ``select_related`` lookup::

    # Hits the database.
    >>> e = Entry.objects.select_related().get(id=5)

    # Doesn't hit the database, because e.blog has been prepopulated
    # in the previous query.
    >>> b = e.blog

``select_related()`` follows foreign keys as far as possible. If you have the
following models::

    class City(models.Model):
        # ...

    class Person(models.Model):
        # ...
        hometown = models.ForeignKey(City)

    class Book(models.Model):
        # ...
        author = models.ForeignKey(Person)

then a call to ``Book.objects.select_related().get(id=4)`` will cache the
related ``Person`` *and* the related ``City``::

    >>> b = Book.objects.select_related().get(id=4)
    >>> p = b.author         # Doesn't hit the database.
    >>> c = p.hometown       # Doesn't hit the database.

    >>> b = Book.objects.get(id=4) # No select_related() in this example.
    >>> p = b.author         # Hits the database.
    >>> c = p.hometown       # Hits the database.

Note that ``select_related()`` does not follow foreign keys that have
``null=True``.

Usually, using ``select_related()`` can vastly improve performance because your
application can avoid many database calls. However, in situations with deeply nested
sets of relationships, ``select_related()`` can sometimes end up following "too
many" relations and can generate queries so large that they end up being slow.

QuerySet Methods That Do Not Return QuerySets
---------------------------------------------

The following ``QuerySet`` methods evaluate the ``QuerySet`` and return
something *other than* a ``QuerySet`` -- a single object, value, and so forth.

get(\*\*lookup)
~~~~~~~~~~~~~~~

Returns the object matching the given lookup parameters, which should be in the
format described in the "Field Lookups" section. This raises ``AssertionError`` if
more than one object was found.

``get()`` raises a ``DoesNotExist`` exception if an object wasn't found for the
given parameters. The ``DoesNotExist`` exception is an attribute of the model
class, for example::

    >>> Entry.objects.get(id='foo') # raises Entry.DoesNotExist

The ``DoesNotExist`` exception inherits from
``django.core.exceptions.ObjectDoesNotExist``, so you can target multiple
``DoesNotExist`` exceptions::

    >>> from django.core.exceptions import ObjectDoesNotExist
    >>> try:
    ...     e = Entry.objects.get(id=3)
    ...     b = Blog.objects.get(id=1)
    ... except ObjectDoesNotExist:
    ...     print "Either the entry or blog doesn't exist."

create(\*\*kwargs)
~~~~~~~~~~~~~~~~~~

This is a convenience method for creating an object and saving it all in one step.
It lets you compress two common steps::

    >>> p = Person(first_name="Bruce", last_name="Springsteen")
    >>> p.save()

into a single line::

    >>> p = Person.objects.create(first_name="Bruce", last_name="Springsteen")

get_or_create(\*\*kwargs)
~~~~~~~~~~~~~~~~~~~~~~~~~

This is a convenience method for looking up an object and creating one if it doesn't
exist. It returns a tuple of ``(object, created)``, where ``object`` is the retrieved or
created object and ``created`` is a Boolean specifying whether a new object was
created.

This method is meant as a shortcut to boilerplate code and is mostly useful for
data-import scripts. For example::

    try:
        obj = Person.objects.get(first_name='John', last_name='Lennon')
    except Person.DoesNotExist:
        obj = Person(first_name='John', last_name='Lennon', birthday=date(1940, 10, 9))
        obj.save()

This pattern gets quite unwieldy as the number of fields in a model increases. The
previous example can be rewritten using ``get_or_create()`` like so::

    obj, created = Person.objects.get_or_create(
        first_name = 'John',
        last_name  = 'Lennon',
        defaults   = {'birthday': date(1940, 10, 9)}
    )

Any keyword arguments passed to ``get_or_create()`` -- *except* an optional one
called ``defaults`` -- will be used in a ``get()`` call. If an object is found,
``get_or_create()`` returns a tuple of that object and ``False``. If an object
is *not* found, ``get_or_create()`` will instantiate and save a new object,
returning a tuple of the new object and ``True``. The new object will be created
according to this algorithm::

    defaults = kwargs.pop('defaults', {})
    params = dict([(k, v) for k, v in kwargs.items() if '__' not in k])
    params.update(defaults)
    obj = self.model(**params)
    obj.save()

In English, that means start with any non-``'defaults'`` keyword argument that
doesn't contain a double underscore (which would indicate a nonexact lookup).
Then add the contents of ``defaults``, overriding any keys if necessary, and
use the result as the keyword arguments to the model class.

If you have a field named ``defaults`` and want to use it as an exact lookup in
``get_or_create()``, just use ``'defaults__exact'`` like so::

    Foo.objects.get_or_create(
        defaults__exact = 'bar',
        defaults={'defaults': 'bar'}
    )

.. note::

    As mentioned earlier, ``get_or_create()`` is mostly useful in scripts that
    need to parse data and create new records if existing ones aren't available.
    But if you need to use ``get_or_create()`` in a view, please make sure to
    use it only in ``POST`` requests unless you have a good reason not to.
    ``GET`` requests shouldn't have any effect on data; use ``POST`` whenever a
    request to a page has a side effect on your data.

count()
~~~~~~~

Returns an integer representing the number of objects in the database matching
the ``QuerySet``. ``count()`` never raises exceptions. Here's an example::

    # Returns the total number of entries in the database.
    >>> Entry.objects.count()
    4

    # Returns the number of entries whose headline contains 'Lennon'
    >>> Entry.objects.filter(headline__contains='Lennon').count()
    1

``count()`` performs a ``SELECT COUNT(*)`` behind the scenes, so you should
always use ``count()`` rather than loading all of the records into Python objects
and calling ``len()`` on the result.

Depending on which database you're using (e.g., PostgreSQL or MySQL),
``count()`` may return a long integer instead of a normal Python integer. This
is an underlying implementation quirk that shouldn't pose any real-world
problems.

in_bulk(id_list)
~~~~~~~~~~~~~~~~

Takes a list of primary key values and returns a dictionary mapping each
primary key value to an instance of the object with the given ID, for example::

    >>> Blog.objects.in_bulk([1])
    {1: Beatles Blog}
    >>> Blog.objects.in_bulk([1, 2])
    {1: Beatles Blog, 2: Cheddar Talk}
    >>> Blog.objects.in_bulk([])
    {}

IDs of objects that don't exist are silently dropped from the result dictionary.
If you pass ``in_bulk()`` an empty list, you'll get an empty dictionary.

latest(field_name=None)
~~~~~~~~~~~~~~~~~~~~~~~

Returns the latest object in the table, by date, using the ``field_name``
provided as the date field. This example returns the latest ``Entry`` in the
table, according to the ``pub_date`` field::

    >>> Entry.objects.latest('pub_date')

If your model's ``Meta`` specifies ``get_latest_by``, you can leave off the
``field_name`` argument to ``latest()``. Django will use the field specified in
``get_latest_by`` by default.

Like ``get()``, ``latest()`` raises ``DoesNotExist`` if an object doesn't exist
with the given parameters.

Field Lookups
=============

Field lookups are how you specify the meat of an SQL ``WHERE`` clause. They're
specified as keyword arguments to the ``QuerySet`` methods ``filter()``,
``exclude()``, and ``get()``.

Basic lookup keyword arguments take the form ``field__lookuptype=value``
(note the double underscore). For example::

    >>> Entry.objects.filter(pub_date__lte='2006-01-01')

translates (roughly) into the following SQL::

    SELECT * FROM blog_entry WHERE pub_date <= '2006-01-01';

If you pass an invalid keyword argument, a lookup function will raise
``TypeError``.

The supported lookup types follow.

exact
-----

Performs an exact match::

    >>> Entry.objects.get(headline__exact="Man bites dog")

This matches any object with the exact headline "Man bites dog".

If you don't provide a lookup type -- that is, if your keyword argument doesn't
contain a double underscore -- the lookup type is assumed to be ``exact``.

For example, the following two statements are equivalent::

    >>> Blog.objects.get(id__exact=14) # Explicit form
    >>> Blog.objects.get(id=14) # __exact is implied

This is for convenience, because ``exact`` lookups are the common case.

iexact
------

Performs a case-insensitive exact match::

    >>> Blog.objects.get(name__iexact='beatles blog')

This will match ``'Beatles Blog'``, ``'beatles blog'``,
``'BeAtLes BLoG'``, and so forth.

contains
--------

Performs a case-sensitive containment test::

    Entry.objects.get(headline__contains='Lennon')

This will match the headline ``'Today Lennon honored'`` but not
``'today lennon honored'``.

SQLite doesn't support case-sensitive ``LIKE`` statements; when using
SQLite,``contains`` acts like ``icontains``.

.. admonition:: Escaping Percent Signs and Underscores in LIKE Statements

    The field lookups that equate to ``LIKE`` SQL statements (``iexact``,
    ``contains``, ``icontains``, ``startswith``, ``istartswith``, ``endswith``,
    and ``iendswith``) will automatically escape the two special characters used in
    ``LIKE`` statements -- the percent sign and the underscore. (In a ``LIKE``
    statement, the percent sign signifies a multiple-character wildcard and the
    underscore signifies a single-character wildcard.)

    This means things should work intuitively, so the abstraction doesn't leak.
    For example, to retrieve all the entries that contain a percent sign, just use
    the percent sign as any other character::

        Entry.objects.filter(headline__contains='%')

    Django takes care of the quoting for you. The resulting SQL will look something
    like this::

        SELECT ... WHERE headline LIKE '%\%%';

    The same goes for underscores. Both percentage signs and underscores are handled
    for you transparently.

icontains
---------

Performs a case-insensitive containment test::

    >>> Entry.objects.get(headline__icontains='Lennon')

Unlike ``contains``, ``icontains`` *will* match ``'today lennon honored'``.

gt, gte, lt, and lte
--------------------

These represent greater than, greater than or equal to, less than, and less
than or equal to::

    >>> Entry.objects.filter(id__gt=4)
    >>> Entry.objects.filter(id__lt=15)
    >>> Entry.objects.filter(id__gte=0)

These queries return any object with an ID greater than 4, an ID less than 15,
and an ID greater than or equal to 1, respectively.

You'll usually use these on numeric fields. Be careful with character fields
since character order isn't always what you'd expect (i.e., the string "4" sorts
*after* the string "10").

in
--

Filters where a value is on a given list::

    Entry.objects.filter(id__in=[1, 3, 4])

This returns all objects with the ID 1, 3, or 4.

startswith
----------

Performs a case-sensitive starts-with::

    >>> Entry.objects.filter(headline__startswith='Will')

This will return the headlines "Will he run?" and "Willbur named judge", but not
"Who is Will?" or "will found in crypt".

istartswith
-----------

Performs a case-insensitive starts-with::

    >>> Entry.objects.filter(headline__istartswith='will')

This will return the headlines "Will he run?", "Willbur named judge", and
"will found in crypt", but not "Who is Will?"

endswith and iendswith
----------------------

Perform case-sensitive and case-insensitive ends-with::

    >>> Entry.objects.filter(headline__endswith='cats')
    >>> Entry.objects.filter(headline__iendswith='cats')

Similar to ``startswith`` and ``istartswith``.

range
-----

Performs an inclusive range check::

    >>> start_date = datetime.date(2005, 1, 1)
    >>> end_date = datetime.date(2005, 3, 31)
    >>> Entry.objects.filter(pub_date__range=(start_date, end_date))

You can use ``range`` anywhere you can use ``BETWEEN`` in SQL -- for dates,
numbers, and even characters.

year, month, and day
--------------------

For date/datetime fields, perform exact year, month, or day matches::

    # Return all entries published in 2005
    >>>Entry.objects.filter(pub_date__year=2005)

    # Return all entries published in December
    >>> Entry.objects.filter(pub_date__month=12)

    # Return all entries published on the 3rd of the month
    >>> Entry.objects.filter(pub_date__day=3)

    # Combination: return all entries on Christmas of any year
    >>> Entry.objects.filter(pub_date__month=12, pub_date_day=25)

isnull
------

Takes either ``True`` or ``False``, which correspond to SQL queries of
``IS NULL`` and ``IS NOT NULL``, respectively::

    >>> Entry.objects.filter(pub_date__isnull=True)

search
------

A Boolean full-text search that takes advantage of full-text indexing. This is like
``contains`` but is significantly faster due to full-text indexing.

Note this is available only in MySQL and requires direct manipulation of the
database to add the full-text index.

The pk Lookup Shortcut
----------------------

For convenience, Django provides a ``pk`` lookup type, which stands for
"primary_key".

In the example ``Blog`` model, the primary key is the ``id`` field, so these
three statements are equivalent::

    >>> Blog.objects.get(id__exact=14) # Explicit form
    >>> Blog.objects.get(id=14) # __exact is implied
    >>> Blog.objects.get(pk=14) # pk implies id__exact

The use of ``pk`` isn't limited to ``__exact`` queries -- any query term can be
combined with ``pk`` to perform a query on the primary key of a model::

    # Get blogs entries  with id 1, 4, and 7
    >>> Blog.objects.filter(pk__in=[1,4,7])

    # Get all blog entries with id > 14
    >>> Blog.objects.filter(pk__gt=14)

``pk`` lookups also work across joins. For example, these three statements are
equivalent::

    >>> Entry.objects.filter(blog__id__exact=3) # Explicit form
    >>> Entry.objects.filter(blog__id=3) # __exact is implied
    >>> Entry.objects.filter(blog__pk=3) # __pk implies __id__exact

The point of ``pk`` is to give you a generic way to refer to the primary key in
cases where you're not sure whether the model's primary key is called ``id``.

Complex Lookups with Q Objects
==============================

Keyword argument queries -- in ``filter()`` and so on -- are ANDed together. If
you need to execute more complex queries (e.g., queries with ``OR``
statements), you can use ``Q`` objects.

A ``Q`` object (``django.db.models.Q``) is an object used to encapsulate a
collection of keyword arguments. These keyword arguments are specified as in
the "Field Lookups" section.

For example, this ``Q`` object encapsulates a single ``LIKE`` query::

    Q(question__startswith='What')

``Q`` objects can be combined using the ``&`` and ``|`` operators. When an
operator is used on two ``Q`` objects, it yields a new ``Q`` object. For example,
this statement yields a single ``Q`` object that represents the
OR of two ``"question__startswith"`` queries::

    Q(question__startswith='Who') | Q(question__startswith='What')

This is equivalent to the following SQL ``WHERE`` clause::

    WHERE question LIKE 'Who%' OR question LIKE 'What%'

You can compose statements of arbitrary complexity by combining ``Q`` objects
with the ``&`` and ``|`` operators. You can also use parenthetical grouping.

Each lookup function that takes keyword arguments (e.g., ``filter()``,
``exclude()``, ``get()``) can also be passed one or more ``Q`` objects as
positional (not-named) arguments. If you provide multiple ``Q`` object
arguments to a lookup function, the arguments will be ANDed together, for
example::

    Poll.objects.get(
        Q(question__startswith='Who'),
        Q(pub_date=date(2005, 5, 2)) | Q(pub_date=date(2005, 5, 6))
    )

roughly translates into the following SQL::

    SELECT * from polls WHERE question LIKE 'Who%'
        AND (pub_date = '2005-05-02' OR pub_date = '2005-05-06')

Lookup functions can mix the use of ``Q`` objects and keyword arguments. All
arguments provided to a lookup function (be they keyword arguments or ``Q``
objects) are ANDed together. However, if a ``Q`` object is provided, it must
precede the definition of any keyword arguments. For example, the following::

    Poll.objects.get(
        Q(pub_date=date(2005, 5, 2)) | Q(pub_date=date(2005, 5, 6)),
        question__startswith='Who')

would be a valid query, equivalent to the previous example, but this::

    # INVALID QUERY
    Poll.objects.get(
        question__startswith='Who',
        Q(pub_date=date(2005, 5, 2)) | Q(pub_date=date(2005, 5, 6)))

would not be valid.

You can find some examples online at http://www.djangoproject.com/documentation/models/or_lookups/.

Related Objects
===============

When you define a relationship in a model (i.e., a ``ForeignKey``,
``OneToOneField``, or ``ManyToManyField``), instances of that model will have
a convenient API to access the related object(s).

For example, an ``Entry`` object ``e`` can get its associated ``Blog`` object by
accessing the ``blog`` attribute ``e.blog``.

Django also creates API accessors for the "other" side of the relationship --
the link from the related model to the model that defines the relationship.
For example, a ``Blog`` object ``b`` has access to a list of all related
``Entry`` objects via the ``entry_set`` attribute: ``b.entry_set.all()``.

All examples in this section use the sample ``Blog``, ``Author``, and ``Entry``
models defined at the start of the appendix.

Lookups That Span Relationships
-------------------------------

Django offers a powerful and intuitive way to "follow" relationships in
lookups, taking care of the SQL ``JOIN``\s for you automatically behind the
scenes. To span a relationship, just use the field name of related fields
across models, separated by double underscores, until you get to the field you
want.

This example retrieves all ``Entry`` objects with a ``Blog`` whose ``name``
is ``'Beatles Blog'``::

    >>> Entry.objects.filter(blog__name__exact='Beatles Blog')

This spanning can be as deep as you'd like.

It works backward, too. To refer to a "reverse" relationship, just use the
lowercase name of the model.

This example retrieves all ``Blog`` objects that have at least one ``Entry``
whose ``headline`` contains ``'Lennon'``::

    >>> Blog.objects.filter(entry__headline__contains='Lennon')

Foreign Key Relationships
-------------------------

If a model has a ``ForeignKey``, instances of that model will have access to
the related (foreign) object via a simple attribute of the model, for example::

    e = Entry.objects.get(id=2)
    e.blog # Returns the related Blog object.

You can get and set via a foreign key attribute. As you may expect, changes to
the foreign key aren't saved to the database until you call ``save()``, for example::

    e = Entry.objects.get(id=2)
    e.blog = some_blog
    e.save()

If a ``ForeignKey`` field has ``null=True`` set (i.e., it allows ``NULL``
values), you can set it to ``NULL`` by assigning ``None`` to it and saving::

    e = Entry.objects.get(id=2)
    e.blog = None
    e.save() # "UPDATE blog_entry SET blog_id = NULL ...;"

Forward access to one-to-many relationships is cached the first time the
related object is accessed. Subsequent accesses to the foreign key on the same
object instance are cached, for example::

    e = Entry.objects.get(id=2)
    print e.blog  # Hits the database to retrieve the associated Blog.
    print e.blog  # Doesn't hit the database; uses cached version.

Note that the ``select_related()`` ``QuerySet`` method recursively prepopulates
the cache of all one-to-many relationships ahead of time::

    e = Entry.objects.select_related().get(id=2)
    print e.blog  # Doesn't hit the database; uses cached version.
    print e.blog  # Doesn't hit the database; uses cached version.

``select_related()`` is documented in the "QuerySet Methods That Return New
QuerySets" section.

"Reverse" Foreign Key Relationships
-----------------------------------

Foreign key relationships are automatically symmetrical -- a reverse
relationship is inferred from the presence of a ``ForeignKey`` pointing to
another model.

If a model has a ``ForeignKey``, instances of the foreign key model will have
access to a ``Manager`` that returns all instances of the first model that
relate to that object. By default, this ``Manager`` is named ``FOO_set``, where
``FOO`` is the source model name, lowercased. This ``Manager`` returns
``QuerySets``, which can be filtered and manipulated as described in the
"Retrieving Objects" section.

Here's an example::

    b = Blog.objects.get(id=1)
    b.entry_set.all() # Returns all Entry objects related to Blog.

    # b.entry_set is a Manager that returns QuerySets.
    b.entry_set.filter(headline__contains='Lennon')
    b.entry_set.count()

You can override the ``FOO_set`` name by setting the ``related_name``
parameter in the ``ForeignKey()`` definition. For example, if the ``Entry``
model was altered to ``blog = ForeignKey(Blog, related_name='entries')``, the
preceding example code would look like this::

    b = Blog.objects.get(id=1)
    b.entries.all() # Returns all Entry objects related to Blog.

    # b.entries is a Manager that returns QuerySets.
    b.entries.filter(headline__contains='Lennon')
    b.entries.count()

``related_name`` is particularly useful if a model has two foreign keys to the
same second model.

You cannot access a reverse ``ForeignKey`` ``Manager`` from the class; it must
be accessed from an instance::

    Blog.entry_set # Raises AttributeError: "Manager must be accessed via instance".

In addition to the ``QuerySet`` methods defined in the "Retrieving Objects" section,
the ``ForeignKey`` ``Manager`` has these additional methods:

* ``add(obj1, obj2, ...)``: Adds the specified model objects to the related
  object set, for example::

      b = Blog.objects.get(id=1)
      e = Entry.objects.get(id=234)
      b.entry_set.add(e) # Associates Entry e with Blog b.

* ``create(**kwargs)``: Creates a new object, saves it, and puts it in the
  related object set. It returns the newly created object::

      b = Blog.objects.get(id=1)
      e = b.entry_set.create(headline='Hello', body_text='Hi', pub_date=datetime.date(2005, 1, 1))
      # No need to call e.save() at this point -- it's already been saved.

  This is equivalent to (but much simpler than) the following::

      b = Blog.objects.get(id=1)
      e = Entry(blog=b, headline='Hello', body_text='Hi', pub_date=datetime.date(2005, 1, 1))
      e.save()

  Note that there's no need to specify the keyword argument of the model
  that defines the relationship. In the preceding example, we don't pass the
  parameter ``blog`` to ``create()``. Django figures out that the new
  ``Entry`` object's ``blog`` field should be set to ``b``.

* ``remove(obj1, obj2, ...)``: Removes the specified model objects from the
  related object set::

      b = Blog.objects.get(id=1)
      e = Entry.objects.get(id=234)
      b.entry_set.remove(e) # Disassociates Entry e from Blog b.

  In order to prevent database inconsistency, this method only exists on
  ``ForeignKey`` objects where ``null=True``. If the related field can't be
  set to ``None`` (``NULL``), then an object can't be removed from a
  relation without being added to another. In the preceding example, removing
  ``e`` from ``b.entry_set()`` is equivalent to doing ``e.blog = None``,
  and because the ``blog`` ``ForeignKey`` doesn't have ``null=True``, this
  is invalid.

* ``clear()``: Removes all objects from the related object set::

      b = Blog.objects.get(id=1)
      b.entry_set.clear()

  Note this doesn't delete the related objects -- it just disassociates
  them.

  Just like ``remove()``, ``clear()`` is only available on ``ForeignKey``s
  where ``null=True``.

To assign the members of a related set in one fell swoop, just assign to it
from any iterable object, for example::

    b = Blog.objects.get(id=1)
    b.entry_set = [e1, e2]

If the ``clear()`` method is available, any pre-existing objects will be
removed from the ``entry_set`` before all objects in the iterable (in this
case, a list) are added to the set. If the ``clear()`` method is *not*
available, all objects in the iterable will be added without removing any
existing elements.

Each "reverse" operation described in this section has an immediate effect on
the database. Every addition, creation, and deletion is immediately and
automatically saved to the database.

Many-to-Many Relationships
--------------------------

Both ends of a many-to-many relationship get automatic API access to the other
end. The API works just as a "reverse" one-to-many relationship (described
in the previous section).

The only difference is in the attribute naming: the model that defines the
``ManyToManyField`` uses the attribute name of that field itself, whereas the
"reverse" model uses the lowercased model name of the original model, plus
``'_set'`` (just like reverse one-to-many relationships).

An example makes this concept easier to understand::

    e = Entry.objects.get(id=3)
    e.authors.all() # Returns all Author objects for this Entry.
    e.authors.count()
    e.authors.filter(name__contains='John')

    a = Author.objects.get(id=5)
    a.entry_set.all() # Returns all Entry objects for this Author.

Like ``ForeignKey``, ``ManyToManyField`` can specify ``related_name``. In the
preceding example, if the ``ManyToManyField`` in ``Entry`` had specified
``related_name='entries'``, then each ``Author`` instance would have an
``entries`` attribute instead of ``entry_set``.

.. admonition:: How Are the Backward Relationships Possible?

    Other object-relational mappers require you to define relationships on both
    sides. The Django developers believe this is a violation of the DRY (Don't
    Repeat Yourself) principle, so Django requires you to define the
    relationship on only one end. But how is this possible, given that a model
    class doesn't know which other model classes are related to it until those
    other model classes are loaded?

    The answer lies in the ``INSTALLED_APPS`` setting. The first time any model
    is loaded, Django iterates over every model in ``INSTALLED_APPS`` and
    creates the backward relationships in memory as needed. Essentially, one of
    the functions of ``INSTALLED_APPS`` is to tell Django the entire model
    domain.

Queries Over Related Objects
----------------------------

Queries involving related objects follow the same rules as queries involving
normal value fields. When specifying the value for a query to match, you
may use either an object instance itself or the primary key value for the
object.

For example, if you have a ``Blog`` object ``b`` with ``id=5``, the following
three queries would be identical::

    Entry.objects.filter(blog=b) # Query using object instance
    Entry.objects.filter(blog=b.id) # Query using id from instance
    Entry.objects.filter(blog=5) # Query using id directly

Deleting Objects
================

The delete method, conveniently, is named ``delete()``. This method immediately
deletes the object and has no return value::

    e.delete()

You can also delete objects in bulk. Every ``QuerySet`` has a ``delete()``
method, which deletes all members of that ``QuerySet``. For example, this
deletes all ``Entry`` objects with a ``pub_date`` year of 2005::

    Entry.objects.filter(pub_date__year=2005).delete()

When Django deletes an object, it emulates the behavior of the SQL
constraint ``ON DELETE CASCADE`` -- in other words, any objects that
had foreign keys pointing at the object to be deleted will be deleted
along with it, for example::

    b = Blog.objects.get(pk=1)
    # This will delete the Blog and all of its Entry objects.
    b.delete()

Note that ``delete()`` is the only ``QuerySet`` method that is not exposed on a
``Manager`` itself. This is a safety mechanism to prevent you from accidentally
requesting ``Entry.objects.delete()`` and deleting *all* the entries. If you
*do* want to delete all the objects, then you have to explicitly request a
complete query set::

    Entry.objects.all().delete()

Shortcuts
=========

As you develop views, you will discover a number of common idioms in the
way you use the database API. Django encodes some of these idioms as
shortcuts that can be used to simplify the process of writing views. These
functions are in the ``django.shortcuts`` module.

get_object_or_404()
-------------------

One common idiom to use ``get()`` and raise ``Http404`` if the
object doesn't exist. This idiom is captured by ``get_object_or_404()``.
This function takes a Django model as its first argument and an
arbitrary number of keyword arguments, which it passes to the default
manager's ``get()`` function. It raises ``Http404`` if the object doesn't
exist, for example::

    # Get the Entry with a primary key of 3
    e = get_object_or_404(Entry, pk=3)

When you provide a model to this shortcut function, the default manager
is used to execute the underlying ``get()`` query. If you don't want to
use the default manager, or if you want to search a list of related objects,
you can provide ``get_object_or_404()`` with a ``Manager`` object instead::

    # Get the author of blog instance e with a name of 'Fred'
    a = get_object_or_404(e.authors, name='Fred')

    # Use a custom manager 'recent_entries' in the search for an
    # entry with a primary key of 3
    e = get_object_or_404(Entry.recent_entries, pk=3)

get_list_or_404()
-----------------

``get_list_or_404`` behaves the same way as ``get_object_or_404()``,
except that it uses ``filter()`` instead of ``get()``. It raises
``Http404`` if the list is empty.

Falling Back to Raw SQL
=======================

If you find yourself needing to write an SQL query that is too complex for
Django's database mapper to handle, you can fall back into raw SQL statement
mode.

The preferred way to do this is by giving your model custom methods or custom
manager methods that execute queries. Although there's nothing in Django that
*requires* database queries to live in the model layer, this approach keeps all
your data access logic in one place, which is smart from a code organization
standpoint. For instructions, see Appendix A.

Finally, it's important to note that the Django database layer is merely an
interface to your database. You can access your database via other tools,
programming languages, or database frameworks -- there's nothing Django-specific
about your database.