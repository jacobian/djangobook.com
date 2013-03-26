==================================
Appendix C: Generic View Reference
==================================

Chapter 11 introduced generic views but leaves out some of the gory details.
This appendix describes each generic view along with all the options each view can
take. Be sure to read Chapter 11 before trying to understand the reference
material that follows. You might want to refer back to the ``Book``,
``Publisher``, and ``Author`` objects defined in that chapter; the examples that
follow use these models.

Common Arguments to Generic Views
=================================

Most of these views take a large number of arguments that can change the generic
view's behavior. Many of these arguments work the same across a large number of
views. Table C-1 describes each of these common arguments; anytime you see one
of these arguments in a generic view's argument list, it will work as described in
the table.

.. table:: Table C-1. Common Arguments to Generic Views

    ==========================  ===============================================
    Argument                    Description
    ==========================  ===============================================
    ``allow_empty``             A Boolean specifying whether to display the
                                page if no objects are available. If this is
                                ``False`` and no objects are available, the view
                                will raise a 404 error instead of displaying an
                                empty page. By default, this is ``True``.

    ``context_processors``      A list of additional template-context processors
                                (besides the defaults) to apply to the view's
                                template. See Chapter 9 for information on
                                template context processors.

    ``extra_context``           A dictionary of values to add to the template
                                context. By default, this is an empty
                                dictionary. If a value in the dictionary is
                                callable, the generic view will call it just
                                before rendering the template.

    ``mimetype``                The MIME type to use for the resulting
                                document. It defaults to the value of the
                                ``DEFAULT_MIME_TYPE`` setting, which is
                                ``text/html`` if you haven't changed it.

    ``queryset``                A ``QuerySet`` (i.e., something like
                                ``Author.objects.all()``) to read objects from.
                                See Appendix B for more information about
                                ``QuerySet`` objects. Most generic views require
                                this argument.

    ``template_loader``         The template loader to use when loading the
                                template. By default, it's
                                ``django.template.loader``. See Chapter 9 for
                                information on template loaders.

    ``template_name``           The full name of a template to use in rendering
                                the page. This lets you override the default
                                template name derived from the ``QuerySet``.

    ``template_object_name``    The name of the template variable to
                                use in the template context. By default, this is
                                ``'object'``. Views that list more than one
                                object (i.e., ``object_list`` views and various
                                objects-for-date views) will append ``'_list'``
                                to the value of this parameter.
    ==========================  ===============================================

"Simple" Generic Views
======================

The module``django.views.generic.simple`` contains simple views that handle a
couple of common cases: rendering a template when no view logic is needed and
issuing a redirect.

Rendering a Template
--------------------

*View function*: ``django.views.generic.simple.direct_to_template``

This view renders a given template, passing it a ``{{ params }}`` template
variable, which is a dictionary of the parameters captured in the URL.

Example
```````

Given the following URLconf::

    from django.conf.urls.defaults import *
    from django.views.generic.simple import direct_to_template

    urlpatterns = patterns('',
        (r'^foo/$',             direct_to_template, {'template': 'foo_index.html'}),
        (r'^foo/(?P<id>\d+)/$', direct_to_template, {'template': 'foo_detail.html'}),
    )

a request to ``/foo/`` would render the template ``foo_index.html``, and a
request to ``/foo/15/`` would render ``foo_detail.html`` with a context
variable ``{{ params.id }}`` that is set to ``15``.

Required Arguments
``````````````````

* ``template``: The full name of a template to use.

Redirecting to Another URL
--------------------------

*View function*: ``django.views.generic.simple.redirect_to``

This view redirects to another URL. The given URL may contain dictionary-style string
formatting, which will be interpolated against the parameters captured in the
URL.

If the given URL is ``None``, Django will return an HTTP 410 ("Gone") message.

Example
```````

This URLconf redirects from ``/foo/<id>/`` to ``/bar/<id>/``::

    from django.conf.urls.defaults import *
    from django.views.generic.simple import redirect_to

    urlpatterns = patterns('django.views.generic.simple',
        ('^foo/(?p<id>\d+)/$', redirect_to, {'url': '/bar/%(id)s/'}),
    )

This example returns a "Gone" response for requests to ``/bar/``::

    from django.views.generic.simple import redirect_to

    urlpatterns = patterns('django.views.generic.simple',
        ('^bar/$', redirect_to, {'url': None}),
    )

Required Arguments
``````````````````

* ``url``: The URL to redirect to, as a string. Or ``None`` to return a 410
  ("Gone") HTTP response.

List/Detail Generic Views
=========================

The list/detail generic views (in the module
``django.views.generic.list_detail``) handle the common case of displaying a
list of items at one view and individual "detail" views of those items at
another.

Lists of Objects
----------------

*View function*: ``django.views.generic.list_detail.object_list``

Use this view to display a page representing a list of objects.

Example
```````

Given the ``Author`` object from Chapter 5, we can use the ``object_list`` view
to show a simple list of all authors given the following URLconf snippet::

    from mysite.books.models import Author
    from django.conf.urls.defaults import *
    from django.views.generic import list_detail

    author_list_info = {
        'queryset':   Author.objects.all(),
    }

    urlpatterns = patterns('',
        (r'authors/$', list_detail.object_list, author_list_info)
    )

Required Arguments
``````````````````

* ``queryset``: A ``QuerySet`` of objects to list (see Table C-1).

Optional Arguments
``````````````````

* ``paginate_by``: An integer specifying how many objects should be
  displayed per page. If this is given, the view will paginate objects with
  ``paginate_by`` objects per page. The view will expect either a ``page``
  query string parameter (via ``GET``) containing a zero-indexed page
  number, or a ``page`` variable specified in the URLconf. See the following
  "Notes on Pagination" section.

Additionally, this view may take any of these common arguments described in
Table C-1:

* ``allow_empty``
* ``context_processors``
* ``extra_context``
* ``mimetype``
* ``template_loader``
* ``template_name``
* ``template_object_name``

Template Name
`````````````

If ``template_name`` isn't specified, this view will use the template
``<app_label>/<model_name>_list.html`` by default. Both the application label and the
model name are derived from the ``queryset`` parameter. The application label is the
name of the application that the model is defined in, and the model name is the
lowercased version of the name of the model class.

In the previous example using ``Author.objects.all()`` as the ``queryset``, the application
label would be ``books`` and the model name would be ``author``. This means
the default template would be ``books/author_list.html``.

Template Context
````````````````

In addition to ``extra_context``, the template's context will contain the following:

* ``object_list``: The list of objects. This variable's name depends on the
  ``template_object_name`` parameter, which is ``'object'`` by default. If
  ``template_object_name`` is ``'foo'``, this variable's name will be
  ``foo_list``.

* ``is_paginated``: A Boolean representing whether the results are
  paginated. Specifically, this is set to ``False`` if the number of
  available objects is less than or equal to ``paginate_by``.

If the results are paginated, the context will contain these extra variables:

* ``results_per_page``: The number of objects per page. (This is the same as
  the ``paginate_by`` parameter.)

* ``has_next``: A Boolean representing whether there's a next page.

* ``has_previous``: A Boolean representing whether there's a previous page.

* ``page``: The current page number, as an integer. This is 1-based.

* ``next``: The next page number, as an integer. If there's no next page,
  this will still be an integer representing the theoretical next-page
  number. This is 1-based.

* ``previous``: The previous page number, as an integer. This is 1-based.

* ``pages``: The total number of pages, as an integer.

* ``hits``: The total number of objects across *all* pages, not just this
  page.

.. admonition:: A Note on Pagination

    If ``paginate_by`` is specified, Django will paginate the results. You can
    specify the page number in the URL in one of two ways:

    * Use the ``page`` parameter in the URLconf. For example, this is what
      your URLconf might look like::

        (r'^objects/page(?P<page>[0-9]+)/$', 'object_list', dict(info_dict))

    * Pass the page number via the ``page`` query-string parameter. For
      example, a URL would look like this::

        /objects/?page=3

    In both cases, ``page`` is 1-based, not 0-based, so the first page would be
    represented as page ``1``.

Detail Views
------------

*View function*: ``django.views.generic.list_detail.object_detail``

This view provides a "detail" view of a single object.

Example
```````

Continuing the previous ``object_list`` example, we could add a detail view for a
given author by modifying the URLconf:

.. parsed-literal::

    from mysite.books.models import Author
    from django.conf.urls.defaults import *
    from django.views.generic import list_detail

    author_list_info = {
        'queryset' :   Author.objects.all(),
    }
    **author_detail_info = {**
        **"queryset" : Author.objects.all(),**
        **"template_object_name" : "author",**
    **}**

    urlpatterns = patterns('',
        (r'authors/$', list_detail.object_list, author_list_info),
        **(r'^authors/(?P<object_id>\d+)/$', list_detail.object_detail, author_detail_info),**
    )

Required Arguments
``````````````````

* ``queryset``: A ``QuerySet`` that will be searched for the object (see Table C-1).

and either

* ``object_id``: The value of the primary-key field for the object.

or

* ``slug``: The slug of the given object. If you pass this field, then the
  ``slug_field`` argument (see the following section) is also required.

Optional Arguments
``````````````````

* ``slug_field``: The name of the field on the object containing the slug.
  This is required if you are using the ``slug`` argument, but it must be
  absent if you're using the ``object_id`` argument.

* ``template_name_field``: The name of a field on the object whose value is
  the template name to use. This lets you store template names in your data.

  In other words, if your object has a field ``'the_template'`` that
  contains a string ``'foo.html'``, and you set ``template_name_field`` to
  ``'the_template'``, then the generic view for this object will use the
  template ``'foo.html'``.

  If the template named by ``template_name_field`` doesn't exist, the one
  named by ``template_name`` is used instead.  It's a bit of a
  brain-bender, but it's useful in some cases.

This view may also take these common arguments (see Table C-1):

* ``context_processors``
* ``extra_context``
* ``mimetype``
* ``template_loader``
* ``template_name``
* ``template_object_name``

Template Name
`````````````

If ``template_name`` and ``template_name_field`` aren't specified, this view
will use the template ``<app_label>/<model_name>_detail.html`` by default.

Template Context
````````````````

In addition to ``extra_context``, the template's context will be as follows:

* ``object``: The object. This variable's name depends on the
  ``template_object_name`` parameter, which is ``'object'`` by default. If
  ``template_object_name`` is ``'foo'``, this variable's name will be
  ``foo``.

Date-Based Generic Views
========================

Date-based generic views are generally used to provide a set of "archive"
pages for dated material. Think year/month/day archives for a newspaper, or a
typical blog archive.

.. admonition:: Tip:

    By default, these views ignore objects with dates in the future.

    This means that if you try to visit an archive page in the future, Django
    will automatically show a 404 ("Page not found") error, even if there are objects
    published that day.

    Thus, you can publish postdated objects that don't appear publicly until
    their desired publication date.

    However, for different types of date-based objects, this isn't appropriate
    (e.g., a calendar of upcoming events). For these views, setting the
    ``allow_future`` option to ``True`` will make the future objects appear (and
    allow users to visit "future" archive pages).

Archive Index
-------------

*View function*: ``django.views.generic.date_based.archive_index``

This view provides a top-level index page showing the "latest" (i.e., most
recent) objects by date.

Example
```````

Say a typical book publisher wants a page of recently published books. Given some
``Book`` object with a ``publication_date`` field, we can use the
``archive_index`` view for this common task:

.. parsed-literal::

    from mysite.books.models import Book
    from django.conf.urls.defaults import *
    from django.views.generic import date_based

    book_info = {
        "queryset"   : Book.objects.all(),
        "date_field" : "publication_date"
    }

    urlpatterns = patterns('',
        (r'^books/$', date_based.archive_index, book_info),
    )

Required Arguments
``````````````````

* ``date_field``: The name of the ``DateField`` or ``DateTimeField`` in the
  ``QuerySet``'s model that the date-based archive should use to determine
  the objects on the page.

* ``queryset``: A ``QuerySet`` of objects for which the archive serves.

Optional Arguments
``````````````````

* ``allow_future``: A Boolean specifying whether to include "future" objects
  on this page, as described in the previous note.

* ``num_latest``: The number of latest objects to send to the template
  context. By default, it's 15.

This view may also take these common arguments (see Table C-1):

* ``allow_empty``
* ``context_processors``
* ``extra_context``
* ``mimetype``
* ``template_loader``
* ``template_name``

Template Name
`````````````

If ``template_name`` isn't specified, this view will use the template
``<app_label>/<model_name>_archive.html`` by default.

Template Context
````````````````

In addition to ``extra_context``, the template's context will be as follows:

* ``date_list``: A list of ``datetime.date`` objects representing all years
  that have objects available according to ``queryset``. These are ordered
  in reverse.

  For example, if you have blog entries from 2003 through 2006, this list
  will contain four ``datetime.date`` objects: one for each of those years.

* ``latest``: The ``num_latest`` objects in the system, in descending order
  by ``date_field``. For example, if ``num_latest`` is ``10``, then
  ``latest`` will be a list of the latest ten objects in ``queryset``.

Year Archives
-------------

*View function*: ``django.views.generic.date_based.archive_year``

Use this view for yearly archive pages. These pages have a list of months in
which objects exists, and they can optionally display all the objects published in
a given year.

Example
```````

Extending the ``archive_index`` example from earlier, we'll add a way to view all
the books published in a given year:

.. parsed-literal::

    from mysite.books.models import Book
    from django.conf.urls.defaults import *
    from django.views.generic import date_based

    book_info = {
        "queryset"   : Book.objects.all(),
        "date_field" : "publication_date"
    }

    urlpatterns = patterns('',
        (r'^books/$', date_based.archive_index, book_info),
        **(r'^books/(?P<year>\d{4})/?$', date_based.archive_year, book_info),**
    )

Required Arguments
``````````````````

* ``date_field``: As for ``archive_index`` (see the previous section).

* ``queryset``: A ``QuerySet`` of objects for which the archive serves.

* ``year``: The four-digit year for which the archive serves (as in our
  example, this is usually taken from a URL parameter).

Optional Arguments
``````````````````

* ``make_object_list``: A Boolean specifying whether to retrieve the full
  list of objects for this year and pass those to the template. If ``True``,
  this list of objects will be made available to the template as
  ``object_list``. (The name ``object_list`` may be different; see the
  information about ``object_list`` in the following "Template Context"
  section.) By default, this is ``False``.

* ``allow_future``: A Boolean specifying whether to include "future" objects
  on this page.

This view may also take these common arguments (see Table C-1):

* ``allow_empty``
* ``context_processors``
* ``extra_context``
* ``mimetype``
* ``template_loader``
* ``template_name``
* ``template_object_name``

Template Name
`````````````

If ``template_name`` isn't specified, this view will use the template
``<app_label>/<model_name>_archive_year.html`` by default.

Template Context
````````````````

In addition to ``extra_context``, the template's context will be as follows:

* ``date_list``: A list of ``datetime.date`` objects representing all months
  that have objects available in the given year, according to ``queryset``,
  in ascending order.

* ``year``: The given year, as a four-character string.

* ``object_list``: If the ``make_object_list`` parameter is ``True``, this
  will be set to a list of objects available for the given year, ordered by
  the date field. This variable's name depends on the
  ``template_object_name`` parameter, which is ``'object'`` by default. If
  ``template_object_name`` is ``'foo'``, this variable's name will be
  ``foo_list``.

  If ``make_object_list`` is ``False``, ``object_list`` will be passed to
  the template as an empty list.

Month Archives
--------------

*View function*: ``django.views.generic.date_based.archive_month``

This view provides monthly archive pages showing all objects for a given month.

Example
```````

Continuing with our example, adding month views should look familiar:

.. parsed-literal::

    urlpatterns = patterns('',
        (r'^books/$', date_based.archive_index, book_info),
        (r'^books/(?P<year>\d{4})/?$', date_based.archive_year, book_info),
        **(**
            **r'^(?P<year>\d{4})/(?P<month>[a-z]{3})/$',**
            **date_based.archive_month,**
            **book_info**
        **),**
    )

Required Arguments
``````````````````

* ``year``: The four-digit year for which the archive serves (a string).

* ``month``: The month for which the archive serves, formatted according to
  the ``month_format`` argument.

* ``queryset``: A ``QuerySet`` of objects for which the archive serves.

* ``date_field``: The name of the ``DateField`` or ``DateTimeField`` in the
  ``QuerySet``'s model that the date-based archive should use to determine
  the objects on the page.

Optional Arguments
``````````````````

* ``month_format``: A format string that regulates what format the ``month``
  parameter uses. This should be in the syntax accepted by Python's
  ``time.strftime``. (See Python's strftime documentation at
  http://docs.python.org/library/time.html#time.strftime.) It's set
  to ``"%b"`` by default, which is a three-letter month abbreviation (i.e.,
  "jan", "feb", etc.). To change it to use numbers, use ``"%m"``.

* ``allow_future``: A Boolean specifying whether to include "future" objects
  on this page, as described in the previous note.

This view may also take these common arguments (see Table C-1):

* ``allow_empty``
* ``context_processors``
* ``extra_context``
* ``mimetype``
* ``template_loader``
* ``template_name``
* ``template_object_name``

Template Name
`````````````

If ``template_name`` isn't specified, this view will use the template
``<app_label>/<model_name>_archive_month.html`` by default.

Template Context
````````````````

In addition to ``extra_context``, the template's context will be as follows:

* ``month``: A ``datetime.date`` object representing the given month.

* ``next_month``: A ``datetime.date`` object representing the first day of
  the next month. If the next month is in the future, this will be ``None``.

* ``previous_month``: A ``datetime.date`` object representing the first day
  of the previous month. Unlike ``next_month``, this will never be ``None``.

* ``object_list``: A list of objects available for the given month. This
  variable's name depends on the ``template_object_name`` parameter, which
  is ``'object'`` by default. If ``template_object_name`` is ``'foo'``, this
  variable's name will be ``foo_list``.

Week Archives
-------------

*View function*: ``django.views.generic.date_based.archive_week``

This view shows all objects in a given week.

.. note::

    For the sake of consistency with Python's built-in date/time handling,
    Django assumes that the first day of the week is Sunday.

Example
```````

.. parsed-literal::

    urlpatterns = patterns('',
        # ...
        **(**
            **r'^(?P<year>\d{4})/(?P<week>\d{2})/$',**
            **date_based.archive_week,**
            **book_info**
        **),**
    )


Required Arguments
``````````````````

* ``year``: The four-digit year for which the archive serves (a string).

* ``week``: The week of the year for which the archive serves (a string).

* ``queryset``: A ``QuerySet`` of objects for which the archive serves.

* ``date_field``: The name of the ``DateField`` or ``DateTimeField`` in the
  ``QuerySet``'s model that the date-based archive should use to determine
  the objects on the page.

Optional Arguments
``````````````````

* ``allow_future``: A Boolean specifying whether to include "future" objects
  on this page, as described in the previous note.

This view may also take these common arguments (see Table C-1):

* ``allow_empty``
* ``context_processors``
* ``extra_context``
* ``mimetype``
* ``template_loader``
* ``template_name``
* ``template_object_name``

Template Name
`````````````

If ``template_name`` isn't specified, this view will use the template
``<app_label>/<model_name>_archive_week.html`` by default.

Template Context
````````````````

In addition to ``extra_context``, the template's context will be as follows:

* ``week``: A ``datetime.date`` object representing the first day of the
  given week.

* ``object_list``: A list of objects available for the given week. This
  variable's name depends on the ``template_object_name`` parameter, which
  is ``'object'`` by default. If ``template_object_name`` is ``'foo'``, this
  variable's name will be ``foo_list``.

Day Archives
------------

*View function*: ``django.views.generic.date_based.archive_day``

This view generates all objects in a given day.

Example
```````

.. parsed-literal::

    urlpatterns = patterns('',
        # ...
        **(**
            **r'^(?P<year>\d{4})/(?P<month>[a-z]{3})/(?P<day>\d{2})/$',**
            **date_based.archive_day,**
            **book_info**
        **),**
    )


Required Arguments
``````````````````

* ``year``: The four-digit year for which the archive serves (a string).

* ``month``: The month for which the archive serves, formatted according to the
  ``month_format`` argument.

* ``day``: The day for which the archive serves, formatted according to the
  ``day_format`` argument.

* ``queryset``: A ``QuerySet`` of objects for which the archive serves.

* ``date_field``: The name of the ``DateField`` or ``DateTimeField`` in the
  ``QuerySet``'s model that the date-based archive should use to determine
  the objects on the page.

Optional Arguments
``````````````````

* ``month_format``: A format string that regulates what format the ``month``
  parameter uses. See the detailed explanation in the "Month Archives"
  section, above.

* ``day_format``: Like ``month_format``, but for the ``day`` parameter. It
  defaults to ``"%d"`` (the day of the month as a decimal number, 01-31).

* ``allow_future``: A Boolean specifying whether to include "future" objects
  on this page, as described in the previous note.

This view may also take these common arguments (see Table C-1):

* ``allow_empty``
* ``context_processors``
* ``extra_context``
* ``mimetype``
* ``template_loader``
* ``template_name``
* ``template_object_name``

Template Name
`````````````

If ``template_name`` isn't specified, this view will use the template
``<app_label>/<model_name>_archive_day.html`` by default.

Template Context
````````````````

In addition to ``extra_context``, the template's context will be as follows:

* ``day``: A ``datetime.date`` object representing the given day.

* ``next_day``: A ``datetime.date`` object representing the next day. If the
  next day is in the future, this will be ``None``.

* ``previous_day``: A ``datetime.date`` object representing the previous day.
  Unlike ``next_day``, this will never be ``None``.

* ``object_list``: A list of objects available for the given day. This
  variable's name depends on the ``template_object_name`` parameter, which
  is ``'object'`` by default. If ``template_object_name`` is ``'foo'``, this
  variable's name will be ``foo_list``.

Archive for Today
-----------------

The ``django.views.generic.date_based.archive_today`` view shows all objects for
*today*. This is exactly the same as ``archive_day``, except the
``year``/``month``/``day`` arguments are not used, and today's date is used
instead.

Example
```````

.. parsed-literal::

    urlpatterns = patterns('',
        # ...
        **(r'^books/today/$', date_based.archive_today, book_info),**
    )


Date-Based Detail Pages
-----------------------

*View function*: ``django.views.generic.date_based.object_detail``

Use this view for a page representing an individual object.

This has a different URL from the ``object_detail`` view; the ``object_detail``
view uses URLs like ``/entries/<slug>/``, while this one uses URLs like
``/entries/2006/aug/27/<slug>/``.

.. note::

    If you're using date-based detail pages with slugs in the URLs, you probably
    also want to use the ``unique_for_date`` option on the slug field to
    validate that slugs aren't duplicated in a single day. See Appendix A for
    details on ``unique_for_date``.

Example
```````

This one differs (slightly) from all the other date-based examples in that we
need to provide either an object ID or a slug so that Django can look up the
object in question.

Since the object we're using doesn't have a slug field, we'll use ID-based URLs.
It's considered a best practice to use a slug field, but in the interest of
simplicity we'll let it go.

.. parsed-literal::

    urlpatterns = patterns('',
        # ...
        **(**
            **r'^(?P<year>\d{4})/(?P<month>[a-z]{3})/(?P<day>\d{2})/(?P<object_id>[\w-]+)/$',**
            **date_based.object_detail,**
            **book_info**
        **),**
    )

Required Arguments
``````````````````

* ``year``: The object's four-digit year (a string).

* ``month``: The object's month, formatted according to the ``month_format``
  argument.

* ``day``: The object's day, formatted according to the ``day_format`` argument.

* ``queryset``: A ``QuerySet`` that contains the object.

* ``date_field``: The name of the ``DateField`` or ``DateTimeField`` in the
  ``QuerySet``'s model that the generic view should use to look up the
  object according to ``year``, ``month``, and ``day``.

You'll also need either:

* ``object_id``: The value of the primary-key field for the object.

or:

* ``slug``: The slug of the given object. If you pass this field, then the
  ``slug_field`` argument (described in the following section) is also
  required.

Optional Arguments
``````````````````

* ``allow_future``: A Boolean specifying whether to include "future" objects
  on this page, as described in the previous note.

* ``day_format``: Like ``month_format``, but for the ``day`` parameter. It
  defaults to ``"%d"`` (the day of the month as a decimal number, 01-31).

* ``month_format``: A format string that regulates what format the ``month``
  parameter uses. See the detailed explanation in the "Month Archives"
  section, above.

* ``slug_field``: The name of the field on the object containing the slug.
  This is required if you are using the ``slug`` argument, but it must be
  absent if you're using the ``object_id`` argument.

* ``template_name_field``: The name of a field on the object whose value is
  the template name to use. This lets you store template names in the data.
  In other words, if your object has a field ``'the_template'`` that
  contains a string ``'foo.html'``, and you set ``template_name_field`` to
  ``'the_template'``, then the generic view for this object will use the
  template ``'foo.html'``.

This view may also take these common arguments (see Table C-1):

* ``context_processors``
* ``extra_context``
* ``mimetype``
* ``template_loader``
* ``template_name``
* ``template_object_name``

Template Name
`````````````

If ``template_name`` and ``template_name_field`` aren't specified, this view
will use the template ``<app_label>/<model_name>_detail.html`` by default.

Template Context
````````````````

In addition to ``extra_context``, the template's context will be as follows:

* ``object``: The object. This variable's name depends on the
  ``template_object_name`` parameter, which is ``'object'`` by default. If
  ``template_object_name`` is ``'foo'``, this variable's name will be
  ``foo``.