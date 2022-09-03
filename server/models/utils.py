from server.database import SessionLocal

def create_n_commit(
  object_creator,
  **kwargs
):
  with SessionLocal() as db:
    obj = object_creator(**kwargs)
    db.add(obj)
    db.commit()