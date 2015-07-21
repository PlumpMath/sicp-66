;;; Section 1.1: The Elements of Programming

(assert (= (+ 137 349) 486))
(assert (= (- 1000 334) 666))
(assert (= (* 5 99) 495))
(assert (= (/ 10 5) 2))
(assert (= (+ 2.7 10) 12.7))

(assert (= 75
           (+ 21 35 12 7)))

(assert (= 1200
           (* 25 4 12)))

(assert (= 19
           (+ (* 3 5) (- 10 6))))

; I donno what this value results in. It wasn't in the text.
; You can check if you want.
(+ (* 3
      (+ (* 2 4)
         (+ 3 5)
   (+ (- 10 7)
      6))))

(define size 2)
(assert (= 10 (* 5 size)))

(* (+ 2 (* 4 6))
   (+ 3 5 7))

; Compound procedures
(define (square x) (* x x))

(assert (= 441 (square 21)))
(assert (= 49  (square (+ 2 5))))
(assert (= 81  (square (square 3))))

(define (sum-of-squares x y)
  (+ (square x) (square y)))

(assert (= 25 (sum-of-squares 3 4)))

(define (f a)
  (sum-of-squares (+ a 1) (* a 2)))

(assert (= 136 (f 5)))

;;; Section 1.1.5 The substitution Model for Procedure Application
; -- blah blah blah

; applicative order vs. normal order

; I remember seeing that stuff when I was really interested in theory.
; But at least this section of the book doesn't go that deep in.

;;; Section 1.1.6 Conditional Expressions and Predicates
(define (abs x)
  (cond ((> x 0) x)
        ((= x 0) 0)
        ((< x 0) (- x))))

(assert (= 10 (abs  10)))
(assert (= 10 (abs -10)))
(assert (=  0 (abs   0)))

;; Another way to write the absolute-value procedure is
(define (abs x)
  (cond ((< x 0) (- x))
        (else x)))

(assert (= 10 (abs  10)))
(assert (= 10 (abs -10)))
(assert (=  0 (abs   0)))

(define (abs x)
  (if (< x 0)
      (- x)
      x))

(assert (= 10 (abs  10)))
(assert (= 10 (abs -10)))
(assert (=  0 (abs   0)))

(define x 7)
(assert (and (> x 5) (< x 10)))
(define x 100)
(assert (not (and (> x 5) (< x 10))))

(define (>= x y)
  (or (> x y) (= x y)))

(assert (>= 10 10))
(assert (>= 12 10))

(define (>= x y)
  (not (< x y)))

(assert (>= 10 10))
(assert (>= 12 10))

;;; Exercise 1.1
(assert (= 10 10))
(assert (= 12 (+ 5 3 4)))
(assert (= 8 (- 9 1)))
(assert (= 6 (+ (* 2 4) (- 4 6))))


;;; Exercise 1.4

(define (a-plus-abs-b a b)
  ((if (> b 0) + -) a b))

(assert (= 20 (a-plus-abs-b 10  10)))
(assert (= 20 (a-plus-abs-b 10 -10)))

#|
  ;;; Exercise 1.5

  (define (p) (p))

  (define (test x y)
    (if (= x 0)
        0
        y))

  (test 0 (p))

  ; An interpreter that uses applicative-order evaluation
  ; will go into an infinite loop trying to evalute
  ; the argument '(p)' to test.

  ; An interpreter using normal-order evaluation will expand
  ; (test 0 (p)) to (if (= 0 0) 0 (p))
  ; then looking at condition, we see it will evalute to 0.
|#

;;; Section 1.1.7 Example: Square Roots by Newton's Method

(define (sqrt x)
  (sqrt-iter 1.0 x))

(define (sqrt-iter guess x)
  (if (good-enough? guess x)
       guess
       (sqrt-iter (improve guess x)
                  x)))

(define (improve guess x)
  (average guess (/ x guess)))

(define (average x y)
  (/ (+ x y) 2))

(define (good-enough? guess x)
  (< (abs (- (square guess) x)) 0.001))

(assert (< (abs (- (sqrt  9) 3)) 0.001))
(assert (< (abs (- (sqrt 16) 4)) 0.001))

(assert (< (abs (- 1000
                   (square (sqrt 1000))))
           0.001))

;;; Exercise 1.6

(define (new-if predicate then-clause else-clause)
  (cond (predicate then-clause)
        (else else-clause)))

(assert (= 5 (new-if (= 2 3) 0 5)))
(assert (= 0 (new-if (= 1 1) 0 5)))

#|
  ; Exercise questions is, what happens if:

  (define if new-if)
  (sqrt 9)

  ; Problem is eager evaluation.
  ; then-clause and else-clause arguments are evaluated
  ; before new-if is called.
  ; 'improve' is going to be called regardless of whether
  ; we are 'good-enough?'

  ; When I run the above two lines now, I get

  ; ...
  ; RuntimeError: maximum recursion depth exceeded while calling a Python
  ;   object

  ; Ok, so actually not infinite loop, because right now we are doing this
  ; on the stack. But if we have tail call optimization (TCO), I think
  ; we would probably get infinite loop.
|#

;;; Exercise 1.7

; good-enough? test with ratio instead of static difference

(define (good-enough? guess x)
  ; 1% error margin
  (< (abs (- 1 (/ (square guess) x))) 0.001))

; Not optimal tests (they aren't optimal for the original either),
; but just an easy measure of 'close enough'.
(assert (< (abs (- (sqrt  9) 3)) 0.001))
(assert (< (abs (- (sqrt 16) 4)) 0.001))

(assert (< (abs (- 1000
                   (square (sqrt 1000))))
           0.001))
