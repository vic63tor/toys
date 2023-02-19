from errors import MismatchError
import ast

def is_python_statement(s): #SHOULD IMPLEMENT AST.PARSE INSTEAD! Also should implement a python repl
  try:
    eval(s)
  except:
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
