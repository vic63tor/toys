from errors import MismatchError

from functools import wraps
import time
import ast

import whisper

def transcribe(path_to_recording, lang=None):
  model = whisper.load_model("small")
  result = model.transcribe(path_to_recording)
  return result["text"]
  
def is_python_statement(s): #SHOULD IMPLEMENT AST.PARSE INSTEAD!
  try:
    eval(s)
  except:
    return False
  if s.isdigit():
    return False
  return True

def compare_similarity(a:str, b:str, c:str):
  if (a == c) != (b == c):
    return a if a == c else b
  else:
    raise MismatchError(f"UID {c}, FromUserName{b}, ToUserName{c} ")

def compare_difference(a:str, b:str, c:str):
  if (a != c) != (b != c):
    return a if a != c else b
  else:
    raise MismatchError(f"UID {c}, FromUserName{b}, ToUserName{c} ")


def async_timeit(func):
  @wraps(func)
  async def timeit_wrapper(*args, **kwargs):
      start_time = time.monotonic_ns()
      result = await func(*args, **kwargs)
      end_time = time.monotonic_ns()
      total_time = end_time - start_time
      print(f'Function {func.__name__}{args} {kwargs} Took {total_time:.4f} seconds')
      return result
  return timeit_wrapper