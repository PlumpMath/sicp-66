"""
This file is starting to get rather big...

structure of this file:

  Imports and Constants
    imorts
    Precompiled regexes
    path to standard library

  Ast
    Ast and its subclasses
    toast function

  parse functions
    legacyparse
    parse function

  Scheme runtime
    Scheme class
    scm, the default root Scheme scope, and a lot of setfuncs
"""
# TODO: Break this file up into multiple files in a nice way.

import fractions
import math
import random
import re
import sys

INT_RE = re.compile(r'(?:\+|\-|)\d+')
FLOAT_RE = re.compile(r'(?:\+|\-|)(?:\.\d+|\d+\.\d*)')

LINE_COMMENT_RE = re.compile(r';.*?(?=\n|\Z)', re.MULTILINE)
BLOCK_COMMENT_RE = re.compile(r'#\|.*?\|#', re.MULTILINE | re.DOTALL)
EMPTY_LINE_RE = re.compile(r'\A\s*\n|\s*?(?=\n|\Z)', re.MULTILINE)
CONSECUTIVE_LINE_RE = re.compile(r'\n+', re.MULTILINE)
SPACES_RE = re.compile(r'\s*', re.MULTILINE)

PATH_TO_STDLIB = './stdlib.scm'

class Ast(object):
  def __new__(cls, *args, **kwargs):
    self = super(Ast, cls).__new__(cls, *args, **kwargs)
    self.attributes = dict()
    return self

class Nil(Ast):
  def __repr__(self):
    return 'nil'

nil = Nil()

class List(Ast, list):
  def __repr__(self):
    return '(%s)' % ' '.join(map(repr, self))

class Bool(Ast, int):
  pass

true = Bool(True)
false = Bool(False)

class Symbol(Ast, str):
  def __repr__(self):
    if str(self) in ('\t', '-\t', '\n'):
      return repr(str(self))
    else:
      return str(self)

  def __eq__(self, other):
    return type(self) == type(other) and super(Symbol, self).__eq__(other)

class Int(Ast, int):
  pass

class Float(Ast, float):
  pass

class Object(Ast):
  def __str__(self):
    key = Symbol('__str__')
    if key in self.attributes:
      return self.attributes[key](None, [])
    else:
      return super(Object, self).__str__()

  def __eq__(self, other):
    # TODO: Come up with better syntax for,
    #       'evaluate as function' and not as macro.
    return self.attributes[Symbol('=')](None, [other])

  def __add__(self, other):
    return self.attributes[Symbol('+')](None, [other])

class Lambda(Ast):
  def __init__(self, name, arglist, body, parentscm):
    super(Lambda, self).__init__()
    self.name = name
    self.arglist = arglist
    self.body = body
    self.parentscm = parentscm

  def __call__(self, scm, args):
    if len(args) != len(self.arglist):
      raise TypeError('Expected %d arguments but found %d arguments' %
                      (len(self.arglist), len(args)))

    # If scm is None, we assume that 'args' has already been evaluated.
    if scm is not None:
      args = List(map(scm.eval, args))

    childscm = Scheme(self.parentscm)
    for name, value in zip(self.arglist, args):
      childscm.declare(name, value)
    last = None

    for expression in self.body:
      last = childscm.eval(expression)
    return last

class Builtin(Ast):
  def __init__(self, f):
    super(Builtin, self).__init__()
    self.f = f

  def __call__(self, scm, args):
    return self.f(scm, args)

def toast(x):
  if isinstance(x, Ast):
    return x
  elif x == None:
    return nil
  elif isinstance(x, str):
    # TODO: distinguish between Symbol and String types.
    return Symbol(x)
  elif isinstance(x, list):
    return List(map(toast, x))
  elif isinstance(x, bool):
    return Bool(x)
  elif isinstance(x, int):
    return Int(x)
  elif isinstance(x, float):
    return Float(x)
  else:
    raise ValueError('%s (%s) could not be converted to Ast type' %
                     (x, type(x)))

def legacyparse(s):
  """Legacy parser. Used by 'parse'."""
  i = 0
  stack = [[]]
  startstack = []

  while True:

    # skip comments and spaces.
    while i < len(s) and (s[i] == ';' or s.startswith('#|', i) or s[i].isspace()):
      if s[i] == ';':
        while i < len(s) and s[i] != '\n':
          i += 1
      elif s.startswith('#|', i):
        i += 2
        while i < len(s) and not s.startswith('|#', i):
          i += 1
        i += 2
      else:
        i += 1

    # eof
    if i >= len(s):
      break

    # extract one token
    if s[i] == '(':
      stack.append([])
      startstack.append(i)
      i += 1
    elif s[i] == ')':
      if not stack:
        # TODO: Better error message.
        raise SyntaxError('Unexpected close parenthesis')
      items = stack.pop()
      stack[-1].append(List(items))
      i += 1
      stack[-1][-1].start = startstack.pop()
      stack[-1][-1].end = i
    elif FLOAT_RE.match(s, i):
      m = FLOAT_RE.match(s, i)
      j = i
      i = m.end()
      val = Float(m.group())
      val.start = j
      val.end = i
      stack[-1].append(val)
    elif INT_RE.match(s, i):
      m = INT_RE.match(s, i)
      j = i
      i = m.end()
      val = Int(m.group())
      val.start = j
      val.end = i
      stack[-1].append(val)
    elif s[i] == '.':
      j = i
      i += 1
      while i < len(s) and s[i] not in '().' and not s[i].isspace():
        i += 1
      attribute = s[j+1:i]
      if attribute == '':
        raise SyntaxError("Attributes can't have blank names")
      owner = stack[-1].pop()
      stack[-1].append(toast(['__attr__', owner, attribute]))
    else:
      j = i
      while i < len(s) and s[i] not in '().' and not s[i].isspace():
        i += 1
      tok = s[j:i]
      val = Symbol(tok)
      val.start = j
      val.end = i
      stack[-1].append(val)
  # TODO: Better error message.
  if len(stack) != 1:
    raise SyntaxError("Expected close parenthesis")
  return stack[0]

# parses a string and returns a list of Ast elements.
#
# 'parse' should be more or less backwards compatible with 'legacyparse'.
# in that any grammar accepted by legacyparse should be accepted by
# parse, and in that case, they should return the same value.
#
# TODO: Have a much more cleaned up parser algorithm
#
# TODO: Include proper location tracking in the parsing algorithm.
#       This is necessary in order to provide helpful error messages
#       when things go wrong.
def parse(s):
  # First create a new version of the input string where all comments
  # are removed.
  # It is important to do this in such a way that we preserve the
  # indentation.
  #
  # TODO: There are some interesting corner cases here.
  #       Handle those correctly (possibly by discarding regexes
  #       altogether).
  s = LINE_COMMENT_RE.sub('', s)
  s = BLOCK_COMMENT_RE.sub('', s)
  s = EMPTY_LINE_RE.sub('', s)
  s = CONSECUTIVE_LINE_RE.sub('\n', s)

  # Split the string by logical lines.
  # logical lines are newlines that are not inside nested parenthesis.
  # Again, we do this in a way that preserves the indentation of each
  # logical line.
  start = 0
  nest = 0
  lines = []
  for i, c in enumerate(s):
    if c == '(':
      nest += 1
    elif c == ')':
      nest -= 1
    elif nest == 0 and c == '\n':
      lines.append(s[start:i])
      start = i + 1
  if s[start:len(s)]:
    lines.append(s[start:len(s)])

  # Within each line, we can actually parse in the traditional manner.
  indents = []
  stack = [[]]
  expressions = None
  for line in lines:
    indent = SPACES_RE.match(line).group()

    if expressions is None:
      indents.append(indent)

    if indent != indents[-1] and indents[-1] in indent:
      stack.append(List(expressions))
      indents.append(indent)
    else:
      if expressions is None:
        pass
      elif len(expressions) == 1:
        stack[-1].append(expressions[0])
      else:
        stack[-1].append(List(expressions))

      if indent not in indents:
        raise SyntaxError('Invalid indent ' + repr(indent))

      while indent != indents[-1]:
        ast = stack.pop()
        stack[-1].append(ast)
        indents.pop()

    expressions = legacyparse(line)

  if expressions is None:
    pass
  elif len(expressions) == 1:
    stack[-1].append(expressions[0])
  else:
    stack[-1].append(List(expressions))

  while len(indents) > 1:
    ast = stack.pop()
    stack[-1].append(ast)
    indents.pop()

  # TODO: Better error message.
  assert len(stack) == 1, 'indentation processing error...'
  return stack.pop()

# Parse tests
# TODO: Figure out what I want to do with these tests.
#       Do I want to keep these here or move them to
#       use some proper test framework?
assert (
    parse("""

    1
    + 2 3

    """) == [
        toast(1),
        toast(['+', 2, 3])])

assert (
    parse("""

    + 1
      2
      + 3
        4
        5

    """) == [toast(
        ['+', 1,
              2,
              ['+', 3,
                    4,
                    5]])])

assert (
    parse("""

    + 1
      2
      + 3 4 5

    """) == [toast(
        ['+', 1,
              2,
              ['+', 3, 4, 5]])])

assert (
    parse("""

    define (f a b)
      + a
        b

    """) == [toast(
        ['define', ['f', 'a', 'b'],
          ['+', 'a',
                'b']])])


class Scheme(object):
  def __init__(self, parent=None, table=None):
    self.parent = parent
    self._table = table or dict()

  def __call__(self, code):
    if isinstance(code, str):
      code = parse(code)

    for ast in code:
      self.eval(ast)

  def declare(self, symbol, value):
    assert isinstance(symbol, Symbol)
    self._table[symbol] = value

  def __getitem__(self, symbol):
    assert isinstance(symbol, Symbol)
    if symbol in self._table:
      return self._table[symbol]
    elif self.parent:
      return self.parent[symbol]
    else:
      raise KeyError('unrecognized symbol: ' + symbol)

  def __setitem__(self, symbol, value):
    assert isinstance(symbol, Symbol)
    if symbol in self._table:
      self._table[symbol] = value
    elif self.parent:
      self.parent[symbol] = value
    else:
      raise KeyError('assignment to unrecognized symbol: ' + symbol)

  def __contains__(self, symbol):
    assert isinstance(symbol, Symbol)
    if symbol in self._table:
      return True
    elif self.parent:
      return self.parent(symbol)
    else:
      return False

  def setfunc(self, name):
    def wrapper(func):
      ret = self.declare(Symbol(name), Builtin(func))
      return ret
    return wrapper

  def eval(self, ast):
    assert isinstance(ast, Ast), ast
    if isinstance(ast, List):
      f = self.eval(ast[0])
      return toast(f(self, ast[1:]))
    elif isinstance(ast, Symbol):
      return self[ast]
    elif isinstance(ast, (Int, Float)):
      return ast
    else:
      raise ValueError('Unknown ast type: %s' % type(ast))

scm = Scheme()

scm.declare(Symbol('nil'), nil)
scm.declare(Symbol('true'), true)
scm.declare(Symbol('false'), false)
scm.declare(Symbol('pi'), toast(math.pi))

@scm.setfunc('print')
def print_(scm, args):
  x, = map(scm.eval, args)
  print(x)

@scm.setfunc('+')
def add(scm, args):
  if scm is not None:
    args = list(map(scm.eval, args))
  it = iter(args)
  first = next(it)
  for item in it:
    first += item
  return first

@scm.setfunc('-')
def subtract(scm, args):
  if len(args) == 1:
    x, = map(scm.eval, args)
    return -x
  else:
    a, b = map(scm.eval, args)
    return a - b

@scm.setfunc('*')
def multiply(scm, args):
  evaledargs = list(map(scm.eval, args))
  first = evaledargs[0]
  rest = evaledargs[1:]
  for item in rest:
    first *= item
  return first

@scm.setfunc('/')
def subtract(scm, args):
  a, b = map(scm.eval, args)
  return a / b

@scm.setfunc('=')
def equals(scm, args):
  a, b = map(scm.eval, args)
  return a == b

@scm.setfunc('<')
def lessthan(scm, args):
  a, b = map(scm.eval, args)
  return a < b

@scm.setfunc('>')
def lessthan(scm, args):
  a, b = map(scm.eval, args)
  return a > b

@scm.setfunc('assert')
def assert_(scm, args):
  cond, = map(scm.eval, args)
  if not cond:
    raise AssertionError(args[0])

@scm.setfunc('define')
def define(scm, args):
  target = args[0]
  if isinstance(target, Symbol):
    source, = map(scm.eval, args[1:])
    scm.declare(target, source)
  elif (isinstance(target, List) and
        len(target) > 0 and
        all(isinstance(entry, Symbol) for entry in target)):
    name = target[0]
    arglist = target[1:]
    scm.declare(name, Lambda(name, arglist, args[1:], scm))
  else:
    raise ValueError("I don't know how to 'define' " + str(target))

def isattr(x):
  return isinstance(x, List) and len(x) == 3 and x[0] == Symbol('__attr__')

@scm.setfunc('set!')
def define(scm, args):
  target = args[0]
  if isinstance(target, Symbol):
    source, = map(scm.eval, args[1:])
    scm[target] = source
  elif (isinstance(target, List) and
        len(target) > 0 and
        isattr(target[0]) and
        all(isinstance(entry, Symbol) for entry in target[1:])):
    owner = scm.eval(target[0][1])
    attribute = target[0][2]
    arglist = target[1:]
    owner.attributes[attribute] = Lambda(attribute, arglist, args[1:], scm)
  elif isattr(target):
    _, value = args
    owner = scm.eval(target[1])
    attribute = target[2]
    owner.attributes[attribute] = scm.eval(value)
  else:
    raise ValueError("I don't know how to 'set!' " + str(target))

@scm.setfunc('cond')
def cond(scm, args):
  for condition, result in args:
    if condition == Symbol('else') or scm.eval(condition):
      return scm.eval(result)

@scm.setfunc('if')
def if_(scm, args):
  cond, lhs, rhs = args
  return scm.eval(lhs if scm.eval(cond) else rhs)

@scm.setfunc('and')
def and_(scm, args):
  # If you use 'all', you lose the actual value -- you only get
  # True of False
  for arg in args:
    result = scm.eval(arg)
    if not result:
      return result
  return True

@scm.setfunc('or')
def or_(scm, args):
  # If you use 'any', you lose the actual value -- you only get
  # True of False
  for arg in args:
    result = scm.eval(arg)
    if result:
      return result
  return False

@scm.setfunc('not')
def not_(scm, args):
  x, = map(scm.eval, args)
  return not x

@scm.setfunc('abs')
def abs_(scm, args):
  x, = map(scm.eval, args)
  return abs(x)

@scm.setfunc('remainder')
def even(scm, args):
  x, n = map(scm.eval, args)
  return x % n

@scm.setfunc('random')
def random_(scm, args):
  x, = map(scm.eval, args)
  # NOTE: randint includes x in the range of possible values.
  return random.randint(0, x)

@scm.setfunc('lambda')
def lambda_(scm, args):
  arglist = args[0]
  body = args[1:]
  return Lambda('<lambda>', arglist, body, scm)

@scm.setfunc('quote')
def quote(scm, args):
  x, = args
  return x

@scm.setfunc('__attr__')
def attr_(scm, args):
  ownerexpr, name = args
  owner = scm.eval(ownerexpr)
  assert type(name) == Symbol
  return owner.attributes[name]

@scm.setfunc('Object')
def Object_(scm, args):
  return Object()

@scm.setfunc('list*')
def liststar(scm, args):
  return list(map(scm.eval, args))

@scm.setfunc('gcd')
def gcd_(scm, args):
  a, b = map(scm.eval, args)
  return fractions.gcd(a, b)

# Load the standard library.
with open(PATH_TO_STDLIB) as f:
  scm(f.read())

def main():
  # TODO: Real option parsing.
  if len(sys.argv) == 2:
    parser = parse
  elif len(sys.argv) == 3 and sys.argv[2] == '--use-legacy-parser':
    parser = legacyparse
  else:
    print('Usage: python %s script.scm [--use-legacy-parser]' % sys.argv[0])
    return 1

  with open(sys.argv[1]) as f:
    content = f.read()

  scm(parser(content))


if __name__ == '__main__':
  exit(main() or 0)
