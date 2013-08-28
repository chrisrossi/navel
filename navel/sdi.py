import colander
import deform
from slug import slug

from pyramid.httpexceptions import HTTPFound

from substanced.form import FormView
from substanced.interfaces import IFolder
from substanced.schema import Schema
from substanced.sdi import mgmt_view
from substanced.sdi.views.folder import AddFolderSchema
from substanced.sdi.views.folder import FolderContents
from substanced.sdi.views.folder import folder_contents_views

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
        title = getattr(entry, 'title', None)
        return [
            {'name': 'Title',
             'value': title}
        ]
