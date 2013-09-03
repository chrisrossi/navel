import datetime
import itertools

from colander.iso8601 import UTC
from hypatia import query
from pyramid.traversal import find_interface
from pyramid.view import view_config, view_defaults
from pyramid_layout.panel import panel_config
from substanced.util import find_catalog, find_objectmap

from .resources import (Blog, pub_date_sorter)


class BlogViewBase(object):

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def get_info(self, entry):
        info = dictify(entry, 'title', 'body', 'pub_date')
        info['url'] = self.request.resource_url(entry)
        return info

    @property
    def blog(self):
        return find_interface(self.context, Blog)


def dictify(obj, *names):
    return dict({(name, getattr(obj, name, None)) for name in names})


@view_defaults(content_type="Blog", permission='view')
class BlogViews(BlogViewBase):
    posts_per_page = 5

    @view_config(renderer='templates/blog.pt')
    def show_blog(self):
        blog = self.context
        request = self.request
        system_catalog = find_catalog(blog, 'system')
        path = system_catalog['path']
        allowed = system_catalog['allowed']
        q = (path.eq(blog, depth=1, include_origin=False) &
            allowed.allows(request, 'view') )
        limit = self.posts_per_page

        year = request.params.get('year')
        month = request.params.get('month')
        if year and month:
            year, month = int(year), int(month)
            limit = None
            start = datetime.datetime(year, month, 1, 0, 0, tzinfo=UTC)
            if month == 12:
                end = datetime.datetime(year + 1, 1, 1, 0, 0, tzinfo=UTC)
            else:
                end = datetime.datetime(year, month + 1, 1, 0, 0, tzinfo=UTC)
            catalog = find_catalog(blog, 'navel')
            pub_date = catalog['pub_date']
            q &= query.InRange(pub_date, start, end)

        results = q.execute()
        results = pub_date_sorter(blog, results, reverse=True)

        if limit and len(results) > limit:
            offset = int(request.params.get('offset', 0))
            last = offset + limit
            ids = itertools.islice(results.ids, offset, last)
            pager = [
                {'title': 'Older',
                 'url': request.resource_url(blog, query={'offset': last}),
                 'disabled': " disabled" if last >= len(results) else ""},
                {'title': 'Newer',
                 'url': request.resource_url(blog,
                                             query={'offset': offset - limit}),
                 'disabled': " disabled" if offset <= 0 else ""}]
        else:
            pager = None
            ids = results.ids

        objectmap = find_objectmap(blog)
        entries = map(self.get_info, map(objectmap.object_for, ids))
        return {
            'entries': entries,
            'pager': pager}


@view_defaults(content_type="Blog Entry", permission='view')
class BlogEntryViews(BlogViewBase):

    @view_config(renderer='templates/blogentry.pt')
    def show_blogentry(self):
        return self.get_info(self.context)


@panel_config(name='toc', context=Blog, renderer='templates/blog_toc.pt')
def blog_toc(blog, request):
    current_url = request.url
    def info(yearmonth):
        year, month = yearmonth
        dt = datetime.date(year, month, 1)
        url = request.resource_url(blog, query={'year': year, 'month': month})
        active = current_url == url
        return {
            'title': dt.strftime("%B %Y"),
            'class': 'active' if active else '',
            'url': url}
    catalog = find_catalog(blog, 'navel')
    months = sorted(set([(dt.year, dt.month) for dt in
                         catalog['pub_date']._fwd_index.keys()]), reverse=True)
    return {'contents': map(info, months)}
