import colander
import deform
from slug import slug
from tzlocal import get_localzone

from pyramid.httpexceptions import HTTPFound

from substanced.form import FormView
from substanced.interfaces import IFolder
from substanced.schema import Schema
from substanced.sdi import mgmt_view
from substanced.sdi.views.folder import AddFolderSchema
from substanced.sdi.views.folder import FolderContents
from substanced.sdi.views.folder import folder_contents_views
from substanced.util import find_catalog, get_icon_name

from .resources import Blog


@mgmt_view(context=IFolder,
           name='add_blog',
           permission='sdi.add_content',
           tab_condition=False,
           renderer="substanced.sdi:templates/form.pt")
class AddBlog(FormView):
    title = 'Add Blog'
    schema = AddFolderSchema()
    buttons = ('add',)

    def add_success(self, appstruct):
        registry = self.request.registry
        name = appstruct['name']
        blog = registry.content.create("Blog")
        self.context[name] = blog
        return HTTPFound(location=self.request.sdiapi.mgmt_path(self.context))


class AddBlogEntrySchema(Schema):
    title = colander.SchemaNode(colander.String())
    body = colander.SchemaNode(
        colander.String(),
        widget=deform.widget.RichTextWidget(
            options={"theme": "advanced"}))


@mgmt_view(content_type="Blog",
           name='add_blog_entry',
           permission='sdi.add_content',
           tab_condition=False,
           renderer="substanced.sdi:templates/form.pt")
class AddBlogEntry(FormView):
    title = 'Add Blog Entry'
    schema = AddBlogEntrySchema()
    buttons = ('add',)

    def add_success(self, appstruct):
        request = self.request
        entry = request.registry.content.create("Blog Entry", **appstruct)
        name = slug(entry.title)
        self.context[name] = entry
        return HTTPFound(location=self.request.sdiapi.mgmt_path(self.context))


@folder_contents_views(context=Blog)
class BlogContents(FolderContents):

    def get_columns(self, entry):
        request = self.request
        if entry:
            title = {'name': getattr(entry, 'title', None),
                     'url': request.sdiapi.mgmt_url(entry),
                     'icon': get_icon_name(entry, request) or ''}
            tz = get_localzone()
            pub_date = entry.pub_date.astimezone(tz).isoformat()
            pub_date = ' '.join(pub_date.rsplit('-', 1)[0].split('T'))
        else:
            title = pub_date = None
        return [
            {'name': 'Title',
             'value': title,
             'formatter': 'icon_label_url',
            },
            {'name': 'Publication Date',
             'value': pub_date,
             #'formatter': 'date',
             'initial_sort_reverse': True,
             'sorter': self.pub_date_sorter},
        ]

    def pub_date_sorter(self, resource, resultset, limit=None, reverse=False):
        catalog = find_catalog(resource, 'navel')
        index = catalog['pub_date']
        resultset = resultset.sort(index, limit=limit, reverse=reverse)
        return resultset
