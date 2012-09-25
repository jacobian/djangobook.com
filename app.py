"""
The simplest possible app that can serve these Sphinx docs and issue
redirects for the previous URLs.
"""

import static
import selector
from unipath import FSPath as Path

app = selector.Selector()

def redirect(to):
    """
    Create a 301 redirect WSGI app.

    `to` may contain str.format-style formatting which'll be formatted against
    the routing arguments (wsgiorg.routing_args).
    """
    def _redirect(environ, start_response):
        args, kwargs = environ['wsgiorg.routing_args']
        start_response('301 MOVED PERMANENTLY',
                       [('Location', to.format(*args, **kwargs))])
        return []
    return _redirect

# Redirects for old doc URLs, since Cool URIs Don't Change.
app.add('/',                    GET=redirect('/en/2.0/index.html'))
app.add('/license/',            GET=redirect('/en/2.0/license.html'))
app.add('/about/',              GET=redirect('/en/2.0/frontmatter.html'))
app.add('/en/1.0/',             GET=redirect('/en/2.0/index.html'))
app.add('/en/1.0/{doc:chunk}/', GET=redirect('/en/2.0/{doc}.html'))
app.add('/en/2.0/{doc:chunk}/', GET=redirect('/en/2.0/{doc}.html'))

# Serve docs at "/en/2.0" still, to leave room for the future.
# One of these days I'll actually do this, not just talk about it!
docs = static.Cling(Path(__file__).parent.child('_build', 'html'))
app.add("/en/2.0|", GET=docs)
