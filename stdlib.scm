; Standard library!
; So that not everything has to be implemented in the python file.

define (square x)
  (* x x)

define (cube x)
  (* x x x)

define (abs x)
  if (< x 0)
     (- x)
     x

define (indentity x) x
