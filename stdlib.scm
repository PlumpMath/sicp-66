; Standard library!
; So that not everything has to be implemented in the python file.

define (> lhs rhs)
  (< rhs lhs)

define (square x)
  (* x x)

define (cube x)
  (* x x x)

define (abs x)
  if (< x 0)
     (- x)
     x

define (indentity x) x

define (cons a b)
  lambda (m)
    (m a b)

define (car x)
  x (lambda (a b) a)

define (cdr x)
  x (lambda (a b) b)

