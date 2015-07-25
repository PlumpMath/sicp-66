# Python style scheme hybrid.
# More or less rewrite of scheme.py
import fractions
import math
import re
import sys

PATH_TO_STDLIB = './stdlib.scm'

EMPTY_LINE_RE = re.compile(r'^\s+?$', re.MULTILINE|re.DOTALL)
BLOCK_COMMENT_RE = re.compile(r'\s*#\|.*?\|#\s*$', re.MULTILINE|re.DOTALL)
LINE_COMMENT_RE = re.compile(r'\s*;.*?$', re.MULTILINE|re.DOTALL)
FLOAT_RE = re.compile(r'(?:\+|\-)?(?:\.\d+|\d+\.\d*)')
INT_RE = re.compile(r'(?:\+|\-)?\d+')
SYMBOL_RE = re.compile(r'[^\s\(\)\.]+')
ATTRIBUTE_RE = re.compile(r'\.[^\s\(\)\.]+')
SPACE_RE = re.compile(r'(?:(?!\n)\s)+')
UNKNOWN_RE = re.compile(r'\S+')
INDENT_RE = re.compile(r' *')

class Object(object):

  def __new__(cls, *args, **kwargs):
    self = super(Object, cls).__new__(cls, *args, **kwargs)
    self.attributes = dict()

    # These fields are set by the parser if this object is
    # part of an AST.
    self.start = None
    self.end = None
    self.parse_result = None
    return self

  @property
  def location_message(self):
    """Human readable location message as a str."""

    if self.parse_result is None:
      raise ValueError('location_messages are only available for '
                       'objects that were created by a parse')

    return self.parse_result.location_message_at(self.start)

  def setattr(self, attribute, value):
    assert isinstance(attribute, Symbol), attribute
    self.attributes[attribute] = value
    return value

  def getattr(self, attribute):
    assert isinstance(attribute, Symbol), attribute
    return self.attributes[attribute]

class UserObject(Object):

  # TODO: If I put these methods in 'Object', Python complains to me
  #       that super does not have '__add__' or '__eq__', even though
  #       the next class in the mro is e.g. 'int'.
  #       Figure out a (clean) workaround for this so that users can
  #       override builtin classes.
  #       If I can determine there is no clean workaround, I would rather
  #       just not implement the feature.
  def __add__(self, other):
    return (self.getattr(Symbol('+'))(other) if '+' in self.attributes else
            super(Object, self).__add__(other))

  def __eq__(self, other):
    return (self.getattr(Symbol('='))(other) if '=' in self.attributes else
            super(Object, self).__eq__(other))


class List(Object, list):
  def __repr__(self):
    if len(self) == 2 and self[0] == '__string__' and isinstance(self[1], str):
      return repr(str(self[1]))
    elif isattr(self):
      return '%r.%r' % (self[1], self[2])
    else:
      return '(%s)' % ' '.join(map(repr, self))

class Symbol(Object, str):
  def __repr__(self):
    return str(self)

class Int(Object, int):
  pass

class Float(Object, float):
  pass

class Bool(Object, int):
  pass

true = Bool(True)
false = Bool(False)

class Nil(Object):
  def __repr__(self):
    return 'nil'

nil = Nil()

class Function(Object):
  pass

class Lambda(Function):
  def __init__(self, arglist, body, parentscope):
    self.arglist = arglist
    self.body = body
    self.parentscope = parentscope

  def __call__(self, *args):
    if len(self.arglist) != len(args):
      raise TypeError('Lambda expected %d args but found %d' %
                      (len(self.arglist), len(args)))

    scope = Scope(self.parentscope)
    for name, value in zip(self.arglist, args):
      scope.declare(name, value)

    last = None
    for ast in self.body:
      last = scope.eval(ast)

    return last

class BuiltinFunction(Function):
  def __init__(self, function):
    self.function = function

  def __call__(self, *args):
    return self.function(*args)

class BuiltinForm(Object):
  def __init__(self, form):
    self.form = form

  def call(self, argscope, *rawargs):
    return self.form(argscope, *rawargs)

class ParseResult(tuple):
  def __new__(cls, objects, source, filename=None):
    self = super(ParseResult, cls).__new__(cls, objects)
    self.source = source
    self.filename = filename or '<unknown>'
    return self

  def location_message_at(self, index):
    linestart = self.source.rfind('\n', 0, index) + 1
    lineend = self.source.find('\n', index)
    lineend = len(self.source) if lineend == -1 else lineend
    line = self.source[linestart:lineend]
    lineno = self.source.count('\n', 0, index) + 1
    colno = index - linestart
    return ('In file %s, on line %d:\n%s\n%s*' %
            (self.filename, lineno, line, ' ' * colno))

def toObject(x):
  if isinstance(x, Object):
    return x
  elif x == None:
    return nil
  elif isinstance(x, str):
    # TODO: distinguish between Symbol and String types.
    return Symbol(x)
  elif isinstance(x, (list, tuple)):
    return List(map(toObject, x))
  elif isinstance(x, bool):
    return Bool(x)
  elif isinstance(x, int):
    return Int(x)
  elif isinstance(x, float):
    return Float(x)
  else:
    raise ValueError('%s (%s) could not be converted to Object type' %
                     (x, type(x)))

def parse(s, filename=None):
  i = 0
  depth = 0
  metastack = None
  indentstack = None
  lastline = None
  listlocstack = []
  indentlocstack = []

  while True:
    # Skip empty lines, comments, etc.
    while True:
      m = EMPTY_LINE_RE.match(s, i)
      if m:
        i = m.end()
        continue

      m = BLOCK_COMMENT_RE.match(s, i)
      if m:
        i = m.end()
        continue

      m = LINE_COMMENT_RE.match(s, i)
      if m:
        i = m.end()
        continue

      if s.startswith('\n', i):
        i += 1
        continue
      break

    # process a single logical line in the rest of this iteration.
    m = INDENT_RE.match(s, i)
    i = m.end()
    indent = m.group()

    if indentstack is None:
      indentstack = [indent]
      metastack = [[]]
    else:
      if indent in indentstack:
        metastack[-1].append(lastline if len(lastline) > 1 else lastline[0])
        while indent != indentstack[-1]:
          # dedent
          indentstack.pop()
          list_ = metastack.pop()
          list_.start = indentlocstack.pop()
          list_.end = m.start()
          metastack[-1].append(list_)
      elif indent.startswith(indentstack[-1]):
        # indent
        indentlocstack.append(m.end())
        metastack.append(lastline)
        indentstack.append(indent)
      else:
        raise SyntaxError('Invalid indent: ' + repr(indent))

    # Break if we hit end of string.
    if i >= len(s):
      break

    stack = [[]]
    while True:
      # Skip spaces and comments.
      # Also, if we are nested in parenthesis, we want
      # to skip newlines as well.
      while True:
        m = SPACE_RE.match(s, i)
        if m:
          i = m.end()
          continue

        m = BLOCK_COMMENT_RE.match(s, i)
        if m:
          i = m.end()
          continue

        m = LINE_COMMENT_RE.match(s, i)
        if m:
          i = m.end()
          continue

        if i < len(s) and s[i] == '\n' and depth:
          i += 1
          continue
        break

      # Break if we hit end of (logical) line.
      if i >= len(s) or s[i] == '\n':
        break

      # Extract a single token from this line.
      if s[i] == '(':
        stack.append([])
        listlocstack.append(i)
        i += 1
        depth += 1
        continue

      if s[i] == ')':
        if len(stack) <= 1:
          raise SyntaxError('Missing open parenthesis')
        list_ = List(stack.pop())
        stack[-1].append(list_)
        stack[-1][-1].start = listlocstack.pop()
        i += 1
        stack[-1][-1].end = i
        depth -= 1
        continue

      m = FLOAT_RE.match(s, i)
      if m:
        stack[-1].append(Float(m.group()))
        stack[-1][-1].start = m.start()
        stack[-1][-1].end = m.end()
        i = m.end()
        continue

      m = INT_RE.match(s, i)
      if m:
        stack[-1].append(Int(m.group()))
        stack[-1][-1].start = m.start()
        stack[-1][-1].end = m.end()
        i = m.end()
        continue

      m = SYMBOL_RE.match(s, i)
      if m:
        stack[-1].append(Symbol(m.group()))
        stack[-1][-1].start = m.start()
        stack[-1][-1].end = m.end()
        i = m.end()
        continue

      m = ATTRIBUTE_RE.match(s, i)
      if m:
        owner = stack[-1].pop()
        stack[-1].append(toObject(
            ['__attribute__', owner, Symbol(m.group()[1:])]))
        stack[-1][-1].start = m.start()
        stack[-1][-1].end = m.end()
        i = m.end()
        continue

      m = UNKNOWN_RE.match(s, i)
      raise SyntaxError('Unrecognized token: ' + m.group())

    if len(stack) > 1:
      raise SyntaxError('Missing close parenthesis')

    # Save the contents of this logical line until we see the
    # indentation level of the next line.
    lastline = List(stack[0])
    lastline.start = lastline[0].start

  assert len(metastack) == 1, 'internal indentation processing error...'

  parse_result = ParseResult(metastack[0], source=s, filename=filename)

  def annotate(ast):
    ast.parse_result = parse_result
    if isinstance(ast, List):
      for child in ast:
        annotate(child)

  for ast in parse_result:
    annotate(ast)

  return parse_result

class Scope(object):
  def __init__(self, parent=None, table=None):
    self.parent = parent
    self._table = table or dict()
    if parent is None:
      self.callstack = []
      self.current = None
      self.stacktrace = None # snapshot of the callstack when we crash.

  def __call__(self, code):
    if isinstance(code, str):
      code = parse(code)

    if not isinstance(code, ParseResult):
      raise ValueError('If you want to execute code using Scope, you must '
                       'pass either a parsable string or a ParseResult '
                       'instance. Instead you passed a %s' % type(code))

    try:
      for ast in code:
        self.eval(ast)
    except Exception as e:
      if self.root.stacktrace is not None:
        for ast in self.root.stacktrace:
          print(ast.location_message)
        print(e)
        raise
      else:
        raise

  @property
  def root(self):
    return self if self.parent is None else self.parent.root

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
      return self.declare(Symbol(name), BuiltinFunction(func))
    return wrapper

  def setform(self, name):
    def wrapper(func):
      return self.declare(Symbol(name), BuiltinForm(func))
    return wrapper

  def eval(self, ast):
    assert isinstance(ast, Object), ast
    self.root.current = ast
    if isinstance(ast, List):
      form = self.eval(ast[0])
      # TODO: The if and else branch of the following if-else
      #       pairs are very similar. Figure out a clean way
      #       to deduplicate.
      if isinstance(form, Function):
        args = tuple(map(self.eval, ast[1:]))
        self.root.callstack.append(ast)
        try:
          return toObject(form(*args))
        except:
          if self.root.stacktrace is None:
            self.root.stacktrace = tuple(self.root.callstack)
          raise
        finally:
          self.root.callstack.pop()
      else:
        # TODO: Better error message machanism for general forms.
        #       We might need some mechanism for forms to indicate
        #       that it is done 'eval'ing all the arguments it
        #       wants to.
        return toObject(form.call(self, *ast[1:]))
    elif isinstance(ast, Symbol):
      return self[ast]
    elif isinstance(ast, (Int, Float)):
      return ast
    else:
      raise ValueError('Unknown ast type: %s' % type(ast))

# Root scope, where we are going to fill with globals.
root = Scope()

root.declare(toObject('nil'), nil)
root.declare(toObject('true'), true)
root.declare(toObject('false'), false)
root.declare(toObject('pi'), math.pi)

@root.setform('define')
def define(scope, name, *rest):
  if isinstance(name, Symbol):
    value, = map(scope.eval, rest)
    scope.declare(name, value)
    return value

  elif isinstance(name, List):
    arglist = name[1:]
    name = name[0]
    body = rest
    function = Lambda(arglist, body, scope)
    scope.declare(name, function)
    return function

  else:
    raise ValueError("I don't know how to 'define' " + str(name))

def isattr(x):
  return isinstance(x, List) and len(x) == 3 and x[0] == '__attribute__'

@root.setform('set!')
def set_(scope, name, *rest):
  if isinstance(name, Symbol):
    value, = map(scope.eval, rest)
    scope[name] = value
    return value

  elif isattr(name):
    _, rawowner, attribute = name
    owner = scope.eval(rawowner)
    value, = map(scope.eval, rest)
    owner.setattr(attribute, value)
    return value

  elif isinstance(name, List) and isattr(name[0]):
    arglist = name[1:]
    rawowner = name[0][1]
    attribute = name[0][2]
    owner = scope.eval(rawowner)
    body = rest
    function = Lambda(arglist, body, scope)
    owner.setattr(attribute, function)
    return function

  else:
    raise ValueError("I don't know how to 'set!' " + str(name))

@root.setform('__attribute__')
def attribute_(scope, rawowner, attribute):
  owner = scope.eval(rawowner)
  return owner.getattr(attribute)

@root.setform('assert')
def assert_(scope, condition):
  result = scope.eval(condition)
  if not result:
    raise AssertionError(condition)
  return result

@root.setfunc('=')
def equal(a, b):
  return a == b

@root.setfunc('+')
def add(*args):
  result = args[0]
  for arg in args[1:]:
    result += arg
  return result

@root.setfunc('-')
def subtract(a, b=None):
  return -a if b is None else a - b

@root.setfunc('*')
def multiply(*args):
  result = args[0]
  for arg in args[1:]:
    result *= arg
  return result

@root.setfunc('/')
def divide(a, b):
  return a / b

@root.setform('__string__')
def string_(scope, string):
  assert type(string) == Symbol
  return ['__string__', string]

@root.setform('cond')
def cond(scope, *pairs):
  for condition, result in pairs:
    if condition == 'else' or scope.eval(condition):
      return scope.eval(result)

@root.setfunc('<')
def lessthan(lhs, rhs):
  return lhs < rhs

@root.setform('and')
def and_(scope, *exprs):
  last = True
  for expr in exprs:
    last = scope.eval(expr)
    if not last:
      return last
  return last

@root.setform('or')
def or_(scope, *exprs):
  last = False
  for expr in exprs:
    last = scope.eval(expr)
    if last:
      return last
  return last

@root.setfunc('not')
def not_(x):
  return not x

@root.setfunc('print')
def print_(*args):
  print(' '.join(map(str, args)))

@root.setform('if')
def if_(scope, cond, ifblock, elseblock):
  return scope.eval(ifblock if scope.eval(cond) else elseblock)

@root.setfunc('Object')
def Object_():
  return UserObject()

@root.setform('quote')
def quote(scope, x):
  return x

@root.setfunc('list*')
def liststar(*args):
  return args

@root.setfunc('remainder')
def remainder(x, n):
  return x % n

@root.setform('lambda')
def lambda_(scope, arglist, *body):
  return Lambda(arglist, body, scope)

@root.setfunc('gcd')
def gcd_(first, *rest):
  g = first
  for item in rest:
    g = fractions.gcd(item, g)
  return g

# Load the standard library.
with open(PATH_TO_STDLIB) as f:
  root(f.read())

def main():
  # TODO: Real option parsing.
  if len(sys.argv) != 2:
    print('Usage: python %s script.scm' % sys.argv[0])
    return 1

  with open(sys.argv[1]) as f:
    content = f.read()

  root(parse(content, sys.argv[1]))

if __name__ == '__main__':
  exit(main() or 0)

