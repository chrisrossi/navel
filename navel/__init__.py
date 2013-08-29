from substanced.catalog import (catalog_factory, Field, indexview)
from substanced.event import subscribe_created
from substanced.root import Root

from .resources import BlogEntry

def includeme(config):
    config.scan(".")


@catalog_factory('navel')
class NavelCatalogFactory(object):
    pub_date = Field()


@subscribe_created(Root)
def create_catalog(event):
    root = event.object
    catalogs = root['catalogs']
    catalogs.add_catalog('navel')


@indexview(catalog_name='navel', index_name='pub_date')
def pub_date(entry, default):
    if isinstance(entry, BlogEntry):
        date = getattr(entry, 'pub_date', None)
        if date:
            return date
    return default
