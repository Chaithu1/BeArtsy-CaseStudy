from google.cloud import datastore

USER_KIND = "User"

def create_user_entity(ds: datastore.Client, data: dict) -> datastore.Entity:
    key = ds.key(USER_KIND)
    user = datastore.Entity(key=key)
    user.update(data)
    ds.put(user)
    return user

def get_user(ds: datastore.Client, user_id: int) -> datastore.Entity | None:
    return ds.get(ds.key(USER_KIND, user_id))

def delete_user(ds: datastore.Client, user_id: int) -> bool:
    key = ds.key(USER_KIND, user_id)
    if ds.get(key) is None:
        return False
    ds.delete(key)
    return True

def list_users(ds: datastore.Client) -> list[datastore.Entity]:
    query = ds.query(kind=USER_KIND)
    return list(query.fetch())

def add_friend(ds: datastore.Client, user1: datastore.Entity, friend_id: int) -> None:
    friends = user1.get("U_Friends", []) or []
    if friend_id not in friends:
        friends.append(friend_id)
    user1["U_Friends"] = friends
    ds.put(user1)

def remove_friend(ds: datastore.Client, user1: datastore.Entity, friend_id: int) -> None:
    friends = user1.get("U_Friends", []) or []
    friends = [fid for fid in friends if fid != friend_id]  # remove all occurrences
    user1["U_Friends"] = friends
    ds.put(user1)