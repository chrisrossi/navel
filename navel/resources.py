import colander
import datetime
import deform

from colander.iso8601 import UTC
from persistent import Persistent

from substanced.content import content
from substanced.folder import Folder
from substanced.property import PropertySheet
from substanced.schema import NameSchemaNode, Schema
from substanced.util import renamer


class BlogEntrySchema(Schema):
    title = colander.SchemaNode(colander.String())
    body = colander.SchemaNode(
        colander.String(),
        widget=deform.widget.RichTextWidget(
            options={"theme": "advanced"}))
    pub_date = colander.SchemaNode(colander.DateTime())
    name = NameSchemaNode(editing=True)


class BlogEntryPropertySheet(PropertySheet):
    schema = BlogEntrySchema()


@content("Blog Entry",
         icon="icon-align-left",
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
         icon="icon-font",
         add_view="add_blog")
class Blog(Folder):
    __sdi_addable__ = ["Blog Entry"]
