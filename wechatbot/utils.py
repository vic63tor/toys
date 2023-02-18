from errors import MismatchError
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
