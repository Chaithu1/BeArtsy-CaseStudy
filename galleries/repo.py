from google.cloud import datastore

GALLERY_KIND = "Gallery"

def create_gallery_entity(ds: datastore.Client, data: dict) -> datastore.Entity:
    key = ds.key(GALLERY_KIND)
    gallery = datastore.Entity(key=key)
    gallery.update(data)
    ds.put(gallery)
    return gallery

def get_gallery(ds: datastore.Client, gallery_id: int) -> datastore.Entity | None:
    return ds.get(ds.key(GALLERY_KIND, gallery_id))

def list_galleries(ds: datastore.Client, *, limit=None, offset=0):
    query = ds.query(kind=GALLERY_KIND)
    if limit is None:
        return list(query.fetch(offset=offset))
    return list(query.fetch(limit=limit, offset=offset))
