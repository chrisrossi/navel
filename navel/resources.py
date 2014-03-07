import colander
import datetime
import deform

from colander.iso8601 import UTC
from persistent import Persistent

from substanced.content import content
from substanced.folder import Folder
from substanced.property import PropertySheet
from substanced.schema import NameSchemaNode, Schema
from substanced.util import find_catalog, renamer


class BlogEntrySchema(Schema):
    title = colander.SchemaNode(colander.String())
    body = colander.SchemaNode(
        colander.String(),
        widget=deform.widget.RichTextWidget(options={
            "menubar": False,
            "plugins": "link image",
        }))
    pub_date = colander.SchemaNode(colander.DateTime())
    name = NameSchemaNode(editing=True)


class BlogEntryPropertySheet(PropertySheet):
    schema = BlogEntrySchema()


@content("Blog Entry",
         icon="glyphicon glyphicon-align-left",
         propertysheets=(('Basic', BlogEntryPropertySheet),),
         add_view="add_blog_entry")
class BlogEntry(Persistent):
    name = renamer()

    def __init__(self, title='', body='', pub_date=None):
        self.title = title
        self.body = body
        if pub_date is None:
            t = datetime.datetime.now(UTC)
            pub_date = datetime.datetime(
                t.year, t.month, t.day, t.hour, t.minute, t.second, tzinfo=UTC)
        self.pub_date = pub_date


@content("Blog",
         icon="glyphicon glyphicon-font",
         add_view="add_blog")
class Blog(Folder):
    __sdi_addable__ = ["Blog Entry"]


def pub_date_sorter(resource, resultset, limit=None, reverse=False):
    catalog = find_catalog(resource, 'navel')
    index = catalog['pub_date']
    resultset = resultset.sort(index, limit=limit, reverse=reverse)
    return resultset
