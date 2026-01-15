from google.cloud import datastore

ART_KIND = "Art"

def create_art_entity(ds: datastore.Client, data: dict) -> datastore.Entity:
    key = ds.key(ART_KIND)
    art = datastore.Entity(key=key)
    art.update(data)
    ds.put(art)
    return art

def get_art(ds: datastore.Client, art_id: int) -> datastore.Entity | None:
    return ds.get(ds.key(ART_KIND, art_id))

def list_arts(ds: datastore.Client, *, limit: int | None = None, offset: int = 0) -> list[datastore.Entity]:
    query = ds.query(kind=ART_KIND)
    if limit is None:
        return list(query.fetch(offset=offset))
    return list(query.fetch(limit=limit, offset=offset))

def delete_art(ds: datastore.Client, art_id: int) -> bool:
    key = ds.key(ART_KIND, art_id)
    if ds.get(key) is None:
        return False
    ds.delete(key)
    return True

def update_art(ds: datastore.Client, art: datastore.Entity, updates: dict) -> datastore.Entity:
    art.update(updates)
    ds.put(art)
    return art

def add_gallery_to_art(ds: datastore.Client, art: datastore.Entity, gallery_mini: dict) -> None:
    galleries = art.get("Galleries", []) or []
    galleries.append(gallery_mini)
    art["Galleries"] = galleries
    ds.put(art)

def remove_gallery_from_art(ds: datastore.Client, art: datastore.Entity, gallery_id: int) -> None:
    galleries = art.get("Galleries", []) or []
    art["Galleries"] = [g for g in galleries if g.get("G_ID") != gallery_id]
    ds.put(art)


