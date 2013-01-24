============
Introduction
============

In the early days, Web developers wrote every page by hand. Updating a Web site
meant editing HTML; a "redesign" involved redoing every single page, one at a
time.

As Web sites grew and became more ambitious, it quickly became obvious that that
situation was tedious, time-consuming, and ultimately untenable. A group of
enterprising hackers at NCSA (the National Center for Supercomputing
Applications, where Mosaic, the first graphical Web browser, was developed)
solved this problem by letting the Web server spawn external programs that could
dynamically generate HTML. They called this protocol the Common Gateway
Interface, or CGI, and it changed the Web forever.

It's hard now to imagine what a revelation CGI must have been: instead of
treating HTML pages as simple files on disk, CGI allows you to think of your
pages as resources generated dynamically on demand. The development of CGI
ushered in the first generation of dynamic Web sites.

However, CGI has its problems: CGI scripts need to contain a lot of repetitive
"boilerplate" code, they make code reuse difficult, and they can be difficult
for first-time developers to write and understand.

PHP fixed many of these problems, and it took the world by storm -- it's now by
far the most popular tool used to create dynamic Web sites, and dozens of
similar languages and environments (ASP, JSP, etc.) followed PHP's design
closely. PHP's major innovation is its ease of use: PHP code is simply embedded
into plain HTML; the learning curve for someone who already knows HTML is
extremely shallow.

But PHP has its own problems; its very ease of use encourages sloppy,
repetitive, ill-conceived code. Worse, PHP does little to protect programmers
from security vulnerabilities, and thus many PHP developers found themselves
learning about security only once it was too late.

These and similar frustrations led directly to the development of the current
crop of "third-generation" Web development frameworks. These frameworks --
Django and Ruby on Rails appear to be the most popular these days -- recognize
that the Web's importance has escalated of late. With this new explosion of Web
development comes yet another increase in ambition; Web developers are expected
to do more and more every day.

Django was invented to meet these new ambitions. Django lets you build deep,
dynamic, interesting sites in an extremely short time. Django is designed to let
you focus on the fun, interesting parts of your job while easing the pain of the
repetitive bits. In doing so, it provides high-level abstractions of common Web
development patterns, shortcuts for frequent programming tasks, and clear
conventions on how to solve problems. At the same time, Django tries to stay out
of your way, letting you work outside the scope of the framework as needed. We
wrote this book because we firmly believe that Django makes Web development
better. It's designed to quickly get you moving on your own Django projects, and
then ultimately teach you everything you need to know to successfully design,
develop, and deploy a site that you'll be proud of.

We're extremely interested in your feedback. This book is `open source`__ and 
all are welcome to improve it. If you prefer to suggest changes, please drop us 
a line at feedback@djangobook.com. Either way, we'd love to hear from you! We're
glad you're here, and we hope that you find Django as exciting, fun and useful 
as we do.

__ http://github.com/jacobian/djangobook.com
