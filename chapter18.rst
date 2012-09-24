================================
Chapter 18: Internationalization
================================

Django was originally developed smack in the middle of the United States
(literally; Lawrence, Kansas, is less than 40 miles from the geographic center
of the continental United States). Like most open source projects, though,
Django's community grew to include people from all over the globe. As Django's
community became increasingly diverse, *internationalization* and
*localization* became increasingly important. Since many developers have at
best a fuzzy understanding of these terms, we'll define them briefly.

*Internationalization* refers to the process of designing programs for the
potential use of any locale. This includes marking text (like UI elements and
error messages) for future translation, abstracting the display of dates and
times so that different local standards may be observed, providing support for
differing time zones, and generally making sure that the code contains no
assumptions about the location if its users. You'll often see
"internationalization" abbreviated *I18N* (the number 18 refers to the number
of letters omitted between the initial "I" and the terminal "N").

*Localization* refers to the process of actually translating an
internationalized program for use in a particular locale. You'll sometimes see
"localization" abbreviated as *L10N*.

Django itself is fully internationalized; all strings are marked for
translation, and settings control the display of locale-dependent values like
dates and times. Django also ships with over 40 different localization files.
If you're not a native English speaker, there's a good chance that Django is
already is translated into your primary language.

The same internationalization framework used for these localizations is
available for you to use in your own code and templates.

In a nutshell, you'll need to add a minimal number of hooks to your Python
code and templates. These hooks are called *translation strings*. They tell
Django, "This text should be translated into the end user's language, if a
translation for this text is available in that language."

Django takes care of using these hooks to translate Web applications, on the
fly, according to users' language preferences.

Essentially, Django does two things:

    * It lets developers and template authors specify which parts of their
      applications should be translatable.
      
    * It uses that information to translate Web applications for particular
      users according to their language preferences.

.. note:: 

    Django's translation machinery uses GNU ``gettext``
    (http://www.gnu.org/software/gettext/) via the standard ``gettext`` module
    that comes with Python.
    
.. admonition:: If You Don't Need Internationalization:

    Django's internationalization hooks are enabled by default, which incurs a
    small bit of overhead. If you don't use internationalization, you should
    set ``USE_I18N = False`` in your settings file. If ``USE_I18N`` is set to
    ``False``, then Django will make some optimizations so as not to load the
    internationalization machinery.
    
    You'll probably also want to remove
    ``'django.core.context_processors.i18n'`` from your
    ``TEMPLATE_CONTEXT_PROCESSORS`` setting.

Specifying Translation Strings in Python Code
=============================================

Translation strings specify "This text should be translated." These strings can
appear in your Python code and templates. It's your responsibility to mark
translatable strings; the system can only translate strings it knows about.

Standard Translation Functions
------------------------------

Specify a translation string by using the function ``_()``. (Yes, the name of
the function is the underscore character.) This function is available globally
(i.e., as a built-in language); you don't have to import it.

In this example, the text ``"Welcome to my site."`` is marked as a translation
string::

    def my_view(request):
        output = _("Welcome to my site.")
        return HttpResponse(output)

The function ``django.utils.translation.gettext()`` is identical to ``_()``.
This example is identical to the previous one::

    from django.utils.translation import gettext
    def my_view(request):
        output = gettext("Welcome to my site.")
        return HttpResponse(output)
        
Most developers prefer to use ``_()``, as it's shorter.

Translation works on computed values. This example is identical to the previous
two::

    def my_view(request):
        words = ['Welcome', 'to', 'my', 'site.']
        output = _(' '.join(words))
        return HttpResponse(output)

Translation works on variables. Again, here's an identical example::

    def my_view(request):
        sentence = 'Welcome to my site.'
        output = _(sentence)
        return HttpResponse(output)

(The caveat with using variables or computed values, as in the previous two
examples, is that Django's translation-string-detecting utility,
``make-messages.py``, won't be able to find these strings. More on
``make-messages`` later.)

The strings you pass to ``_()`` or ``gettext()`` can take placeholders,
specified with Python's standard named-string interpolation syntax, for example::

    def my_view(request, n):
        output = _('%(name)s is my name.') % {'name': n}
        return HttpResponse(output)

This technique lets language-specific translations reorder the placeholder
text. For example, an English translation may be ``"Adrian is my name."``,
while a Spanish translation may be ``"Me llamo Adrian."``, with the
placeholder (the name) placed after the translated text instead of before it.

For this reason, you should use named-string interpolation (e.g., ``%(name)s``)
instead of positional interpolation (e.g., ``%s`` or ``%d``). If you use
positional interpolation, translations won't be able to reorder placeholder
text.

Marking Strings As No-op
------------------------

Use the function ``django.utils.translation.gettext_noop()`` to mark a string as
a translation string without actually translating it at that moment. Strings
thus marked aren't translated until the last possible moment.

Use this approach if you have constant strings that should be stored in the original
language -- such as strings in a database -- but should be translated at the
last possible point in time, such as when the string is presented to the user.

Lazy Translation
----------------

Use the function ``django.utils.translation.gettext_lazy()`` to translate
strings lazily -- when the value is accessed rather than when the
``gettext_lazy()`` function is called.

For example, to mark a fields's ``help_text`` attribute as translatable, do
the following::

    from django.utils.translation import gettext_lazy

    class MyThing(models.Model):
        name = models.CharField(help_text=gettext_lazy('This is the help text'))

In this example, ``gettext_lazy()`` stores a lazy reference to the string --
not the actual translation. The translation itself will be done when the string
is used in a string context, such as template rendering on the Django admin site.

If you don't like the verbose name ``gettext_lazy``, you can just alias it as
``_`` (underscore), like so::

    from django.utils.translation import gettext_lazy as _

    class MyThing(models.Model):
        name = models.CharField(help_text=_('This is the help text'))

Always use lazy translations in Django models (otherwise they won't be
translated correctly on a per-user basis). And it's a good idea to add
translations for the field names and table names, too. This means writing
explicit ``verbose_name`` and ``verbose_name_plural`` options in the ``Meta``
class::

    from django.utils.translation import gettext_lazy as _

    class MyThing(models.Model):
        name = models.CharField(_('name'), help_text=_('This is the help text'))
        class Meta:
            verbose_name = _('my thing')
            verbose_name_plural = _('mythings')

Pluralization
-------------

Use the function ``django.utils.translation.ngettext()`` to specify messages that
have different singular and plural forms, for example::

    from django.utils.translation import ngettext
    def hello_world(request, count):
        page = ngettext(
            'there is %(count)d object', 
            'there are %(count)d objects', count
        ) % {'count': count}
        return HttpResponse(page)

``ngettext`` takes three arguments: the singular translation string, the plural
translation string, and the number of objects (which is passed to the translation
languages as the ``count`` variable).

Specifying Translation Strings in Template Code
===============================================

Using translations in Django templates uses two template tags and a slightly
different syntax than in Python code. To give your template access to these
tags, put ``{% load i18n %}`` toward the top of your template.

The ``{% trans %}`` template tag marks a string for translations::

    <title>{% trans "This is the title." %}</title>

If you only want to mark a value for translation, but translate it later, use the ``noop`` option::

    <title>{% trans "value" noop %}</title>

It's not possible to use template variables in ``{% trans %}`` -- only constant
strings, in single or double quotes, are allowed. If your translations require
variables (placeholders), use ``{% blocktrans %}``, for example::

    {% blocktrans %}This will have {{ value }} inside.{% endblocktrans %}

To translate a template expression -- say, using template filters -- you need
to bind the expression to a local variable for use within the translation
block::

    {% blocktrans with value|filter as myvar %}
      This will have {{ myvar }} inside.
    {% endblocktrans %}

If you need to bind more than one expression inside a ``blocktrans`` tag,
separate the pieces with ``and``::

    {% blocktrans with book|title as book_t and author|title as author_t %}
      This is {{ book_t }} by {{ author_t }}
    {% endblocktrans %}

To pluralize, specify both the singular and plural forms with the
``{% plural %}`` tag, which appears within ``{% blocktrans %}`` and
``{% endblocktrans %}``, for example::

    {% blocktrans count list|length as counter %}
      There is only one {{ name }} object.
    {% plural %}
      There are {{ counter }} {{ name }} objects.
    {% endblocktrans %}

Internally, all block and inline translations use the appropriate 
``gettext``/``ngettext`` call.

When you use ``RequestContext`` (see `Chapter 10`_), your templates have access to
three translation-specific variables:


    * ``{{ LANGUAGES }}`` is a list of tuples in which the first element is
      the language code and the second is the language name (in that
      language).
    
    * ``{{ LANGUAGE_CODE }}`` is the current user's preferred language, as a
      string (e.g., ``en-us``). (See the "How Django Discovers Language
      Preference" section for more information.)

    * ``{{ LANGUAGE_BIDI }}`` is the current language's writing system. If
      ``True``, it's a right-to-left language (e.g., Hebrew, Arabic). If
      ``False``, it's a left-to-right language (e.g., English, French,
      German).

You can also load these values using template tags::

    {% load i18n %}
    {% get_current_language as LANGUAGE_CODE %}
    {% get_available_languages as LANGUAGES %}
    {% get_current_language_bidi as LANGUAGE_BIDI %}

Translation hooks are also available within any template block tag that accepts
constant strings. In those cases, just use ``_()`` syntax to specify a
translation string, for example::

    {% some_special_tag _("Page not found") value|yesno:_("yes,no") %}

In this case, both the tag and the filter will see the already-translated string
(i.e., the string is translated *before* being passed to the tag handler
functions), so they don't need to be aware of translations.

.. _Chapter 10: ../chapter10/

Creating Language Files
=======================

Once you've tagged your strings for later translation, you need to write (or
obtain) the language translations themselves. In this section we explain how that works.

Creating Message Files
----------------------

The first step is to create a *message file* for a new language. A message
file is a plain-text file representing a single language that contains all
available translation strings and how they should be represented in the given
language. Message files have a ``.po`` file extension.

Django comes with a tool, ``bin/make-messages.py``, that automates the creation
and maintenance of these files.

To create or update a message file, run this command::

    bin/make-messages.py -l de

where ``de`` is the language code for the message file you want to create.
The language code, in this case, is in locale format. For example, it's
``pt_BR`` for Brazilian Portuguese and ``de_AT`` for Austrian German.
Take a look at thelanguage codes in the ``django/conf/locale/`` directory to see which
languages are currently supported.

The script should be run from one of three places:

    * The root ``django`` directory (not a Subversion checkout, but the one
      that is linked to via ``$PYTHONPATH`` or is located somewhere on that
      path)
    * The root directory of your Django project
    * The root directory of your Django application

The script runs over the entire tree it is run on and pulls out all strings
marked for translation. It creates (or updates) a message file in the directory
``conf/locale``. In the ``de`` example, the file will be
``conf/locale/de/LC_MESSAGES/django.po``.

If run over your project source tree or your application source tree, it will
do the same, but the location of the locale directory is ``locale/LANG/LC_MESSAGES``
(note the missing ``conf`` prefix).  The first time you run it on your tree
you'll need to create the ``locale`` directory.

.. admonition:: No gettext?

    If you don't have the ``gettext`` utilities installed, ``make-messages.py``
    will create empty files. If that's the case, either install the ``gettext``
    utilities or just copy the English message file
    (``conf/locale/en/LC_MESSAGES/django.po``) and use it as a starting point;
    it's just an empty translation file.

The format of ``.po`` files is straightforward. Each ``.po`` file contains a
small bit of metadata, such as the translation maintainer's contact
information, but the bulk of the file is a list of *messages* -- simple
mappings between translation strings and the actual translated text for the
particular language.

For example, if your Django application contains a translation string for the text
``"Welcome to my site."``, like so::

    _("Welcome to my site.")

then ``make-messages.py`` will have created a ``.po`` file containing the
following snippet -- a message::

    #: path/to/python/module.py:23
    msgid "Welcome to my site."
    msgstr ""

A quick explanation is in order:

    * ``msgid`` is the translation string, which appears in the source. Don't
      change it.
    * ``msgstr`` is where you put the language-specific translation. It starts
      out empty, so it's your responsibility to change it. Make sure you keep
      the quotes around your translation.
    * As a convenience, each message includes the file name and line number
      from which the translation string was gleaned.

Long messages are a special case. The first string directly after
``msgstr`` (or ``msgid``) is an empty string. Then the content itself will be
written over the next few lines as one string per line. Those strings are
directly concatenated. Don't forget trailing spaces within the strings;
otherwise, they'll be tacked together without whitespace!

For example, here's a multiline translation (taken from the Spanish
localization that ships with Django)::

    msgid ""
    "There's been an error. It's been reported to the site administrators via e-"
    "mail and should be fixed shortly. Thanks for your patience."
    msgstr ""
    "Ha ocurrido un error. Se ha informado a los administradores del sitio "
    "mediante correo electrónico y debería arreglarse en breve. Gracias por su "
    "paciencia."
    
Note the trailing spaces.

.. admonition:: Mind Your Charset

    When creating a ``.po`` file with your favorite text editor, first edit
    the charset line (search for ``"CHARSET"``) and set it to the charset
    you'll be using to edit the content. Generally, UTF-8 should work for most
    languages, but ``gettext`` should handle any charset you throw at it.

To reexamine all source code and templates for new translation strings and
update all message files for *all* languages, run this::

    make-messages.py -a

Compiling Message Files
-----------------------

After you create your message file, and each time you make changes to it,
you'll need to compile it into a more efficient form, for use by ``gettext``.
Do this with the ``bin/compile-messages.py`` utility.

This tool runs over all available ``.po`` files and creates ``.mo`` files,
which are binary files optimized for use by ``gettext``. In the same directory
from which you ran ``make-messages.py``, run ``compile-messages.py`` like
this::

   bin/compile-messages.py

That's it. Your translations are ready for use.

How Django Discovers Language Preference
========================================

Once you've prepared your translations -- or, if you just want to use the
translations that are included with Django -- you'll just need to activate
translation for your application.

Behind the scenes, Django has a very flexible model of deciding which language
should be used -- installation-wide, for a particular user, or both.

To set an installation-wide language preference, set ``LANGUAGE_CODE`` in your
settings file. Django uses this language as the default translation -- the
final attempt if no other translator finds a translation.  

If all you want to do is run Django with your native language, and a language
file is available for your language, simply set ``LANGUAGE_CODE``.

If you want to let each individual user specify the language he or she
prefers, use ``LocaleMiddleware``. ``LocaleMiddleware`` enables language
selection based on data from the request. It customizes content for each user.

To use ``LocaleMiddleware``, add ``'django.middleware.locale.LocaleMiddleware'``
to your ``MIDDLEWARE_CLASSES`` setting. Because middleware order matters, you
should follow these guidelines:

    * Make sure it's among the first middleware classes installed.
    
    * It should come after ``SessionMiddleware``, because ``LocaleMiddleware``
      makes use of session data.
      
    * If you use ``CacheMiddleware``, put ``LocaleMiddleware`` after it (otherwise
      users could get cached content from the wrong locale).

For example, your ``MIDDLEWARE_CLASSES`` might look like this::

    MIDDLEWARE_CLASSES = (
       'django.middleware.common.CommonMiddleware',    
       'django.contrib.sessions.middleware.SessionMiddleware',
       'django.middleware.locale.LocaleMiddleware'
    )

``LocaleMiddleware`` tries to determine the user's language preference by
following this algorithm:

    * First, it looks for a ``django_language`` key in the current user's
      session.
      
    * Failing that, it looks for a cookie called ``django_language``.
    
    * Failing that, it looks at the ``Accept-Language`` HTTP header. This
      header is sent by your browser and tells the server which language(s) you
      prefer, in order of priority. Django tries each language in the header
      until it finds one with available translations.
      
    * Failing that, it uses the global ``LANGUAGE_CODE`` setting.

In each of these places, the language preference is expected to be in the
standard language format, as a string. For example, Brazilian Portuguese is
``pt-br``. If a base language is available but the sub-language specified is
not, Django uses the base language. For example, if a user specifies ``de-at``
(Austrian German) but Django only has ``de`` available, Django uses ``de``.

Only languages listed in the ``LANGUAGES`` setting can be selected. If you want
to restrict the language selection to a subset of provided languages (because
your application doesn't provide all those languages), set your ``LANGUAGES``
setting to a list of languages, for example::

    LANGUAGES = (
        ('de', _('German')),
        ('en', _('English')),
    )

This example restricts languages that are available for automatic selection to
German and English (and any sub-language, like ``de-ch`` or ``en-us``).

If you define a custom ``LANGUAGES``, it's OK to mark the languages as
translation strings -- but use a "dummy" ``gettext()`` function, not the one in
``django.utils.translation``. You should *never* import
``django.utils.translation`` from within your settings file, because that module
itself depends on the settings, and that would cause a circular import.

The solution is to use a "dummy" ``gettext()`` function. Here's a sample
settings file::

    _ = lambda s: s

    LANGUAGES = (
          ('de', _('German')),
          ('en', _('English')),
    )

With this arrangement, ``make-messages.py`` will still find and mark these
strings for translation, but the translation won't happen at runtime, so
you'll have to remember to wrap the languages in the *real* ``gettext()`` in any
code that uses ``LANGUAGES`` at runtime.

The ``LocaleMiddleware`` can only select languages for which there is a
Django-provided base translation. If you want to provide translations for your
application that aren't already in the set of translations in Django's source
tree, you'll want to provide at least basic translations for that language. For
example, Django uses technical message IDs to translate date formats and time
formats -- so you will need at least those translations for the system to work
correctly.

A good starting point is to copy the English ``.po`` file and to translate at
least the technical messages, and maybe the validator messages, too.

Technical message IDs are easily recognized; they're all uppercase. You don't
translate the message ID as with other messages; rather, you provide the correct local
variant on the provided English value. For example, with ``DATETIME_FORMAT`` (or
``DATE_FORMAT`` or ``TIME_FORMAT``), this would be the format string that you
want to use in your language. The format is identical to the format strings used
by the ``now`` template tag.

Once ``LocaleMiddleware`` determines the user's preference, it makes this
preference available as ``request.LANGUAGE_CODE`` for each request object. Feel
free to read this value in your view code. Here's a simple example::

    def hello_world(request, count):
        if request.LANGUAGE_CODE == 'de-at':
            return HttpResponse("You prefer to read Austrian German.")
        else:
            return HttpResponse("You prefer to read another language.")

Note that, with static (i.e. without middleware) translation, the language is
in ``settings.LANGUAGE_CODE``, while with dynamic (middleware) translation,
it's in ``request.LANGUAGE_CODE``.

The set_language Redirect View
==============================

As a convenience, Django comes with a view, ``django.views.i18n.set_language``,
that sets a user's language preference and redirects back to the previous page.

Activate this view by adding the following line to your URLconf::

    (r'^i18n/', include('django.conf.urls.i18n')),

(Note that this example makes the view available at ``/i18n/setlang/``.)

The view expects to be called via the ``GET`` method, with a ``language``
parameter set in the query string. If session support is enabled, the view
saves the language choice in the user's session. Otherwise, it saves the
language choice in a ``django_language`` cookie.

After setting the language choice, Django redirects the user, following this
algorithm:

    * Django looks for a ``next`` parameter in the query string.
    * If that doesn't exist or is empty, Django tries the URL in the
      ``Referer`` header.
    * If that's empty -- say, if a user's browser suppresses that header --
      then the user will be redirected to ``/`` (the site root) as a fallback.

Here's example HTML template code::

    <form action="/i18n/setlang/" method="get">
    <input name="next" type="hidden" value="/next/page/" />
    <select name="language">
    {% for lang in LANGUAGES %}
    <option value="{{ lang.0 }}">{{ lang.1 }}</option>
    {% endfor %}
    </select>
    <input type="submit" value="Go" />
    </form>

Using Translations in Your Own Projects
=======================================

Django looks for translations by following this algorithm:

    * First, it looks for a ``locale`` directory in the application directory
      of the view that's being called. If it finds a translation for the
      selected language, the translation will be installed.
    * Next, it looks for a ``locale`` directory in the project directory. If it
      finds a translation, the translation will be installed.
    * Finally, it checks the base translation in ``django/conf/locale``.

This way, you can write applications that include their own translations, and
you can override base translations in your project path. Or, you can just build
a big project out of several applications and put all translations into one big project
message file. The choice is yours.

.. note::

    If you're using manually configured settings, the ``locale`` directory in
    the project directory will not be examined, since Django loses the ability
    to work out the location of the project directory. (Django normally uses
    the location of the settings file to determine this, and a settings file
    doesn't exist if you're manually configuring your settings.)

All message file repositories are structured the same way:

    * ``$APPPATH/locale/<language>/LC_MESSAGES/django.(po|mo)``
    * ``$PROJECTPATH/locale/<language>/LC_MESSAGES/django.(po|mo)``
    * All paths listed in ``LOCALE_PATHS`` in your settings file are
      searched in that order for ``<language>/LC_MESSAGES/django.(po|mo)``
    * ``$PYTHONPATH/django/conf/locale/<language>/LC_MESSAGES/django.(po|mo)``

To create message files, you use the same ``make-messages.py`` tool as with the
Django message files. You only need to be in the right place -- in the directory
where either the ``conf/locale`` (in case of the source tree) or the ``locale/``
(in case of application messages or project messages) directory is located. And you
use the same ``compile-messages.py`` to produce the binary ``django.mo`` files that
are used by ``gettext``.

Application message files are a bit complicated to discover -- they need the
``LocaleMiddleware``. If you don't use the middleware, only the Django message
files and project message files will be processed.

Finally, you should give some thought to the structure of your translation
files. If your applications need to be delivered to other users and will
be used in other projects, you might want to use application-specific translations.
But using application-specific translations and project translations could produce
weird problems with ``make-messages``. ``make-messages`` will traverse all
directories below the current path and so might put message IDs into the
project message file that are already in application message files.

The easiest way out is to store applications that are not part of the project
(and so carry their own translations) outside the project tree. That way,
``make-messages`` on the project level will only translate strings that are
connected to your explicit project and not strings that are distributed
independently.

Translations and JavaScript
===========================

Adding translations to JavaScript poses some problems:

    * JavaScript code doesn't have access to a ``gettext`` implementation.

    * JavaScript code doesn't have access to ``.po`` or ``.mo`` files; they need to be
      delivered by the server.

    * The translation catalogs for JavaScript should be kept as small as
      possible.

Django provides an integrated solution for these problems: it passes the
translations into JavaScript, so you can call ``gettext`` and friends from within
JavaScript.

The javascript_catalog View
---------------------------

The main solution to these problems is the ``javascript_catalog`` view, which
generates a JavaScript code library with functions that mimic the ``gettext``
interface, plus an array of translation strings. Those translation strings are
taken from the application, project, or Django core, according to what you
specify in either the ``info_dict`` or the URL.

You hook it up like this::

    js_info_dict = {
        'packages': ('your.app.package',),
    }

    urlpatterns = patterns('',
        (r'^jsi18n/$', 'django.views.i18n.javascript_catalog', js_info_dict),
    )

Each string in ``packages`` should be in Python dotted-package syntax (the
same format as the strings in ``INSTALLED_APPS``) and should refer to a package
that contains a ``locale`` directory. If you specify multiple packages, all
those catalogs are merged into one catalog. This is useful if you're depending upon
JavaScript that uses strings from different applications.

You can make the view dynamic by putting the packages into the URL pattern::

    urlpatterns = patterns('',
        (r'^jsi18n/(?P<packages>\S+?)/$, 'django.views.i18n.javascript_catalog'),
    )

With this, you specify the packages as a list of package names delimited by
plus signs (``+``) in the URL. This is especially useful if your pages use
code from different applications, and this changes often and you don't want to
pull in one big catalog file. As a security measure, these values can only be
either ``django.conf`` or any package from the ``INSTALLED_APPS`` setting.

Using the JavaScript Translation Catalog
----------------------------------------

To use the catalog, just pull in the dynamically generated script like this::

    <script type="text/javascript" src="/path/to/jsi18n/"></script>

This is how the admin site fetches the translation catalog from the server.
When the catalog is loaded, your JavaScript code can use the standard
``gettext`` interface to access it::

    document.write(gettext('this is to be translated'));

There even is a ``ngettext`` interface and a string interpolation function::

    d = {
        count: 10
    };
    s = interpolate(ngettext('this is %(count)s object', 'this are %(count)s objects', d.count), d);

The ``interpolate`` function supports both positional interpolation and named
interpolation. So the preceding code could have been written as follows::

    s = interpolate(ngettext('this is %s object', 'this are %s objects', 11), [11]);

The interpolation syntax is borrowed from Python. You shouldn't go over the top
with string interpolation, though -- this is still JavaScript, so the code will
have to do repeated regular-expression substitutions. This isn't as fast as
string interpolation  in Python, so keep it to those cases where you really
need it (e.g., in conjunction with ``ngettext`` to produce proper
pluralization).

Creating JavaScript Translation Catalogs
----------------------------------------

You create and update the translation catalogs the same way as the other Django
translation catalogs: with the ```make-messages.py``` tool. The only
difference is you need to provide a ``-d djangojs`` parameter, like this::

    make-messages.py -d djangojs -l de

This creates or updates the translation catalog for JavaScript for German.
After updating translation catalogs, just run ``compile-messages.py`` the same
way as you do with normal Django translation catalogs.

Notes for Users Familiar with ``gettext``
=========================================

If you know ``gettext``, you might note these special things in the way Django
does translation:

    * The string domain is ``django`` or ``djangojs``. The string domain is used to
      differentiate between different programs that store their data in a
      common message-file library (usually ``/usr/share/locale/``). The ``django``
      domain is used for Python and template translation strings, and is loaded into
      the global translation catalogs. The ``djangojs`` domain is only used for
      JavaScript translation catalogs to make sure that those are as small as
      possible.

    * Django only uses ``gettext`` and ``gettext_noop``. That's because Django
      always uses ``DEFAULT_CHARSET`` strings internally. There isn't much benefit
      to using ``ugettext``, because you'll always need to produce UTF-8
      anyway.

    * Django doesn't use ``xgettext`` alone. It uses Python wrappers around
      ``xgettext`` and ``msgfmt``. That's mostly for convenience.
      
What's Next?
============

This chapter mostly concludes our coverage of Django's features. You should now
know enough to start producing your own Django sites.

However, writing the code is only the first step in deploying a successful
Web site. The next two chapters cover the things you'll need to know if you want
your site to survive in the real world. `Chapter 19`_ discuses how you can secure 
your sites and your users from malicious attackers, and `Chapter 20`_ details how to 
deploy a Django application onto one or many servers.

.. _Chapter 19: ../chapter19/
.. _Chapter 20: ../chapter20/
