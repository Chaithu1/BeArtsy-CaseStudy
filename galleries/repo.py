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

def delete_gallery(ds: datastore.Client, gallery_id: int) -> bool:
    key = ds.key(GALLERY_KIND, gallery_id)
    if ds.get(key) is None:
        return False
    ds.delete(key)
    return True

def update_gallery(ds: datastore.Client, gallery: datastore.Entity, updates: dict) -> datastore.Entity:
    gallery.update(updates)
    ds.put(gallery)
    return gallery

def add_art_to_gallery(ds: datastore.Client, gallery: datastore.Entity, art_mini: dict) -> None:
    arts = gallery.get("Arts", []) or []
    arts.append(art_mini)
    gallery["Arts"] = arts
    ds.put(gallery)

def remove_art_from_gallery(ds: datastore.Client, gallery: datastore.Entity, art_id: int) -> None:
    arts = gallery.get("Arts", []) or []
    gallery["Arts"] = [a for a in arts if a.get("A_ID") != art_id]
    ds.put(gallery)


