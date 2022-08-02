import functools
import traceback

from flask import jsonify
from logzero import logger

def on_success_result_success(func):
  """
  Returns dict with `{'result': 'success'}`

  BEWARE: when using with `on_exception_result_failure`, it must
  be listed AFTER `on_exception_result_failure`:
  e.g. `@on_exception_result_failure @on_success_result_success`
  """
  @functools.wraps(func)
  def wrapper():
    func()
    return jsonify({'result': 'success'})
  return wrapper

def on_exception_result_failure(func):
  """
  Returns dict with `{'result': 'failure'}` on exception
  """
  @functools.wraps(func)
  def wrapper():
    try:
      value = func()
      return value
    except:
      logger.warning(traceback.format_exc())
      return jsonify({ 'result': 'failure' })
  return wrapper