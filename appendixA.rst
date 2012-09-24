========================
Appendix A: Case Studies
========================

To help answer questions about how Django works in the "real world," we spoke
with (well, emailed) a handful of people who have complete, deployed Django
sites under their belts. Most of this appendix is in their words, which have
been lightly edited for clarity.

Cast of Characters
==================

Let's meet our cast and their projects.

    * *Ned Batchelder* is the lead engineer at Tabblo.com. Tabblo started life as
      a storytelling tool built around photo sharing, but it was recently bought
      by Hewlett-Packard for more wide-reaching purposes:
      
        HP saw real value in our style of web development, and in the way we
        bridged the virtual and physical worlds. They acquired us so that we
        could bring that technology to other sites on the Web. Tabblo.com is
        still a great storytelling site, but now we are also working to
        componentize and rehost the most interesting pieces of our technology.

    * *Johannes Beigel* is a lead developer at Brainbot Technologies AG.
      Brainbot's major public-facing Django site is http://pediapress.com/,
      where you can order printed versions of Wikipedia articles. Johannes's team
      is currently working on an enterprise-class knowledge-management program
      known as Brainfiler.
      
      Johannes tells us that Brainfiler 
      
        [...] is a software solution to manage, search for, categorize, and share
        information from distributed information sources. It's built for
        enterprise usage for both the intranet and the Internet and is highly
        scalable and customizable. The development of the core concepts and
        components started in 2001. Just recently we have
        redesigned/reimplemented the application server and Web front-end, which
        is [now] based on Django.
      
    * *David Cramer* is the lead developer at Curse, Inc. He develops
      Curse.com, a gaming site devoted to massively multiplayer online games
      like World of Warcraft, Ultima Online, and others.
      
      Curse.com is one of the largest deployed Django sites on the Internet:
      
        We do roughly 60-90 million page views in an average month, and we have
        peaked at over 130 million page views [in a month] using Django. We are a
        very dynamic and user-centric Web site for online gamers, specifically
        massively multiplayer games, and are one of the largest Web sites
        globally for World of Warcraft. Our Web site was established in early
        2005, and since late 2006 we have been expanding our reach into games
        beyond World of Warcraft.
      
    * *Christian Hammond* is a senior engineer at VMware (a leading developer
      of virtualization software). He's also the lead developer of Review Board
      (http://www.review-board.org/), a Web-based code review system. Review
      Board began life as an internal VMware project, but is now open source:
      
        In late 2006, David Trowbridge and I were discussing the process we used
        at VMware for handling code reviews. Before people committed code to the
        source repository, they were supposed to send out a diff of the change
        to a mailing list and get it reviewed. It was all handled over email,
        and as such, it became hard to keep track of reviews requiring your
        attention. We began to discuss potential solutions for this problem.
        
        Rather than writing down my ideas, I put them into code. Before long,
        Review Board was born. Review Board helps developers, contributors, and
        reviewers to keep track of the code that's out for review and to better
        communicate with each other. Rather than vaguely referencing some part
        of the code in an email, the reviewer is able to comment directly on
        the code. The code, along with the comments, will then appear in the
        review, giving the developer enough context to work with to quickly make
        the necessary changes.
        
        Review Board grew quickly at VMware. Much faster than expected,
        actually. Within a few short weeks, we had ten teams using Review Board.
        However, this project is not internal to VMware. It was decided day one
        that this should be open source and be made available for any company or
        project to use.
        
        We made an open source announcement and put a site together, which is
        available at http://www.review-board.org/. The response to our public
        announcement was as impressive as our internal VMware announcement.
        Before long, our demo server reached over 600 users, and people began to
        contribute back to the project.
        
        Review Board isn't the only code review tool on the market, but it is
        the first we have seen that is open source and has the extensive feature
        set we've worked to build into it. We hope this will in time benefit
        many open source and commercial projects.
        
Why Django?
===========

We asked each developer why he decided to use Django, what other options
were considered, and how the decision to use Django was ultimately made.

*Ned Batchelder*:
    
    Before I joined Tabblo, Antonio Rodriguez (Tabblo's founder/CTO) did an evaluation
    of Rails and Django, and found that both provided a great
    quick-out-of-the-blocks rapid development environment. In comparing the
    two, he found that Django had a greater technical depth that would make it
    easier to build a robust, scalable site. Also, Django's Python foundation
    meant that we'd have all the richness of the Python ecosystem to support
    our work. This has definitely been proven out as we've built Tabblo.
    
*Johannes Beigel*:

    As we have been coding in Python for many years now, and quickly started
    using the Twisted framework, Nevow was the most "natural" solution for our
    Web application stuff. But we soon realized that -- despite the perfect
    Twisted integration -- many things were getting a little cumbersome and
    got in the way of our agile development process.
    
    After some Internet research it quickly became clear that Django was the
    most promising Web development framework for our requirements.
    
    The trigger that led us to Django was its template syntax, but we soon
    appreciated all the other features that are included, and so Django was
    pretty much a fast-selling item.
    
    After doing a few years of parallel development and deployment (Nevow is
    still in use for some projects on customer sites), we came to the
    conclusion that Django is a lot less cumbersome, results in code that is
    much better to maintain, and is more fun to work with.
    
*David Cramer*:

    I heard about Django in the summer of 2006, about the time we were getting
    ready to do an overhaul of Curse, and we did some research on it. We were
    all very impressed at what it could do, and where it could save time for
    us. We talked it over, decided on Django, and began writing the third
    revision to the Web site almost immediately.
    
*Christian Hammond*:

    I had toyed around with Django on a couple of small projects and had been
    very impressed with it. It's based on Python, which I had become a big
    fan of, and it made it easy not only to develop Web sites and Web apps, but
    also to keep them organized and maintainable. This was always tricky in PHP and
    Perl. Based on past experiences, going with Django was a no-brainer.
    
Getting Started
===============

Since Django's a relatively new tool, there aren't that many experienced
Django developers out there. We asked our "panel" how they got their team up
to speed on Django and for any tips they wanted to share with new Django
developers.

*Johannes Beigel*:

    After coding mostly in C++ and Perl, we switched to Python and continued
    using C++ for the computationally intensive code.

    [We learned Django by] working through the tutorial, browsing the
    documentation to get an idea of what's possible (it's easy to miss many
    features by just doing the tutorial), and trying to understand the basic
    concepts behind middleware, request objects, database models, template
    tags, custom filters, forms, authorization, localization... Then [we
    could] take a deeper look at those topics when [we] actually needed them.

*David Cramer*:

    The Web site documentation is great. Stick with it.

*Christian Hammond*:

    David and I both had prior experience with Django, though it was limited.
    We had learned a lot through our development of Review Board. I would
    advise new users to read through the well-written Django documentation and
    [the book you're reading now], both of which have been invaluable to us.

We didn't have to bribe Christian to get that quote -- promise!

Porting Existing Code
=====================

Although Review Board and Tabblo were ground-up development, the other sites
were ported from existing code. We were interested in hearing how that process
went.

*Johannes Beigel*:

    We started to "port" the site from Nevow, but we soon realized that we'd
    like to change so many conceptual things (both in the UI part and in the
    application server part) that we started from scratch and used the former
    code merely as a reference.

*David Cramer*:

    The previous site was written in PHP. Going from PHP to Python was great
    programmatically. The only downfall is you have to be a lot more careful
    with memory management [since Django processes stay around a lot longer
    than PHP processes (which are single cycle)].
    
How Did It Go?
==============

Now for the million-dollar question: How did Django treat you? We were especially
interested in hearing where Django fell down -- it's important to know where
your tools are weak *before* you run into roadblocks.

*Ned Batchelder*:

    Django has really enabled us to experiment with our Web site's
    functionality. Both as a startup heat-seeking customers and businesses,
    and now as a part of HP working with a number of partners, we've had to be
    very nimble when it comes to adapting the software to new demands. The
    separation of functionality into models, views, and controllers has given
    us modularity so we can appropriately choose where to extend and modify.
    The underlying Python environment gives us the opportunity to make use of
    existing libraries to solve problems without reinventing the wheel. PIL, PDFlib,
    ZSI, JSmin, and BeautifulSoup are just a handful of the libraries we've
    pulled in to do some heavy lifting for us.
    
    The most difficult part of our Django use has been the relationship of
    memory objects to database objects, in a few ways. First, Django's ORM
    does not ensure that two references to the same database record are the
    same Python object, so you can get into situations where two parts of the
    code are both trying to modify the same record, and one of the copies is
    stale. Second, the Django development model encourages you to base your
    data objects on database objects. We've found over time more and more uses
    for data objects that are not tied to the database, and we've had to
    migrate away from assuming that data is stored in the database.
    
    For a large, long-lived code base, it definitely makes sense to spend time
    up front anticipating the ways your data will be stored and accessed, and
    building some infrastructure to support those ways.
    
    We've also added our own database migration facility so that developers
    don't have to apply SQL patches to keep their database schemas current.
    Developers who change the schema write a Python function to update the
    database, and these are applied automatically when the server is started.

*Johannes Beigel*:

    We consider Django as a very successful platform that perfectly fits
    in the Pythonic way of thinking. Almost everything just worked as
    intended.

    One thing that needed a bit of work in our current project was tweaking
    the global ``settings.py`` file and directory structure/configuration
    (for apps, templates, locale data, etc.), because we implemented a highly
    modular and configurable system, where all Django views are actually
    methods of some class instances. But with the omnipotence of dynamic
    Python code, that was still possible.

*David Cramer*:

    We managed to push out large database applications in a weekend. This
    would have taken one to two weeks to do on the previous Web site, in PHP. Django
    has shined exactly where we wanted it to.

    Now, while Django is a great platform, it can't go without saying that it's
    not built specific to everyone's needs. Upon the initial launch of the
    Django Web site, we had our highest traffic month of the year, and we
    weren't able to keep up. Over the next few months we tweaked bits and
    pieces, mostly hardware and the software serving Django requests. [This
    included modification of our] hardware configuration, optimization of
    Django, [and tuning] the software we were using to serve the requests
    (which, at the time, was lighttpd and FastCGI).
    
    In May of 2007, Blizzard (the creators of World of Warcraft) released
    another quite large patch, as they had done in December when we first
    launched Django. The first thing going through our heads was, "Hey, we
    nearly held up in December, this is nowhere near as big, we should be
    fine." We lasted about 12 hours before the servers started to feel the
    heat. The question was raised again: was Django really the best solution
    for what we want to accomplish?
    
    Thanks to a lot of great support from the community, and a late night, we
    managed to implement several "hot-fixes" to the Web site during those few
    days. The changes (which hopefully have been rolled back into Django by
    the time this book is released) managed to completely reassure everyone
    that while not everyone needs to be able to do 300 Web requests per
    second, the people who do, can, with Django.

*Christian Hammond*:

    Django allowed us to build Review Board fairly quickly by forcing us to
    stay organized through its URL, view, and template separations, and by
    providing useful built-in components, such as the authentication app,
    built-in caching, and the database abstraction. Most of this has worked
    really well for us.
    
    Being a dynamic [Web application], we've had to write a lot of JavaScript
    code. This is an area that Django hasn't really helped us with so far.
    Django's templates, template tags, filters, and forms support are great, but
    aren't easily usable from JavaScript code. There are times when we would
    want to use a particular template or filter but had no way of using it
    from JavaScript. I would personally like to see some creative solutions
    for this incorporated into Django.
    
Team Structure
==============

Often successful projects are made so by their teams, not their choice of
technology. We asked our panel how their teams work, and what tools and
techniques they use to stay on track.

*Ned Batchelder*:

    We're a pretty standard Web startup environment: Trac/SVN, five
    developers. We have a staging server, a production server, an ad hoc deploy
    script, and so on.

    Memcached rocks.

*Johannes Beigel*:

    We use Trac as our bug tracker and wiki and have recently switched from using
    Subversion+SVK to Mercurial (a Python-written distributed version-
    control system that handles branching/merging like a charm).

    I think we have a very agile development process, but we do not follow a
    "rigid" methodology like Extreme Programming ([though] we borrow many
    ideas from it). We are more like Pragmatic Programmers.

    We have an automated build system (customized but based on SCons) and unit
    tests for almost everything.

*David Cramer*:

    Our team consists of four Web developers, all working in the same office
    space, so it's quite easy to communicate. We rely on common tools such as
    SVN and Trac.

*Christian Hammond*:

    Review Board currently has two main developers (myself and David
    Trowbridge) and a couple of contributors. We're hosted on Google Code and
    make use of their Subversion repository, issue tracker, and wiki. We
    actually use Review Board to review our changes before they go in. We test
    on our local computers, both by hand and through unit tests. Our users at
    VMware who use Review Board every day provide a lot of useful feedback and
    bug reports, which we try to incorporate into the program.

Deployment
==========

The Django developers take ease of deployment and scaling very seriously, so
we're always interested in hearing about real-world trials and tribulations.

*Ned Batchelder*:

    We've used caching both at the query and response layers to speed response
    time. We have a classic configuration: a multiplexer, many app servers,
    one database server. This has worked well for us, because we can use
    caching at the app server to avoid database access, and then add app
    servers as needed to handle the volume.

*Johannes Beigel*:

    Linux servers, preferably Debian, with many gigs of RAM. Lighttpd as the Web
    server, Pound as the HTTPS front-end and load balancer if needed, and Memcached
    for caching. SQLite for small databases, Postgres if data grows larger, and
    highly specialized custom database stuff for our search and knowledge
    management components.

*David Cramer*:

    Our structure is still up for debate... [but this is what's current]:

    When a user requests the site they are sent to a cluster of Squid servers
    using lighttpd. There, servers then check if the user is logged in. If not,
    they're served a cached page. A logged-in user is forwarded to a cluster
    of Web servers running apache2 plus mod_python (each with a large amount of
    memory), which then each rely on a distributed Memcached system and a
    beastly MySQL database server. Static content is hosted on a cluster of
    lighttpd servers. Media, such as large files and videos, are hosted
    (currently) on a server using a minimal Django install using lighttpd plus
    fastcgi. As of right now we're moving toward pushing all media to
    a service similar to Amazon's S3.

*Christian Hammond*:

    There are two main production servers right now. One is at VMware and
    consists of an Ubuntu virtual machine running on VMware ESX. We use MySQL
    for the database, Memcached for our caching back-end, and currently Apache
    for the Web server. We have several powerful servers that we can scale
    across when we need to. We may find ourselves moving MySQL or Memcached to
    another virtual machine as our user base increases.
    
    The second production server is the one for Review Board itself. The
    setup is nearly identical to the one at VMware, except the virtual machine
    is being hosted on VMware Server.