import pickle
import redis

from server.config import Config

def get_redis_connection():
  return redis.Redis(host=Config.REDIS_HOSTNAME, port=6379)

def get_key(key, connection=None):
  if not connection:
    with get_redis_connection() as connection:
      return pickle.loads(connection.get(key))
  return pickle.loads(connection.get(key))

def get_saved_jobs(connection=None):
  return get_key('saved_jobs', connection)

def get_algorithms_infos(connection=None):
  return get_key('algorithms_infos', connection)

def set_key(key, value, connection=None):
  svalue = pickle.dumps(value)
  if not connection:
    with get_redis_connection() as connection:
      print(f"{key}: {svalue}")
      connection.set(key, svalue)
  connection.set(key, svalue)

def set_saved_jobs(value, connection=None):
  set_key('saved_jobs', value, connection)

def set_algorithms_infos(value, connection=None):
  set_key('algorithms_infos', value, connection)
