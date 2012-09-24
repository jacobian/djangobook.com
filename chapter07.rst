==========================
Chapter 7: Form Processing
==========================

**Guest author: Simon Willison**

After following along with the last chapter, you should now have a fully
functioning if somewhat simple site. In this chapter, we'll deal with the next
piece of the puzzle: building views that take input from readers.

We'll start by making a simple search form "by hand" and looking at how to
handle data submitted from the browser. From there, we'll move on to using Django's
forms framework.

Search
======

The Web is all about search. Two of the Net's biggest success stories, Google
and Yahoo, built their multi-billion-dollar businesses around search. Nearly
every site sees a large percentage of traffic coming to and from its search
pages. Often the difference between the success or failure of a site is the
quality of its search. So it looks like we'd better add some searching to 
our fledgling books site, no?

We'll start by adding the search view to our URLconf
(``mysite.urls``). Recall that this means adding something like
``(r'^search/$', 'mysite.books.views.search')`` to the set of URL patterns.

Next, we'll write this ``search`` view into our view module
(``mysite.books.views``)::

    from django.db.models import Q
    from django.shortcuts import render_to_response
    from models import Book

    def search(request):
        query = request.GET.get('q', '')
        if query:
            qset = (
                Q(title__icontains=query) |
                Q(authors__first_name__icontains=query) |
                Q(authors__last_name__icontains=query)
            )
            results = Book.objects.filter(qset).distinct()
        else:
            results = []
        return render_to_response("books/search.html", {
            "results": results,
            "query": query
        })

There are a couple of things going on here that you haven't yet seen. First, 
there's ``request.GET``. This is how you access GET data
from Django; POST data is accessed through a similar ``request.POST`` object.
These objects behave exactly like standard Python dictionaries with some extra
features covered in Appendix H.

.. admonition:: What's GET and POST Data?

    GET and POST are the two methods that browsers use to send data to a server.
    Most of the time, you'll see them in HTML form tags::

        <form action="/books/search/" method="get">

    This instructs the browser to submit the form data to the URL
    ``/books/search/`` using the GET method.

    There are important differences between the semantics of GET and POST that
    we won't get into right now, but see
    http://www.w3.org/2001/tag/doc/whenToUseGet.html if you want to learn more.

So the line::

    query = request.GET.get('q', '')

looks for a GET parameter named ``q`` and returns an empty string if that
parameter wasn't submitted.

Note that we're using the ``get()`` method on ``request.GET``, which is
potentially confusing. The ``get()`` method here is the one that every Python
dictionary has. We're using it here to be careful: it is *not* safe to assume
that ``request.GET`` contains a ``'q'`` key, so we use ``get('q', '')`` to
provide a default fallback value of ``''`` (the empty string). If we merely
accessed the variable using ``request.GET['q']``, that code would raise a
``KeyError`` if ``q`` wasn't available in the GET data.

Second, what about this ``Q`` business? ``Q`` objects are used to build up
complex queries -- in this case, we're searching for any books where either the
title or the name of one of the authors matches the search query. Technically,
these ``Q`` objects comprise a QuerySet, and you can read more about them in
Appendix C.

In these queries, ``icontains`` is a case-insensitive search that uses the SQL
``LIKE`` operator in the underlying database.

Since we're searching against a many-to-many field, it's possible for the same
book to be returned more than once by the query (e.g., a book with two
authors who both match the search query). Adding ``.distinct()`` to the filter
lookup eliminates any duplicate results.

There's still no template for this search view, however. This should do the
trick::

    <!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN">
    <html lang="en">
    <head>
        <title>Search{% if query %} Results{% endif %}</title>
    </head>
    <body>
      <h1>Search</h1>
      <form action="." method="GET">
        <label for="q">Search: </label>
        <input type="text" name="q" value="{{ query|escape }}">
        <input type="submit" value="Search">
      </form>
    
      {% if query %}
        <h2>Results for "{{ query|escape }}":</h2>
    
        {% if results %}
          <ul>
          {% for book in results %}
            <li>{{ book|escape }}</l1>
          {% endfor %}
          </ul>
        {% else %}
          <p>No books found</p>
        {% endif %}
      {% endif %}
    </body>
    </html>

Hopefully by now what this does is fairly obvious. However, there are a few
subtleties worth pointing out:

    * The form's action is ``.``, which means "the current URL." This is a
      standard best practice: don't use separate views for the form page and
      the results page; use a single one that serves the form and search
      results.

    * We reinsert the value of the query back into the ``<input>``.  This lets
      readers easily refine their searches without having to retype what they
      searched for.

    * Everywhere ``query`` and ``book`` is used, we pass it through the 
      ``escape`` filter to make sure that any potentially malicious search 
      text is filtered out before being inserted into the page.

      It's *vital* that you do this with any user-submitted content! Otherwise
      you open your site up to cross-site scripting (XSS) attacks. Chapter 19
      discusses XSS and security in more detail.

    * However, we don't need to worry about harmful content in your database
      lookups -- we can simply pass the query into the lookup as is. This is
      because Django's database layer handles this aspect of security for you.

Now we have a working search. A further improvement would be putting a search
form on every page (i.e., in the base template); we'll let you handle that one
yourself.

Next, we'll look at a more complex example. But before we do, let's discuss
a more abstract topic: the "perfect form."

The "Perfect Form"
==================

Forms can often be a major cause of frustration for the users of your site.
Let's consider the behavior of a hypothetical perfect form:

    * It should ask the user for some information, obviously. Accessibility and
      usability matter here, so smart use of the HTML ``<label>`` element and
      useful contextual help are important.

    * The submitted data should be subjected to extensive validation. The golden
      rule of Web application security is "never trust incoming data," so
      validation is essential.

    * If the user has made any mistakes, the form should be redisplayed with
      detailed, informative error messages. The original data should be
      prefilled, to save the user from having to reenter everything.

    * The form should continue to redisplay until all of the fields have been
      correctly filled.

Constructing the perfect form seems like a lot of work! Thankfully, Django's
forms framework is designed to do most of the work for you. You provide a
description of the form's fields, validation rules, and a simple template, and
Django does the rest. The result is a "perfect form" with very little effort.

Creating a Feedback Form
========================

The best way to build a site that people love is to listen to their feedback.
Many sites appear to have forgotten this; they hide their contact details
behind layers of FAQs, and they seem to make it as difficult as possible to get in
touch with an actual human being.

When your site has millions of users, this may be a reasonable strategy. When
you're trying to build up an audience, though, you should actively encourage
feedback at every opportunity. Let's build a simple feedback form and use it
to illustrate Django's forms framework in action.

We'll start by adding adding ``(r'^contact/$', 'mysite.books.views.contact')`` to 
the URLconf, then defining our form. Forms in Django are created in a similar way
to models: declaratively, using a Python class. Here's the class for our simple
form. By convention, we'll insert it into a new ``forms.py`` file within our
application directory::

    from django import newforms as forms

    TOPIC_CHOICES = (
        ('general', 'General enquiry'),
        ('bug', 'Bug report'),
        ('suggestion', 'Suggestion'),
    )

    class ContactForm(forms.Form):
        topic = forms.ChoiceField(choices=TOPIC_CHOICES)
        message = forms.CharField()
        sender = forms.EmailField(required=False)

.. admonition:: "New" Forms? What?

    When Django was first released to the public, it had a complicated, confusing forms
    system. It made producing forms far too difficult, so it was completely
    rewritten and is now called "newforms." However, there's still a fair amount of
    code that depends on the "old" form system, so for the time being Django
    ships with two form packages.

    As we write this book, Django's old form system is still available as
    ``django.forms`` and the new form package as ``django.newforms``. At some
    point that will change and ``django.forms`` will point to the new form
    package. However, to make sure the examples in this book work as widely as
    possible, all the examples will refer to ``django.newforms``.

A Django form is a subclass of ``django.newforms.Form``, just as a Django model
is a subclass of ``django.db.models.Model``. The ``django.newforms`` module also
contains a number of ``Field`` classes; a full list is available in Django's
documentation at http://www.djangoproject.com/documentation/0.96/newforms/.

Our ``ContactForm`` consists of three fields: a topic, which is a choice among
three options; a message, which is a character field; and a sender, which is an
email field and is optional (because even anonymous feedback can be useful).
There are a number of other field types available, and you can write your own
if they don't cover your needs.

The form object itself knows how to do a number of useful things. It can
validate a collection of data, it can generate its own HTML "widgets," it can
construct a set of useful error messages and, if we're feeling lazy, it can
even draw the entire form for us. Let's hook it into a view and see it in
action. In ``views.py``:

.. parsed-literal::

    from django.db.models import Q
    from django.shortcuts import render_to_response
    from models import Book
    **from forms import ContactForm**

    def search(request):
        query = request.GET.get('q', '')
        if query:
            qset = (
                Q(title__icontains=query) |
                Q(authors__first_name__icontains=query) |
                Q(authors__last_name__icontains=query)
            )
            results = Book.objects.filter(qset).distinct()
        else:
            results = []
        return render_to_response("books/search.html", {
            "results": results,
            "query": query
        })

    **def contact(request):**
        **form = ContactForm()**
        **return render_to_response('contact.html', {'form': form})**

and in ``contact.html``::

    <!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN">
    <html lang="en">
    <head>
        <title>Contact us</title>
    </head>
    <body>
        <h1>Contact us</h1>
        <form action="." method="POST">
            <table>
                {{ form.as_table }}
            </table>
            <p><input type="submit" value="Submit"></p>
        </form>
    </body>
    </html>

The most interesting line here is ``{{ form.as_table }}``. ``form`` is our
ContactForm instance, as passed to ``render_to_response``. ``as_table`` is a
method on that object that renders the form as a sequence of table rows
(``as_ul`` and ``as_p`` can also be used). The generated HTML looks like this::

    <tr>
        <th><label for="id_topic">Topic:</label></th>
        <td>
            <select name="topic" id="id_topic">
                <option value="general">General enquiry</option>
                <option value="bug">Bug report</option>
                <option value="suggestion">Suggestion</option>
            </select>
        </td>
    </tr>
    <tr>
        <th><label for="id_message">Message:</label></th>
        <td><input type="text" name="message" id="id_message" /></td>
    </tr>
    <tr>
        <th><label for="id_sender">Sender:</label></th>
        <td><input type="text" name="sender" id="id_sender" /></td>
    </tr>


Note that the ``<table>`` and ``<form>`` tags are not included; you need to
define those yourself in the template, which gives you control over how the form
behaves when it is submitted. Label elements *are* included, making forms
accessible out of the box.

Our form is currently using a ``<input type="text">`` widget for the message
field. We don't want to restrict our users to a single line of text, so we'll
swap in a ``<textarea>`` widget instead:

.. parsed-literal::

    class ContactForm(forms.Form):
        topic = forms.ChoiceField(choices=TOPIC_CHOICES)
        message = forms.CharField(**widget=forms.Textarea()**)
        sender = forms.EmailField(required=False)

The forms framework separates out the presentation logic for each field into a
set of widgets. Each field type has a default widget, but you can easily override
the default, or provide a custom widget of your own.

At the moment, submitting the form doesn't actually do anything. Let's hook in
our validation rules::

    def contact(request):
        if request.method == 'POST':
            form = ContactForm(request.POST)
        else:
            form = ContactForm()
        return render_to_response('contact.html', {'form': form})

A form instance can be in one of two states: bound or unbound. A *bound*
instance is constructed with a dictionary (or dictionary-like object) and 
knows how to validate and redisplay the data from it. An *unbound* form has 
no data associated with it and simply knows how to display itself.

Try clicking Submit on the blank form. The page should redisplay, showing a
validation error that informs us that our message field is required.

Try entering an invalid email address as well. The ``EmailField`` knows how to
validate email addresses, at least to a reasonable level of doubt.

.. admonition:: Setting Initial Data

    Passing data directly to the form constructor binds that data and indicates
    that validation should be performed. Often, though, we need to display an
    initial form with some of the fields prefilled -- for example, an "edit"
    form. We can do this with the ``initial`` keyword argument::

        form = CommentForm(initial={'sender': 'user@example.com'})

    If our form will *always* use the same default values, we can configure
    them in the form definition itself:
    
    .. parsed-literal::

        message = forms.CharField(widget=forms.Textarea(), 
                                  **initial="Replace with your feedback"**)

Processing the Submission
=========================

Once the user has filled the form to the point that it passes our validation
rules, we need to do something useful with the data. In this case, we want to
construct and send an email containing the user's feedback. We'll use Django's
email package to do this.

First, though, we need to tell if the data is indeed valid, and if it is, we need
access to the validated data. The forms framework does more than just validate
the data, it also converts it into Python types. Our contact form only deals
with strings, but if we were to use an ``IntegerField`` or ``DateTimeField``, the
forms framework would ensure that we got back a Python integer or ``datetime``
object, respectively.

To tell whether a form is bound to valid data, call the ``is_valid()`` method::

    form = ContactForm(request.POST)
    if form.is_valid():
        # Process form data

Now we need access to the data. We could pull it straight out of
``request.POST``, but if we did, we'd miss out on the type conversions performed
by the forms framework. Instead, we use ``form.clean_data``::

    if form.is_valid():
        topic = form.clean_data['topic']
        message = form.clean_data['message']
        sender = form.clean_data.get('sender', 'noreply@example.com')
        # ...

Note that since ``sender`` is not required, we provide a default when it's missing.
Finally, we need to record the user's feedback. The easiest way to do this is to
email it to a site administrator. We can do that using the ``send_mail``
function::

    from django.core.mail import send_mail

    # ...

    send_mail(
        'Feedback from your site, topic: %s' % topic,
        message, sender,
        ['administrator@example.com']
    )

The ``send_mail`` function has four required arguments: the email subject, the
email body, the "from" address, and a list of recipient addresses. ``send_mail``
is a convenient wrapper around Django's ``EmailMessage`` class, which provides
advanced features such as attachments, multipart emails, and full control over
email headers.

Having sent the feedback email, we'll redirect our user to a static
confirmation page. The finished view function looks like this::

    from django.http import HttpResponseRedirect
    from django.shortcuts import render_to_response
    from django.core.mail import send_mail
    from forms import ContactForm

    def contact(request):
        if request.method == 'POST':
            form = ContactForm(request.POST)
            if form.is_valid():
                topic = form.clean_data['topic']
                message = form.clean_data['message']
                sender = form.clean_data.get('sender', 'noreply@example.com')
                send_mail(
                    'Feedback from your site, topic: %s' % topic,
                    message, sender,
                    ['administrator@example.com']
                )
                return HttpResponseRedirect('/contact/thanks/')
        else:
            form = ContactForm()
        return render_to_response('contact.html', {'form': form})

.. admonition:: Redirect After POST

    If a user selects Refresh on a page that was displayed by a POST request,
    that request will be repeated. This can often lead to undesired behavior,
    such as a duplicate record being added to the database. Redirect after
    POST is a useful pattern that can help avoid this scenario: after a
    successful POST has been processed, redirect the user to another page
    rather than returning HTML directly.

Custom Validation Rules
=======================

Imagine we've launched our feedback form, and the emails have started tumbling
in. There's just one problem: some of the emails are just one or two words,
hardly enough for a detailed missive. We decide to adopt a new validation
policy: four words or more, please.

There are a number of ways to hook custom validation into a Django form. If our
rule is something we will reuse again and again, we can create a custom field
type. Most custom validations are one-off affairs, though, and can be tied directly to
the form class.

We want additional validation on the ``message`` field, so we need to add a
``clean_message`` method to our form::

    class ContactForm(forms.Form):
        topic = forms.ChoiceField(choices=TOPIC_CHOICES)
        message = forms.CharField(widget=forms.Textarea())
        sender = forms.EmailField(required=False)

        def clean_message(self):
            message = self.clean_data.get('message', '')
            num_words = len(message.split())
            if num_words < 4:
                raise forms.ValidationError("Not enough words!")
            return message

This new method will be called after the default field validator (in this case,
the validator for a required ``CharField``). Because the field data has already been
partially processed, we need to pull it out of the form's ``clean_data``
dictionary.

We naively use a combination of ``len()`` and ``split()`` to count the number of words.
If the user has entered too few words, we raise a ``ValidationError``. The
string attached to this exception will be displayed to the user as an item in
the error list.

It is important that we explicitly return the value for the field at the end of
the method. This allows us to modify the value (or convert it to a different
Python type) within our custom validation method. If we forget the return
statement, then ``None`` will be returned, and the original value will be lost.

A Custom Look and Feel
======================

The quickest way to customize the form's presentation is with CSS. The list of
errors in particular could do with some visual enhancement, and the ``<ul>`` has
a class attribute of ``errorlist`` for that exact purpose. The following CSS
really makes our errors stand out::

    <style type="text/css">
        ul.errorlist {
            margin: 0;
            padding: 0;
        }
        .errorlist li {
            background-color: red;
            color: white;
            display: block;
            font-size: 10px;
            margin: 0 0 3px;
            padding: 4px 5px;
        }
    </style>

While it's convenient to have our form's HTML generated for us, in many
cases the default rendering won't be right for our application. ``{{
form.as_table }}`` and friends are useful shortcuts while we develop our
application, but everything about the way a form is displayed can be overridden,
mostly within the template itself.

Each field widget (``<input type="text">``, ``<select>``, ``<textarea>``, or
similar) can be rendered individually by accessing ``{{ form.fieldname }}``. Any
errors associated with a field are available as ``{{ form.fieldname.errors }}``.
We can use these form variables to construct a custom template for our contact
form::

    <form action="." method="POST">
        <div class="fieldWrapper">
            {{ form.topic.errors }}
            <label for="id_topic">Kind of feedback:</label>
            {{ form.topic }}
        </div>
        <div class="fieldWrapper">
            {{ form.message.errors }}
            <label for="id_message">Your message:</label>
            {{ form.message }}
        </div>
        <div class="fieldWrapper">
            {{ form.sender.errors }}
            <label for="id_sender">Your email (optional):</label>
            {{ form.sender }}
        </div>
        <p><input type="submit" value="Submit"></p>
    </form>

``{{ form.message.errors }}`` will display as a ``<ul class="errorlist">`` if
errors are present and a blank string if the field is valid (or the form is
unbound). We can also treat ``form.message.errors`` as a Boolean or even iterate
over it as a list, for example::

    <div class="fieldWrapper{% if form.message.errors %} errors{% endif %}">
        {% if form.message.errors %}
            <ol>
            {% for error in form.message.errors %}
                <li><strong>{{ error|escape }}</strong></li>
            {% endfor %}
            </ol>
        {% endif %}
        {{ form.message }}
    </div>

In the case of validation errors, this will add an "errors" class to the
containing ``<div>`` and display the list of errors in an ordered list.

Creating Forms from Models
==========================

Let's build something a little more interesting: a form that submits a new
publisher to our book application from Chapter 5.

An important rule of thumb in software development that Django tries to adhere
to is Don't Repeat Yourself (DRY). Andy Hunt and Dave Thomas in *The Pragmatic
Programmer* define this as follows:

    Every piece of knowledge must have a single, unambiguous, authoritative
    representation within a system.

Our ``Publisher`` model class says that a publisher has a name, address, city,
state_province, country, and website. Duplicating this information in a form
definition would break the DRY rule. Instead, we can use a useful shortcut: 
``form_for_model()``::

    from models import Publisher
    from django.newforms import form_for_model

    PublisherForm = form_for_model(Publisher)

``PublisherForm`` is a ``Form`` subclass, just like the ``ContactForm`` class
we created manually earlier on. We can use it in much the same way::

    from forms import PublisherForm
    
    def add_publisher(request):
        if request.method == 'POST':
            form = PublisherForm(request.POST)
            if form.is_valid():
                form.save()
                return HttpResponseRedirect('/add_publisher/thanks/')
        else:
            form = PublisherForm()
        return render_to_response('books/add_publisher.html', {'form': form})

The ``add_publisher.html`` file is almost identical to our original
``contact.html`` template, so it has been omitted.  Also remember to add a new
pattern to the URLconf: ``(r'^add_publisher/$', 'mysite.books.views.add_publisher')``.

There's one more shortcut being demonstrated here. Since forms derived from
models are often used to save new instances of the model to the database, the
form class created by ``form_for_model`` includes a convenient ``save()``
method. This deals with the common case; you're welcome to ignore it if you want
to do something a bit more involved with the submitted data.

``form_for_instance()`` is a related method that can create a preinitialized
form from an instance of a model class. This is useful for creating "edit"
forms.

What's Next?
============

This chapter concludes the introductory material in this book. The next 13
chapters deal with various advanced topics, including generating content other
than HTML (`Chapter 11`_), security (`Chapter 19`_), and deployment (`Chapter 20`_).

After these first seven chapters, you should know enough to start writing your
own Django projects. The rest of the material in this book will help fill in the
missing pieces as you need them.

We'll start in `Chapter 8`_ by doubling back and taking a closer look at views and
URLconfs (introduced first in `Chapter 3`_).

.. _Chapter 3: ../chapter03/
.. _Chapter 8: ../chapter08/
.. _Chapter 11: ../chapter11/
.. _Chapter 19: ../chapter19/
.. _Chapter 20: ../chapter20/
