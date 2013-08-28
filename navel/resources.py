from persistent import Persistent

from substanced.content import content
from substanced.folder import Folder


@content("Blog Entry",
         icon="icon-align-left",
         add_view="add_blog_entry")
class BlogEntry(Persistent):

    def __init__(self, title='', body='', pub_date=''):
        self.title = title
        self.body = body
        self.pub_date = pub_date


@content("Blog",
         icon="icon-font",
         add_view="add_blog")
class Blog(Folder):
    __sdi_addable__ = ["Blog Entry"]
