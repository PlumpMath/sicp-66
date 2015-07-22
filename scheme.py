import random
import sys

class Ast(object):
  pass

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
    return str(self)

  def __eq__(self, other):
    return type(self) == type(other) and super(Symbol, self).__eq__(other)

class Int(Ast, int):
  pass

class Float(Ast, float):
  pass

class Lambda(Ast):
  def __init__(self, name, arglist, body, parentscm):
    self.name = name
    self.arglist = arglist
    self.body = body
    self.parentscm = parentscm

  def __call__(self, scm, args):
    if len(args) != len(self.arglist):
      raise TypeError('Expected %d arguments but found %d arguments' %
                      (len(self.arglist), len(args)))
    childscm = Scheme(self.parentscm)
    for name, value in zip(self.arglist, List(map(scm.eval, args))):
      childscm.table[name] = value
    last = None
    for expression in self.body:
      last = childscm.eval(expression)
    return last

class Builtin(Ast):
  def __init__(self, f):
    self.f = f

  def __call__(self, scm, args):
    return self.f(scm, args)

def toast(x):
  if isinstance(x, Ast):
    return x
  elif x == None:
    return nil
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

def parse(s):
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
    else:
      j = i
      while i < len(s) and s[i] not in ('(', ')') and not s[i].isspace():
        i += 1
      tok = s[j:i]
      try:
        val = Int(tok)
      except ValueError:
        try:
          val = Float(tok)
        except ValueError:
          val = Symbol(tok)
      val.start = j
      val.end = i
      stack[-1].append(val)
  # TODO: Better error message.
  if len(stack) != 1:
    raise SyntaxError("Expected close parenthesis")
  return stack[0]

class Scheme(object):
  def __init__(self, parent=None, table=None):
    self.parent = parent
    self.table = table or dict()

  def __call__(self, code):
    if isinstance(code, str):
      code = parse(code)

    for ast in code:
      self.eval(ast)

  def __getitem__(self, symbol):
    assert isinstance(symbol, Symbol)
    if symbol in self.table:
      return self.table[symbol]
    elif self.parent:
      return self.parent[symbol]
    else:
      raise KeyError('unrecognized symbol: ' + symbol)

  def setfunc(self, name):
    def wrapper(func):
      ret = self.table[Symbol(name)] = Builtin(func)
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

scm.table[Symbol('nil')] = nil
scm.table[Symbol('true')] = true
scm.table[Symbol('false')] = false

@scm.setfunc('print')
def print_(scm, args):
  x, = map(scm.eval, args)
  print(x)

@scm.setfunc('+')
def add(scm, args):
  return sum(map(scm.eval, args))

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
    scm.table[target] = source
  elif (isinstance(target, List) and
        len(target) > 0 and
        all(isinstance(entry, Symbol) for entry in target)):
    name = target[0]
    arglist = target[1:]
    scm.table[name] = Lambda(name, arglist, args[1:], scm)
  else:
    raise ValueError("I don't know how to 'define' " + str(target))

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

@scm.setfunc('square')
def square(scm, args):
  x, = map(scm.eval, args)
  return x * x

@scm.setfunc('random')
def random_(scm, args):
  x, = map(scm.eval, args)
  # NOTE: randint includes x in the range of possible values.
  return random.randint(0, x)

def main():
  if len(sys.argv) > 1:
    with open(sys.argv[1]) as f:
      content = f.read()
  else:
    content = sys.stdin.read()
  scm(content)

if __name__ == '__main__':
  main()
