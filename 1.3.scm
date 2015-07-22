;;; 1.3 Formulating Abstractions with Higher-Order Procedures

;;; 1.3.1 Procedures as Arguments

define (sum-integers a b)
  if (> a b)
     0
     + a (sum-integers (+ a 1) b)

assert
  = 55
    sum-integers 1 10

define (sum-cubes a b)
  if (> a b)
     0
     + (cube a) (sum-cubes (+ a 1) b)

assert
  = 36
    sum-cubes 1 3

; converges to pi/8 (very slowly)
define (pi-sum a b)
  if (> a b)
     0
     +
       / 1.0
         * a (+ a 2)
       pi-sum (+ a 4) b

assert
  > 0.01
    abs (- (pi-sum 1 100) (/ pi 8))

define (sum term a next b)
  if (> a b)
     0
     + (term a)
       (sum term (next a) next b)

define (inc n) (+ n 1)

define (sum-cubes a b)
  sum cube a inc b

assert
  = 3025
    sum-cubes 1 10

define (sum-integers a b)
  sum identity a inc b

define (pi-sum a b)
  define (pi-term x) (/ 1.0 (* x (+ x 2)))
  define (pi-next x) (+ x 4)
  sum pi-term a pi-next b

; Recursion depth exceeded in my python implementation right now.
; TODO: Implement TCO in the interpreter so I don't get stack overflow.
; print (* 8 (pi-sum 1 1000))

assert
  > 0.1
    abs
      - pi
        (* 8 (pi-sum 1 100))

;;; 1.3.2 Constructing Procedures Using Lambda

define (pi-sum a b)
  sum (lambda (x) (/ 1.0 (* x (+ x 2))))
      a
      lambda (x) (+ x 4)
      b

assert
  > 0.1
    abs
      - pi
        (* 8 (pi-sum 1 100))

; TODO: Using 'let' to create local variables.

;;; 1.3.3 Procedures as General Methods

; TODO: There is *a lot* of 1.3 left to do.
