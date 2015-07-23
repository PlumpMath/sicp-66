;;; 2.1 Introduction to Data Abstraction

;;; 2.1.1 Example: Arithmetic Operations for Rational Numbers

define (make-rat numerator denominator)
  define x (Object)

  define g (gcd numerator denominator)
  set! numerator (/ numerator g)
  set! denominator (/ denominator g)

  set! x.numerator numerator
  set! x.denominator denominator

  set! (x.= y)
    and (= x.numerator y.numerator)
        (= x.denominator y.denominator)

  set! (x.+ y)
    make-rat
      +
        * x.numerator
          y.denominator
        * y.numerator
          x.denominator
      * x.denominator
        y.denominator

  x

assert
  = (make-rat 1 2)
    + (make-rat 1 4)
      (make-rat 1 4)

  ; Pairs

  ; TODO: Figure out how much I care for cons cells.
  ;       I realize that cons cells are a big part of things that
  ;       feel functional programmy, but not entirely sold on its
  ;       benefits just yet.

;;; 2.1.2 Abstraction Barriers

;;; 2.1.3 What is meant by data?

  ; Using functions as a way to store data.
  ; Interesting...
define (cons x y)
  define (dispatch m)
    cond ((= m 0) x)
         ((= m 1) y)
         (else (error))

define (car z) (z 0)

define (cdr z) (z 1)

  ; ** Quote **
  ; The point of exhibiting the procedural representation of pairs is not that
  ; our language works this way (Scheme, and Lisp systems in general,
  ; implement pairs directly, for efficiency reasons) but that it could work
  ; this way.

;;; Exercise 2.4
  ; What is the corresponding definition of cdr?

define (cons x y)
  lambda (m) (m x y)

define (car z)
  z (lambda (p q) p)

  ; Solution

define (cdr z)
  z (lambda (p q) q)

  ; Dang. This makes me ashamed of my old data structures and how I
  ; used to only think of data with where the bits and bytes are.


;;; Exercise 2.6
  ; TODO: Church numerals exercise. Seems like fun.

;;; 2.1.4 Extended Exercise: Internval Arithmetic

  ; TODO: This section

