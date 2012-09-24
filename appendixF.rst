==============================================
Appendix F: Built-in Template Tags and Filters 
==============================================

Chapter 4 lists a number of the most useful built-in template tags and
filters. However, Django ships with many more built-in tags and filters. This
appendix lists the ones that were included at the time this book was written,
but new tags get added fairly regularly.

The best reference to all the available tags and filters is directly in your
admin interface. Django's admin interface includes a complete reference of all
tags and filters available for a given site. To see it, go to your admin
interface and click the Documentation link at the upper right of the page.

The tags and filters sections of the built-in documentation describe all the
built-in tags (in fact, the tag and filter references in this appendix come
directly from those pages) as well as any custom tag libraries available.

For those without an admin site available, reference for the stock tags and
filters follows. Because Django is highly customizable, the reference in your
admin site should be considered the final word on the available tags and
filters and what they do.

Built-in Tag Reference
======================

block
-----

Defines a block that can be overridden by child templates. See the section
on template inheritance in Chapter 4 for more information.

comment
-------

Ignores everything between ``{% comment %}`` and ``{% endcomment %}``.

cycle
-----

Cycles among the given strings each time this tag is encountered.

Within a loop, it cycles among the given strings each time through the loop::

    {% for o in some_list %}
        <tr class="{% cycle row1,row2 %}">
            ...
        </tr>
    {% endfor %}

Outside of a loop, give the values a unique name the first time you call it, and
then use that name each successive time through::

        <tr class="{% cycle row1,row2,row3 as rowcolors %}">...</tr>
        <tr class="{% cycle rowcolors %}">...</tr>
        <tr class="{% cycle rowcolors %}">...</tr>

You can use any number of values, separated by commas. Make sure not to put
spaces between the values -- only commas.

debug
-----

Outputs a whole load of debugging information, including the current context and
imported modules.

extends
-------

Signals that this template extends a parent template.

This tag can be used in two ways:

   * ``{% extends "base.html" %}`` (with quotes) uses the literal value
     ``"base.html"`` as the name of the parent template to extend.

   * ``{% extends variable %}`` uses the value of ``variable``. If the variable
     evaluates to a string, Django will use that string as the name of the
     parent template. If the variable evaluates to a ``Template`` object,
     Django will use that object as the parent template.

See Chapter 4 for many usage examples.

filter
------

Filters the contents of the variable through variable filters.

Filters can also be piped through each other, and they can have arguments --
just like in variable syntax.

Here's a sample usage::

    {% filter escape|lower %}
        This text will be HTML-escaped, and will appear in all lowercase.
    {% endfilter %}

firstof
-------

Outputs the first variable passed that is not ``False``. Outputs nothing if all
the passed variables are ``False``.

Here's a sample usage::

    {% firstof var1 var2 var3 %}

This is equivalent to the following::

    {% if var1 %}
        {{ var1 }}
    {% else %}{% if var2 %}
        {{ var2 }}
    {% else %}{% if var3 %}
        {{ var3 }}
    {% endif %}{% endif %}{% endif %}

for
---

Loops over each item in an array. For example, to display a list of athletes
given ``athlete_list``::

    <ul>
    {% for athlete in athlete_list %}
        <li>{{ athlete.name }}</li>
    {% endfor %}
    </ul>

You can also loop over a list in reverse by using ``{% for obj in list reversed %}``.

The ``for`` loop sets a number of variables available within the loop (see Table F-1).

.. table:: Table F-1. Variables Available Inside {% for %} Loops

    ==========================  ====================================================
    Variable                    Description
    ==========================  ====================================================
    ``forloop.counter``         The current iteration of the loop (1-indexed).
    ``forloop.counter0``        The current iteration of the loop (0-indexed).
    ``forloop.revcounter``      The number of iterations from the end of the
                                loop (1-indexed).
    ``forloop.revcounter0``     The number of iterations from the end of the
                                loop (0-indexed).
    ``forloop.first``           ``True`` if this is the first time through the loop.
    ``forloop.last``            ``True`` if this is the last time through the loop.
    ``forloop.parentloop``      For nested loops, this is the loop "above" the
                                current one.
    ==========================  ====================================================

if
--

The ``{% if %}`` tag evaluates a variable, and if that variable is "true" (i.e., it
exists, is not empty, and is not a false Boolean value), the contents of the
block are output::

    {% if athlete_list %}
        Number of athletes: {{ athlete_list|length }}
    {% else %}
        No athletes.
    {% endif %}

If ``athlete_list`` is not empty, the number of athletes will be
displayed by the ``{{ athlete_list|length }}`` variable.

As you can see, the ``if`` tag can take an optional ``{% else %}`` clause that
will be displayed if the test fails.

``if`` tags may use ``and``, ``or``, or ``not`` to test a number of variables or
to negate a given variable::

    {% if athlete_list and coach_list %}
        Both athletes and coaches are available.
    {% endif %}

    {% if not athlete_list %}
        There are no athletes.
    {% endif %}

    {% if athlete_list or coach_list %}
        There are some athletes or some coaches.
    {% endif %}

    {% if not athlete_list or coach_list %}
        There are no athletes or there are some coaches (OK, so
        writing English translations of Boolean logic sounds
        stupid; it's not our fault).
    {% endif %}

    {% if athlete_list and not coach_list %}
        There are some athletes and absolutely no coaches.
    {% endif %}

``if`` tags don't allow ``and`` and ``or`` clauses within the same tag, because
the order of logic would be ambiguous. For example, this is invalid::

    {% if athlete_list and coach_list or cheerleader_list %}

If you need to combine ``and`` and ``or`` to do advanced logic, just use nested
``if`` tags, for example::

    {% if athlete_list %}
        {% if coach_list or cheerleader_list %}
            We have athletes, and either coaches or cheerleaders!
        {% endif %}
    {% endif %}

Multiple uses of the same logical operator are fine, as long as you use the
same operator. For example, this is valid::

    {% if athlete_list or coach_list or parent_list or teacher_list %}

ifchanged
---------

Checks if a value has changed from the last iteration of a loop.

The ``ifchanged`` block tag is used within a loop. It has two possible uses:

1. It checks its own rendered contents against its previous state and only
   displays the content if it has changed. For example, this displays a list of
   days, only displaying the month if it changes::

        <h1>Archive for {{ year }}</h1>

        {% for date in days %}
            {% ifchanged %}<h3>{{ date|date:"F" }}</h3>{% endifchanged %}
            <a href="{{ date|date:"M/d"|lower }}/">{{ date|date:"j" }}</a>
        {% endfor %}

2. If given a variable, it checks whether that variable has changed:: 

        {% for date in days %}
            {% ifchanged date.date %} {{ date.date }} {% endifchanged %}
            {% ifchanged date.hour date.date %}
                {{ date.hour }}
            {% endifchanged %}
        {% endfor %}

   The preceding shows the date every time it changes, but it only shows the hour if
   both the hour and the date have changed.

ifequal
-------

Outputs the contents of the block if the two arguments equal each other.

Here's an example::

    {% ifequal user.id comment.user_id %}
        ...
    {% endifequal %}

As in the ``{% if %}`` tag, an ``{% else %}`` clause is optional.

The arguments can be hard-coded strings, so the following is valid::

    {% ifequal user.username "adrian" %}
        ...
    {% endifequal %}

It is only possible to compare an argument to template variables or strings.
You cannot check for equality with Python objects such as ``True`` or
``False``.  If you need to test if something is true or false, use the ``if``
tag instead.

ifnotequal
----------

Just like ``ifequal``, except it tests that the two arguments are *not* equal.

include
-------

Loads a template and renders it with the current context. This is a way of
"including" other templates within a template.

The template name can be either a variable or a hard-coded (quoted) string,
in either single or double quotes.

This example includes the contents of the template ``"foo/bar.html"``::

    {% include "foo/bar.html" %}

This example includes the contents of the template whose name is contained in
the variable ``template_name``::

    {% include template_name %}

load
----

Loads a custom template library. See Chapter 10 for information about custom
template libraries.

now
---

Displays the date, formatted according to the given string.

This tag was inspired by, and uses the same format as, a PHP's ``date()`` function
(http://php.net/date). Django's version, however, has some custom extensions.

Table F-2 shows the available format strings.

.. table:: Table F-2. Available Date Format Strings

    ================  ========================================  ============================================================================
    Format Character  Description                               Example Output
    ================  ========================================  ============================================================================
    a                 ``'a.m.'`` or ``'p.m.'``. (Note that       ``'a.m.'``
                      this is slightly different from PHP's
                      output, because this includes periods
                      to match Associated Press style.)
    
    A                 ``'AM'`` or ``'PM'``.                     ``'AM'``
    
    b                 Month, textual, three letters,            ``'jan'``
                      lowercase
    
    d                 Day of the month, two digits with         ``'01'`` to ``'31'``
                      leading zeros.
    
    D                 Day of the week, textual, three letters.  ``'Fri'``
    
    f                 Time, in 12-hour hours and minutes,       ``'1'``, ``'1:30'``
                      with minutes left off if they're zero.
    
    F                 Month, textual, long.                     ``'January'``
    
    g                 Hour, 12-hour format without leading      ``'1'`` to ``'12'``
                      zeros.
    
    G                 Hour, 24-hour format without leading      ``'0'`` to ``'23'``
                      zeros.
    
    h                 Hour, 12-hour format.                     ``'01'`` to ``'12'``
    
    H                 Hour, 24-hour format.                     ``'00'`` to ``'23'``
    
    i                 Minutes.                                  ``'00'`` to ``'59'``
        
    j                 Day of the month without leading          ``'1'`` to ``'31'``
                      zeros.
    
    l                 Day of the week, textual, long.           ``'Friday'``
    
    L                 Boolean for whether it's a leap year.     ``True`` or ``False``
    
    m                 Month, two digits with leading zeros.     ``'01'`` to ``'12'``
    
    M                 Month, textual, three letters.            ``'Jan'``
    
    n                 Month without leading zeros.              ``'1'`` to ``'12'``
    
    N                 Month abbreviation in Associated Press    ``'Jan.'``, ``'Feb.'``, ``'March'``, ``'May'``
                      style.
    
    O                 Difference to Greenwich Mean Time         ``'+0200'``
                      in hours.

    P                 Time, in 12-hour hours, minutes, and      ``'1 a.m.'``, ``'1:30 p.m.'``, ``'midnight'``, ``'noon'``, ``'12:30 p.m.'``
                      a.m./p.m., with minutes left off
                      if they're zero and the special-case
                      strings ``'midnight'`` and ``'noon'`` if
                      appropriate.
    
    r                 RFC 822 formatted date.                   ``'Thu, 21 Dec 2000 16:01:07 +0200'``
    
    s                 Seconds, two digits with leading zeros.   ``'00'`` to ``'59'``
    
    S                 English ordinal suffix for day of the     ``'st'``, ``'nd'``, ``'rd'`` or ``'th'``
                      month, two characters.
    
    t                 Number of days in the given month.        ``28`` to ``31``
    
    T                 Time zone of this machine.                ``'EST'``, ``'MDT'``
        
    w                 Day of the week, digits without           ``'0'`` (Sunday) to ``'6'`` (Saturday)
                      leading zeros.
    
    W                 ISO-8601 week number of year, with        ``1``, ``23``
                      weeks starting on Monday.
    
    y                 Year, two digits.                         ``'99'``
    
    Y                 Year, four digits.                        ``'1999'``
    
    z                 Day of the year.                          ``0`` to ``365``
    
    Z                 Time zone offset in seconds. The          ``-43200`` to ``43200``
                      offset for time zones west of UTC is
                      always negative, and for those east of
                      UTC it is always positive.
    ================  ========================================  ============================================================================

Here's an example::

    It is {% now "jS F Y H:i" %}

Note that you can backslash-escape a format string if you want to use the "raw"
value. In this example, "f" is backslash-escaped, because otherwise "f" is a
format string that displays the time. The "o" doesn't need to be escaped,
because it's not a format character::

    It is the {% now "jS o\f F" %}

This would display as "It is the 4th of September".

regroup
-------

Regroups a list of alike objects by a common attribute.

This complex tag is best illustrated by use of an example. Say that ``people``
is a list of ``Person`` objects that have ``first_name``, ``last_name``, and
``gender`` attributes, and you'd like to display a list that looks like this::

    * Male:
        * George Bush
        * Bill Clinton
    * Female:
        * Margaret Thatcher
        * Condoleezza Rice
    * Unknown:
        * Pat Smith

The following snippet of template code would accomplish this dubious task::

    {% regroup people by gender as grouped %}
    <ul>
    {% for group in grouped %}
        <li>{{ group.grouper }}
        <ul>
            {% for item in group.list %}
            <li>{{ item }}</li>
            {% endfor %}
        </ul>
        </li>
    {% endfor %}
    </ul>

As you can see, ``{% regroup %}`` populates a variable with a list of objects
with ``grouper`` and ``list`` attributes. ``grouper`` contains the item that was
grouped by; ``list`` contains the list of objects that share that ``grouper``.
In this case, ``grouper`` would be ``Male``, ``Female``, and ``Unknown``, and
``list`` is the list of people with those genders.

Note that ``{% regroup %}`` does not work when the list to be grouped is not
sorted by the key you are grouping by! This means that if your list of people
was not sorted by gender, you'd need to make sure it is sorted before using it,
that is::

    {% regroup people|dictsort:"gender" by gender as grouped %}

spaceless
---------

Removes whitespace between HTML tags. This includes tab
characters and newlines.

Here's an example::

    {% spaceless %}
        <p>
            <a href="foo/">Foo</a>
        </p>
    {% endspaceless %}

This example would return this HTML::

    <p><a href="foo/">Foo</a></p>

Only space between *tags* is removed -- not space between tags and text. In
this example, the space around ``Hello`` won't be stripped::

    {% spaceless %}
        <strong>
            Hello
        </strong>
    {% endspaceless %}

ssi
---

Outputs the contents of a given file into the page.

Like a simple "include" tag, ``{% ssi %}`` includes the contents of another
file -- which must be specified using an absolute path -- in the current
page::

    {% ssi /home/html/ljworld.com/includes/right_generic.html %}

If the optional "parsed" parameter is given, the contents of the included
file are evaluated as template code, within the current context::

    {% ssi /home/html/ljworld.com/includes/right_generic.html parsed %}

Note that if you use ``{% ssi %}``, you'll need to define
`ALLOWED_INCLUDE_ROOTS` in your Django settings, as a security measure.

Most of the time ``{% include %}`` works better than ``{% ssi %}``; ``{% ssi
%}`` exists mostly for backward compatibility.

templatetag
-----------

Outputs one of the syntax characters used to compose template tags.

Since the template system has no concept of "escaping," to display one of the
bits used in template tags, you must use the ``{% templatetag %}`` tag.

The argument tells which template bit to output (see Table F-3).

.. table:: Table F-3. Valid Arguments to templatetag

    ==================  =======
    Argument            Output
    ==================  =======
    ``openblock``       ``{%``
    ``closeblock``      ``%}``
    ``openvariable``    ``{{``
    ``closevariable``   ``}}``
    ``openbrace``       ``{``
    ``closebrace``      ``}``
    ``opencomment``     ``{#``
    ``closecomment``    ``#}``
    ==================  =======

url
---

Returns an absolute URL (i.e., a URL without the domain name) matching a given
view function and optional parameters. This is a way to output links without
violating the DRY principle by having to hard-code URLs in your templates::

    {% url path.to.some_view arg1,arg2,name1=value1 %}

The first argument is a path to a view function in the format
``package.package.module.function``. Additional arguments are optional and
should be comma-separated values that will be used as positional and keyword
arguments in the URL. All arguments required by the URLconf should be present.

For example, suppose you have a view, ``app_name.client``, whose URLconf takes
a client ID. The URLconf line might look like this::

    ('^client/(\d+)/$', 'app_name.client')

If this application's URLconf is included into the project's URLconf under a path
such as this::

    ('^clients/', include('project_name.app_name.urls'))

then, in a template, you can create a link to this view like this::

    {% url app_name.client client.id %}

The template tag will output the string ``/clients/client/123/``.

widthratio
----------

For creating bar charts and such, this tag calculates the ratio of a given value
to a maximum value, and then applies that ratio to a constant.

Here's an example::

    <img src="bar.gif" height="10" width="{% widthratio this_value max_value 100 %}" />

If ``this_value`` is 175 and ``max_value`` is 200, the image in the
preceding example will be 88 pixels wide (because 175/200 = .875; .875 * 100 = 87.5,
which is rounded up to 88).

Built-in Filter Reference
=========================

add
---

Example::

    {{ value|add:"5" }}

Adds the argument to the value.

addslashes
----------

Example::

    {{ string|addslashes }}

Adds backslashes before single and double quotes. This is useful for passing strings to
JavaScript, for example.

capfirst
--------

Example::

    {{ string|capfirst }}

Capitalizes the first character of the string.

center
------

Example::

    {{ string|center:"50" }}

Centers the string in a field of a given width.

cut
---

Example::

    {{ string|cut:"spam" }}

Removes all values of the argument from the given string.

date
----

Example::

    {{ value|date:"F j, Y" }}

Formats a date according to the given format (same as the ``now`` tag).

default
-------

Example::

    {{ value|default:"(N/A)" }}

If the value is unavailable, use the given default.

default_if_none
---------------

Example::

    {{ value|default_if_none:"(N/A)" }}

If the value is ``None``, use the given default.

dictsort
--------

Example::

    {{ list|dictsort:"foo" }}

Takes a list of dictionaries and returns that list sorted by the property given in
the argument.

dictsortreversed
------------------

Example::

    {{ list|dictsortreversed:"foo" }}

Takes a list of dictionaries and returns that list sorted in reverse order by the
property given in the argument.

divisibleby
------------

Example::

    {% if value|divisibleby:"2" %}
        Even!
    {% else %}
        Odd!
    {% else %}

Returns ``True`` if the value is divisible by the argument.

escape
------

Example::

    {{ string|escape }}

Escapes a string's HTML. Specifically, it makes these replacements:

    * ``"&"`` to ``"&amp;"``
    * ``<`` to ``"&lt;"``
    * ``>`` to ``"&gt;"``
    * ``'"'`` (double quote) to ``'&quot;'``
    * ``"'"`` (single quote) to ``'&#39;'``

filesizeformat
--------------

Example::

    {{ value|filesizeformat }}

Formats the value like a "human-readable" file size (i.e., ``'13 KB'``,
``'4.1 MB'``, ``'102 bytes'``, etc).

first
-----

Example::

    {{ list|first }}

Returns the first item in a list.

fix_ampersands
---------------

Example::

    {{ string|fix_ampersands }}

Replaces ampersands with ``&amp;`` entities.

floatformat
-----------

Examples::

    {{ value|floatformat }}
    {{ value|floatformat:"2" }}

When used without an argument, rounds a floating-point number to one decimal
place -- but only if there's a decimal part to be displayed, for example:

    * ``36.123`` gets converted to ``36.1``.
    * ``36.15`` gets converted to ``36.2``.
    * ``36`` gets converted to ``36``.

If used with a numeric integer argument, ``floatformat`` rounds a number to that
many decimal places:

    * ``36.1234`` with floatformat:3 gets converted to ``36.123``.
    * ``36`` with floatformat:4 gets converted to ``36.0000``.

If the argument passed to ``floatformat`` is negative, it will round a number to
that many decimal places -- but only if there's a decimal part to be displayed:

    * ``36.1234`` with floatformat:-3 gets converted to ``36.123``.
    * ``36`` with floatformat:-4 gets converted to ``36``.

Using ``floatformat`` with no argument is equivalent to using ``floatformat`` with
an argument of ``-1``.

get_digit
---------

Example::

    {{ value|get_digit:"1" }}

Given a whole number, returns the requested digit of it, where 1 is the
rightmost digit, 2 is the second-to-rightmost digit, and so forth. It returns the original
value for invalid input (if the input or argument is not an integer, or if the argument
is less than 1). Otherwise, output is always an integer.

join
----

Example::

    {{ list|join:", " }}

Joins a list with a string, like Python's ``str.join(list)``.

length
------

Example::

    {{ list|length }}

Returns the length of the value.

length_is
---------

Example::

    {% if list|length_is:"3" %}
        ...
    {% endif %}

Returns a Boolean of whether the value's length is the argument.

linebreaks
----------

Example::

    {{ string|linebreaks }}

Converts newlines into ``<p>`` and ``<br />`` tags.

linebreaksbr
------------

Example::

    {{ string|linebreaksbr }}

Converts newlines into ``<br />`` tags.

linenumbers
-----------

Example::

    {{ string|linenumbers }}

Displays text with line numbers.

ljust
-----

Example::

    {{ string|ljust:"50" }}

Left-aligns the value in a field of a given width.

lower
-----

Example::

    {{ string|lower }}

Converts a string into all lowercase.

make_list
---------

Example::

    {% for i in number|make_list %}
        ...
    {% endfor %}

Returns the value turned into a list. For an integer, it's a list of
digits. For a string, it's a list of characters.

phone2numeric
-------------

Example::

    {{ string|phone2numeric }}

Converts a phone number (possibly containing letters) to its numerical
equivalent. For example, ``'800-COLLECT'`` will be converted to
``'800-2655328'``.

The input doesn't have to be a valid phone number. This will happily convert
any string.

pluralize
---------

Example::

    The list has {{ list|length }} item{{ list|pluralize }}.

Returns a plural suffix if the value is not 1. By default, this suffix is ``'s'``.

Example::

    You have {{ num_messages }} message{{ num_messages|pluralize }}.

For words that require a suffix other than ``'s'``, you can provide an alternate
suffix as a parameter to the filter.

Example::

    You have {{ num_walruses }} walrus{{ num_walrus|pluralize:"es" }}.

For words that don't pluralize by simple suffix, you can specify both a
singular and plural suffix, separated by a comma.

Example::

    You have {{ num_cherries }} cherr{{ num_cherries|pluralize:"y,ies" }}.

pprint
------

Example::

    {{ object|pprint }}

A wrapper around Python's built-in ``pprint.pprint`` -- for debugging, really.

random
------

Example::

    {{ list|random }}

Returns a random item from the list.

removetags
----------

Example::

    {{ string|removetags:"br p div" }}

Removes a space-separated list of [X]HTML tags from the output.

rjust
-----

Example::

    {{ string|rjust:"50" }}

Right-aligns the value in a field of a given width.

slice
-----

Example:: 

    {{ some_list|slice:":2" }}

Returns a slice of the list.

Uses the same syntax as Python's list slicing. See
http://diveintopython.org/native_data_types/lists.html#odbchelper.list.slice for
an introduction.

slugify
-------

Example::

    {{ string|slugify }}

Converts to lowercase, removes nonword characters (alphanumerics and
underscores), and converts spaces to hyphens. It also strips leading and trailing
whitespace.

stringformat
------------

Example::

    {{ number|stringformat:"02i" }}

Formats the variable according to the argument, a string formatting specifier.
This specifier uses Python string-formatting syntax, with the exception that the
leading "%" is dropped.

See http://docs.python.org/lib/typesseq-strings.html for documentation of Python
string formatting.

striptags
---------

Example::

    {{ string|striptags }}

Strips all [X]HTML tags.

time
----

Example::

    {{ value|time:"P" }}

Formats a time according to the given format (same as the ``now`` tag).

timesince
---------

Examples::

    {{ datetime|timesince }}
    {{ datetime|timesince:"other_datetime" }}

Formats a date as the time since that date (e.g., "4 days, 6 hours").

Takes an optional argument that is a variable containing the date to use as
the comparison point (without the argument, the comparison point is *now*).
For example, if ``blog_date`` is a date instance representing midnight on 1
June 2006, and ``comment_date`` is a date instance for 08:00 on 1 June 2006,
then ``{{ comment_date|timesince:blog_date }}`` would return "8 hours".

timeuntil
---------

Examples::

    {{ datetime|timeuntil }}
    {{ datetime|timeuntil:"other_datetime" }}

Similar to ``timesince``, except that it measures the time from now until the
given date or datetime. For example, if today is 1 June 2006 and
``conference_date`` is a date instance holding 29 June 2006, then
``{{ conference_date|timeuntil }}`` will return "28 days".

Takes an optional argument that is a variable containing the date to use as
the comparison point (instead of *now*). If ``from_date`` contains 22 June
2006, then ``{{ conference_date|timeuntil:from_date }}`` will return "7 days".

title
-----

Example::

    {{ string|titlecase }}

Converts a string into title case.

truncatewords
-------------

Example::

    {{ string|truncatewords:"15" }}

Truncates a string after a certain number of words.

truncatewords_html
------------------

Example::

    {{ string|truncatewords_html:"15" }}

Similar to ``truncatewords``, except that it is aware of HTML tags. Any tags
that are opened in the string and not closed before the truncation point are
closed immediately after the truncation.

This is less efficient than ``truncatewords``, so it should be used only when it
is being passed HTML text.

unordered_list
--------------

Example::
    
    <ul>
        {{ list|unordered_list }}
    </ul>

Recursively takes a self-nested list and returns an HTML unordered list --
*without* opening and closing <ul> tags.

The list is assumed to be in the proper format. For example, if ``var`` contains
``['States', [['Kansas', [['Lawrence', []], ['Topeka', []]]], ['Illinois', []]]]``,
then ``{{ var|unordered_list }}`` would return the following::

    <li>States
    <ul>
            <li>Kansas
            <ul>
                    <li>Lawrence</li>
                    <li>Topeka</li>
            </ul>
            </li>
            <li>Illinois</li>
    </ul>
    </li>

upper
-----

Example::
    
    {{ string|upper }}

Converts a string into all uppercase.

urlencode
---------

Example::

    <a href="{{ link|urlencode }}">linkage</a>

Escapes a value for use in a URL.

urlize
------

Example::

    {{ string|urlize }}

Converts URLs in plain text into clickable links.

urlizetrunc
------------

Example::

    {{ string|urlizetrunc:"30" }}

Converts URLs into clickable links, truncating URLs to the given character limit.

wordcount
---------

Example::

    {{ string|wordcount }}

Returns the number of words.

wordwrap
--------

Example::

    {{ string|wordwrap:"75" }}

Wraps words at a specified line length.

yesno
-----

Example::

    {{ boolean|yesno:"Yes,No,Perhaps" }}

Given a string mapping values for ``True``, ``False``, and (optionally) ``None``,
returns one of those strings according to the value (see Table F-4).

.. table:: Table F-4. Examples of the yesno Filter

    ==========  ======================  ========================================
    Value       Argument                Output
    ==========  ======================  ========================================
    ``True``    ``"yeah,no,maybe"``     ``yeah``
    
    ``False``   ``"yeah,no,maybe"``     ``no``
    
    ``None``    ``"yeah,no,maybe"``     ``maybe``
    
    ``None``    ``"yeah,no"``           ``"no"`` (converts ``None`` to ``False``
                                        if no mapping for ``None`` is given)
    ==========  ======================  ========================================
