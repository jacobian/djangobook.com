========================================
Appendix G: Request and Response Objects
========================================

Django uses request and response objects to pass state through the system.

When a page is requested, Django creates an ``HttpRequest`` object that
contains metadata about the request. Then Django loads the appropriate view,
passing the ``HttpRequest`` as the first argument to the view function. Each
view is responsible for returning an ``HttpResponse`` object.

We've used these objects often throughout the book; this appendix explains the
complete APIs for ``HttpRequest`` and ``HttpResponse`` objects.

HttpRequest
===========

``HttpRequest`` represents a single HTTP request from some user-agent.

Much of the important information about the request is available as attributes
on the ``HttpRequest`` instance (see Table G-1). All attributes except
``session`` should be considered read-only.

.. table:: Table G-1. Attributes of HttpRequest Objects

    ==================  =======================================================
    Attribute           Description
    ==================  =======================================================
    ``path``            A string representing the full path to the requested
                        page, not including the domain -- for example,
                        ``"/music/bands/the_beatles/"``.

    ``method``          A string representing the HTTP method used in the
                        request. This is guaranteed to be uppercase. For
                        example::

                            if request.method == 'GET':
                                do_something()
                            elif request.method == 'POST':
                                do_something_else()

    ``encoding``        A string representing the current encoding used to
                        decode form submission data (or ``None``, which means
                        the ``DEFAULT_CHARSET`` setting is used).

                        You can write to this attribute to change the encoding
                        used when accessing the form data. Any subsequent
                        attribute accesses (such as reading from ``GET`` or
                        ``POST``) will use the new ``encoding`` value.  Useful
                        if you know the form data is not in the
                        ``DEFAULT_CHARSET`` encoding.

    ``GET``             A dictionary-like object containing all given HTTP GET
                        parameters. See the upcoming ``QueryDict`` documentation.

    ``POST``            A dictionary-like object containing all given HTTP POST
                        parameters. See the upcoming ``QueryDict`` documentation.

                        It's possible that a request can come in via POST with
                        an empty ``POST`` dictionary -- if, say, a form is
                        requested via the POST HTTP method but does not
                        include form data. Therefore, you shouldn't use ``if
                        request.POST`` to check for use of the POST method;
                        instead, use ``if request.method == "POST"`` (see
                        the ``method`` entry in this table).

                        Note: ``POST`` does *not* include file-upload
                        information. See ``FILES``.

    ``REQUEST``         For convenience, a dictionary-like object that searches
                        ``POST`` first, and then ``GET``. Inspired by PHP's
                        ``$_REQUEST``.

                        For example, if ``GET = {"name": "john"}`` and ``POST
                        = {"age": '34'}``, ``REQUEST["name"]`` would be
                        ``"john"``, and ``REQUEST["age"]`` would be ``"34"``.

                        It's strongly suggested that you use ``GET`` and
                        ``POST`` instead of ``REQUEST``, because the former
                        are more explicit.

    ``COOKIES``         A standard Python dictionary containing all cookies.
                        Keys and values are strings. See Chapter 14 for more
                        on using cookies.

    ``FILES``           A dictionary-like object that maps filenames to
                        ``UploadedFile`` objects. See the Django
                        documentation for more.

    ``META``            A standard Python dictionary containing all available
                        HTTP headers. Available headers depend on the client
                        and server, but here are some examples:

                        * ``CONTENT_LENGTH``
                        * ``CONTENT_TYPE``
                        * ``QUERY_STRING``: The raw unparsed query string
                        * ``REMOTE_ADDR``: The IP address of the client
                        * ``REMOTE_HOST``: The hostname of the client
                        * ``SERVER_NAME``: The hostname of the server.
                        * ``SERVER_PORT``: The port of the server

                        Any HTTP headers are available in ``META`` as keys
                        prefixed with ``HTTP_``, converted to uppercase and
                        substituting underscores for hyphens. For example:

                        * ``HTTP_ACCEPT_ENCODING``
                        * ``HTTP_ACCEPT_LANGUAGE``
                        * ``HTTP_HOST``: The HTTP ``Host`` header sent by
                          the client
                        * ``HTTP_REFERER``: The referring page, if any
                        * ``HTTP_USER_AGENT``: The client's user-agent string
                        * ``HTTP_X_BENDER``: The value of the ``X-Bender``
                          header, if set

    ``user``            A ``django.contrib.auth.models.User`` object
                        representing the currently logged-in user. If the user
                        isn't currently logged in, ``user`` will be set to an
                        instance of
                        ``django.contrib.auth.models.AnonymousUser``. You can
                        tell them apart with ``is_authenticated()``, like so::

                            if request.user.is_authenticated():
                                # Do something for logged-in users.
                            else:
                                # Do something for anonymous users.

                        ``user`` is available only if your Django installation
                        has the ``AuthenticationMiddleware`` activated.

                        For the complete details of authentication and users,
                        see Chapter 14.

    ``session``         A readable and writable, dictionary-like object that
                        represents the current session. This is available only
                        if your Django installation has session support
                        activated. See Chapter 14.

    ``raw_post_data``   The raw HTTP POST data. This is useful for advanced
                        processing.
    ==================  =======================================================

Request objects also have a few useful methods, as shown in Table G-2.

.. table:: Table G-2. HttpRequest Methods

    ======================  ===================================================
    Method                  Description
    ======================  ===================================================
    ``__getitem__(key)``    Returns the GET/POST value for the given key,
                            checking POST first, and then GET. Raises
                            ``KeyError`` if the key doesn't exist.

                            This lets you use dictionary-accessing syntax on
                            an ``HttpRequest`` instance.

                            For example, ``request["foo"]`` is the same as
                            checking ``request.POST["foo"]`` and then
                            ``request.GET["foo"]``.

    ``has_key()``           Returns ``True`` or ``False``, designating whether
                            ``request.GET`` or ``request.POST`` has the given
                            key.

    ``get_host()``          Returns the originating host of the request using
                            information from the ``HTTP_X_FORWARDED_HOST`` and
                            ``HTTP_HOST`` headers (in that order). If they
                            don't provide a value, the method uses a
                            combination of ``SERVER_NAME`` and
                            ``SERVER_PORT``.

    ``get_full_path()``     Returns the ``path``, plus an appended query
                            string, if applicable. For example,
                            ``"/music/bands/the_beatles/?print=true"``

    ``is_secure()``         Returns ``True`` if the request is secure; that
                            is, if it was made with HTTPS.
    ======================  ===================================================

QueryDict Objects
-----------------

In an ``HttpRequest`` object, the ``GET`` and ``POST`` attributes are
instances of ``django.http.QueryDict``. ``QueryDict`` is a dictionary-like
class customized to deal with multiple values for the same key. This is
necessary because some HTML form elements, notably ``<select
multiple="multiple">``, pass multiple values for the same key.

``QueryDict`` instances are immutable, unless you create a ``copy()`` of them.
That means you can't change attributes of ``request.POST`` and ``request.GET``
directly.

``QueryDict`` implements the all standard dictionary methods, because it's a
subclass of dictionary. Exceptions are outlined in Table G-3.

.. table:: Table G-3. How QueryDicts Differ from Standard Dictionaries.

    ==================  =======================================================
    Method              Differences from Standard dict Implementation
    ==================  =======================================================
    ``__getitem__``     Works just like a dictionary. However, if the key
                        has more than one value, ``__getitem__()`` returns the
                        last value.

    ``__setitem__``     Sets the given key to ``[value]`` (a Python list whose
                        single element is ``value``). Note that this, as other
                        dictionary functions that have side effects, can
                        be called only on a mutable ``QueryDict`` (one that was
                        created via ``copy()``).

    ``get()``           If the key has more than one value, ``get()`` returns
                        the last value just like ``__getitem__``.

    ``update()``        Takes either a ``QueryDict`` or standard dictionary.
                        Unlike the standard dictionary's ``update`` method,
                        this method *appends* to the current dictionary items
                        rather than replacing them::

                            >>> q = QueryDict('a=1')
                            >>> q = q.copy() # to make it mutable
                            >>> q.update({'a': '2'})
                            >>> q.getlist('a')
                            ['1', '2']
                            >>> q['a'] # returns the last
                            ['2']

    ``items()``         Just like the standard dictionary ``items()`` method,
                        except this uses the same last-value logic as
                        ``__getitem()__``::

                             >>> q = QueryDict('a=1&a=2&a=3')
                             >>> q.items()
                             [('a', '3')]

    ``values()``        Just like the standard dictionary ``values()`` method,
                        except this uses the same last-value logic as
                        ``__getitem()__``.
    ==================  =======================================================

In addition, ``QueryDict`` has the methods shown in Table G-4.

.. table:: G-4. Extra (Nondictionary) QueryDict Methods

    ==========================  ===============================================
    Method                      Description
    ==========================  ===============================================
    ``copy()``                  Returns a copy of the object, using
                                ``copy.deepcopy()`` from the Python standard
                                library. The copy will be mutable -- that is,
                                you can change its values.

    ``getlist(key)``            Returns the data with the requested key, as a
                                Python list. Returns an empty list if the key
                                doesn't exist. It's guaranteed to return a
                                list of some sort.

    ``setlist(key, list_)``     Sets the given key to ``list_`` (unlike
                                ``__setitem__()``).

    ``appendlist(key, item)``   Appends an item to the internal list associated
                                with ``key``.

    ``setlistdefault(key, a)``  Just like ``setdefault``, except it takes a
                                list of values instead of a single value.

    ``lists()``                 Like ``items()``, except it includes all
                                values, as a list, for each member of the
                                dictionary. For example::

                                    >>> q = QueryDict('a=1&a=2&a=3')
                                    >>> q.lists()
                                    [('a', ['1', '2', '3'])]


    ``urlencode()``             Returns a string of the data in query-string
                                format (e.g., ``"a=2&b=3&b=5"``).
    ==========================  ===============================================

A Complete Example
------------------

For example, given this HTML form::

    <form action="/foo/bar/" method="post">
    <input type="text" name="your_name" />
    <select multiple="multiple" name="bands">
        <option value="beatles">The Beatles</option>
        <option value="who">The Who</option>
        <option value="zombies">The Zombies</option>
    </select>
    <input type="submit" />
    </form>

if the user enters ``"John Smith"`` in the ``your_name`` field and selects
both "The Beatles" and "The Zombies" in the multiple select box, here's what
Django's request object would have::

    >>> request.GET
    {}
    >>> request.POST
    {'your_name': ['John Smith'], 'bands': ['beatles', 'zombies']}
    >>> request.POST['your_name']
    'John Smith'
    >>> request.POST['bands']
    'zombies'
    >>> request.POST.getlist('bands')
    ['beatles', 'zombies']
    >>> request.POST.get('your_name', 'Adrian')
    'John Smith'
    >>> request.POST.get('nonexistent_field', 'Nowhere Man')
    'Nowhere Man'

.. admonition:: Implementation Note:

    The ``GET``, ``POST``, ``COOKIES``, ``FILES``, ``META``, ``REQUEST``,
    ``raw_post_data``, and ``user`` attributes are all lazily loaded. That means
    Django doesn't spend resources calculating the values of those attributes until
    your code requests them.

HttpResponse
============

In contrast to ``HttpRequest`` objects, which are created automatically by
Django, ``HttpResponse`` objects are your responsibility. Each view you write
is responsible for instantiating, populating, and returning an
``HttpResponse``.

The ``HttpResponse`` class lives at ``django.http.HttpResponse``.

Construction HttpResponses
--------------------------

Typically, you'll construct an ``HttpResponse`` to pass the contents of the
page, as a string, to the ``HttpResponse`` constructor::

    >>> response = HttpResponse("Here's the text of the Web page.")
    >>> response = HttpResponse("Text only, please.", mimetype="text/plain")

But if you want to add content incrementally, you can use ``response`` as a
filelike object::

    >>> response = HttpResponse()
    >>> response.write("<p>Here's the text of the Web page.</p>")
    >>> response.write("<p>Here's another paragraph.</p>")

You can pass ``HttpResponse`` an iterator rather than passing it
hard-coded strings. If you use this technique, follow these guidelines:

* The iterator should return strings.

* If an ``HttpResponse`` has been initialized with an iterator as its
  content, you can't use the ``HttpResponse`` instance as a filelike
  object. Doing so will raise ``Exception``.

Finally, note that ``HttpResponse`` implements a ``write()`` method, which
makes is suitable for use anywhere that Python expects a filelike object. See
Chapter 8 for some examples of using this technique.

Setting Headers
---------------

You can add and delete headers using dictionary syntax::

    >>> response = HttpResponse()
    >>> response['X-DJANGO'] = "It's the best."
    >>> del response['X-PHP']
    >>> response['X-DJANGO']
    "It's the best."

You can also use ``has_header(header)`` to check for the existence of a header.

Avoid setting ``Cookie`` headers by hand; instead, see Chapter 14 for
instructions on how cookies work in Django.

HttpResponse Subclasses
-----------------------

Django includes a number of ``HttpResponse`` subclasses that handle different
types of HTTP responses (see Table G-5). Like ``HttpResponse``, these subclasses live in
``django.http``.

.. table:: Table G-5. HttpResponse Subclasses

    ==================================  =======================================
    Class                               Description
    ==================================  =======================================
    ``HttpResponseRedirect``            The constructor takes a single argument:
                                        the path to redirect to. This can
                                        be a fully qualified URL (e.g.,
                                        ``'http://search.yahoo.com/'``) or
                                        an absolute URL with no domain (e.g.,
                                        ``'/search/'``). Note that this
                                        returns an HTTP status code 302.

    ``HttpResponsePermanentRedirect``   Like ``HttpResponseRedirect``, but it
                                        returns a permanent redirect (HTTP
                                        status code 301) instead of a "found"
                                        redirect (status code 302).

    ``HttpResponseNotModified``         The constructor doesn't take any
                                        arguments. Use this to designate that
                                        a page hasn't been modified since the
                                        user's last request.

    ``HttpResponseBadRequest``          Acts just like ``HttpResponse`` but
                                        uses a 400 status code.

    ``HttpResponseNotFound``            Acts just like ``HttpResponse`` but
                                        uses a 404 status code.

    ``HttpResponseForbidden``           Acts just like ``HttpResponse`` but
                                        uses a 403 status code.

    ``HttpResponseNotAllowed``          Like ``HttpResponse``, but uses a 405
                                        status code. It takes a single, required
                                        argument: a list of permitted methods
                                        (e.g., ``['GET', 'POST']``).

    ``HttpResponseGone``                Acts just like ``HttpResponse`` but
                                        uses a 410 status code.

    ``HttpResponseServerError``         Acts just like ``HttpResponse`` but
                                        uses a 500 status code.
    ==================================  =======================================

You can, of course, define your own ``HttpResponse`` subclass to support
different types of responses not supported out of the box.

Returning Errors
----------------

Returning HTTP error codes in Django is easy. We've already mentioned the
``HttpResponseNotFound``, ``HttpResponseForbidden``,
``HttpResponseServerError``, and other subclasses. Just return an instance of one
of those subclasses instead of a normal ``HttpResponse`` in order to signify
an error, for example::

    def my_view(request):
        # ...
        if foo:
            return HttpResponseNotFound('<h1>Page not found</h1>')
        else:
            return HttpResponse('<h1>Page was found</h1>')

Because a 404 error is by far the most common HTTP error, there's an easier
way to handle it.

When you return an error such as ``HttpResponseNotFound``, you're responsible
for defining the HTML of the resulting error page::

    return HttpResponseNotFound('<h1>Page not found</h1>')

For convenience, and because it's a good idea to have a consistent 404 error page
across your site, Django provides an ``Http404`` exception. If you raise
``Http404`` at any point in a view function, Django will catch it and return the
standard error page for your application, along with an HTTP error code 404.

Here's an example::

    from django.http import Http404

    def detail(request, poll_id):
        try:
            p = Poll.objects.get(pk=poll_id)
        except Poll.DoesNotExist:
            raise Http404
        return render(request, 'polls/detail.html', {'poll': p})

In order to use the ``Http404`` exception to its fullest, you should create a
template that is displayed when a 404 error is raised. This template should be
called ``404.html``, and it should be located in the top level of your template tree.

Customizing the 404 (Not Found) View
------------------------------------

When you raise an ``Http404`` exception, Django loads a special view devoted
to handling 404 errors. By default, it's the view
``django.views.defaults.page_not_found``, which loads and renders the template
``404.html``.

This means you need to define a ``404.html`` template in your root template
directory. This template will be used for all 404 errors.

This ``page_not_found`` view should suffice for 99% of Web applications, but
if you want to override the 404 view, you can specify ``handler404`` in your
URLconf, like so::

    from django.conf.urls.defaults import *

    urlpatterns = patterns('',
        ...
    )

    handler404 = 'mysite.views.my_custom_404_view'

Behind the scenes, Django determines the 404 view by looking for
``handler404``. By default, URLconfs contain the following line::

    from django.conf.urls.defaults import *

That takes care of setting ``handler404`` in the current module. As you can
see in ``django/conf/urls/defaults.py``, ``handler404`` is set to
``'django.views.defaults.page_not_found'`` by default.

There are three things to note about 404 views:

* The 404 view is also called if Django doesn't find a match after checking
  every regular expression in the URLconf.

* If you don't define your own 404 view -- and simply use the default,
  which is recommended -- you still have one obligation: to create a
  ``404.html`` template in the root of your template directory. The default
  404 view will use that template for all 404 errors.

* If ``DEBUG`` is set to ``True`` (in your settings module), then your 404
  view will never be used, and the traceback will be displayed instead.

Customizing the 500 (Server Error) View
---------------------------------------

Similarly, Django executes special-case behavior in the case of runtime errors
in view code. If a view results in an exception, Django will, by default, call
the view ``django.views.defaults.server_error``, which loads and renders the
template ``500.html``.

This means you need to define a ``500.html`` template in your root template
directory. This template will be used for all server errors.

This ``server_error`` view should suffice for 99% of Web applications, but if
you want to override the view, you can specify ``handler500`` in your
URLconf, like so::

    from django.conf.urls.defaults import *

    urlpatterns = patterns('',
        ...
    )

    handler500 = 'mysite.views.my_custom_error_view'
