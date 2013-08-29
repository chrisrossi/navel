from pyramid.view import view_config, view_defaults
from substanced.util import find_catalog, find_objectmap

from .resources import pub_date_sorter


@view_defaults(content_type="Blog", permission='view')
class BlogViews(object):

    def __init__(self, blog, request):
        self.blog = blog
        self.request = request

    @view_config(renderer='templates/blog.pt')
    def show_blog(self):
        return {'blog_entries': self.get_blog_entries()}

    def get_blog_entries(self):
        blog = self.blog
        request = self.request
        system_catalog = find_catalog(blog, 'system')
        path = system_catalog['path']
        allowed = system_catalog['allowed']
        query = (path.eq(blog, depth=1, include_origin=False) &
                 allowed.allows(request, 'sdi.view') )
        results = query.execute()
        results = pub_date_sorter(blog, results, limit=5, reverse=True)
        objectmap = find_objectmap(blog)
        return map(dictify('title', 'body', 'pub_date'),
                   map(objectmap.object_for, results.ids))


def dictify(*names):
    def inner(obj):
        return dict({(name, getattr(obj, name, None)) for name in names})
    return inner
