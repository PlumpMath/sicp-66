# Simple scheme.
# Rewrite of peme.py, but more scheme-y, and minimal.
import collections
import fractions
import re

SKIP_RE = re.compile(r'(\s|#\|.*?\|#|;.*?\n)*', re.MULTILINE|re.DOTALL)
SYMBOL_RE = re.compile(r'[^\s\(\)]+')

class Object(object):
  """Root of simple scheme's object system."""

class Nil(Object):

  def __contains__(self, item):
    return False

  def __repr__(self):
    return 'nil'

nil = Nil()

class Symbol(Object, str):

  def __repr__(self):
    return str(self)

class Lambda(Object):

  def __init__(self, scope, arglist, body):
    self.scope = scope
    self.arglist = arglist
    self.body = body

  def call(self, args):
    pass

class Cons(Object):

  def __new__(cls, car, cdr):
    self = super(Cons, cls).__new__(cls)
    self.car = car
    self.cdr = cdr
    return self

  def __contains__(self, item):
    return item == self.car or item in self.cdr

  def __iter__(self):
    while self is not nil:
      yield self.car
      self = self.cdr

  def __repr__(self):
    return '(%s)' % ' '.join(map(repr, self))

def parse(s):

  def parseiter(i):
    i = SKIP_RE.match(s, i).end()
    if i >= len(s) or s[i] == ')':
      return i, nil
    elif s[i] == '(':
      i, list_ = parseiter(i+1)
      if i >= len(s):
        raise Symbol('Missing close parenthesis')
      i, rest = parseiter(i+1)
      return i, Cons(list_, rest)
    else:
      m = SYMBOL_RE.match(s, i)
      symbol = Symbol(m.group())
      i, rest = parseiter(m.end())
      return i, Cons(symbol, rest)

  i, ast = parseiter(0)

  if i < len(s):
    print(i, ast)
    raise SyntaxError('Missing open parenthesis')

  return ast

print(parse("""

(1 2 3)

"""))

