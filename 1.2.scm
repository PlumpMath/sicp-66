;;; 1.2 Procedures and the Processes They Generate

; python scheme.py 1.2.scm

;;; 1.2.1 Linear Recursion and Iteration

; Naive version
(define (factorial n)
  ; In original version, the following line was
  ; (if (= n 1)
  ; but that would cause infinte loop when
  ; we try to run '(factorial 0)'
  (if (= n 0)
      1
      (* n (factorial (- n 1)))))

(assert (=    1 (factorial 0)))
(assert (=    1 (factorial 1)))
(assert (=    2 (factorial 2)))
(assert (=    6 (factorial 3)))
(assert (=   24 (factorial 4)))
(assert (=  120 (factorial 5)))
(assert (=  720 (factorial 6)))
(assert (= 5040 (factorial 7)))

; Iterative version
(define (factorial-iter product counter)
  (if (< 1 counter)
      (factorial-iter (* counter product)
                      (- counter 1))
      product))

(define (factorial n)
  (factorial-iter 1 n))

(assert (=    1 (factorial 0)))
(assert (=    1 (factorial 1)))
(assert (=    2 (factorial 2)))
(assert (=    6 (factorial 3)))
(assert (=   24 (factorial 4)))
(assert (=  120 (factorial 5)))
(assert (=  720 (factorial 6)))
(assert (= 5040 (factorial 7)))

;;; Exercise 1.9

#|
  ; Which one is iterative process and which one is recursive process?

  ; This one is recursive.
  ; this is not tail call recursive; we can't evaluate the 'inc' until
  ; we evaluate the recursive '+' on the inside.
  (define (+ a b)
    (if (= a 0)
        b
        (inc (+ (dec a) b))))

  ; This one is iterative.
  ; Once we get to the inner '+', we can roll up the stack and just return
  ; the value from the nested recursive call.
  (define (+ a b)
    (if (= a 0)
        b
        (+ (dec a) (inc b))))
|#

;;; Exercise 1.10
(define (A x y)
  (cond ((= y 0) 0)
        ((= x 0) (* 2 y))
        ((= y 1) 2)
        (else (A (- x 1)
                 (A x (- y 1))))))

(assert (= 1024  (A 1 10)))
(assert (= 65536 (A 2  4)))
(assert (= 65536 (A 3  3)))

;;; 1.2.2 Tree Recursion

; tree recursive version.
(define (fib n)
  (cond ((= n 0) 0)
        ((= n 1) 1)
        (else (+ (fib (- n 1))
              (fib (- n 2))))))

(assert (=   0 (fib 0)))
(assert (=   1 (fib 1)))
(assert (=   1 (fib 2)))
(assert (=   2 (fib 3)))
(assert (=   3 (fib 4)))
(assert (=   5 (fib 5)))
(assert (=   8 (fib 6)))
(assert (=  13 (fib 7)))
(assert (=  21 (fib 8)))
(assert (=  34 (fib 9)))

; iterative version.
(define (fib n)
  (fib-iter 1 0 n))

(define (fib-iter next current count)
  (if (= count 0)
      current
      (fib-iter (+ next current) next (- count 1))))

(assert (=   0 (fib 0)))
(assert (=   1 (fib 1)))
(assert (=   1 (fib 2)))
(assert (=   2 (fib 3)))
(assert (=   3 (fib 4)))
(assert (=   5 (fib 5)))
(assert (=   8 (fib 6)))
(assert (=  13 (fib 7)))
(assert (=  21 (fib 8)))
(assert (=  34 (fib 9)))

;;; Exercise 1.11.  A function f is defined by the rule that f(n) = n if n<3
  ; and f(n) = f(n - 1) + 2f(n - 2) + 3f(n - 3) if n >= 3
  ; Write a procedure that computes f by means of a recursive process.
  ; Write a procedure that computes f by means of an iterative process.

(define (f-recursive n)
  (if (< n 3)
      n
      (+ (f-recursive (- n 1))
         (f-recursive (- n 2))
         (f-recursive (- n 3)))))

; Disadvantage of this iterative version is that it does not handle
; negative values of n very well.
(define (f-iterative n)
  (define (iterate current next-1 next-2 count)
    (if (= count 0)
        current
        (iterate next-1
                 next-2
                 (+ current
                    next-1
                    next-2)
                 (- count 1))))
  (iterate 0 1 2 n))

;********************************************************************
;*** Thinking out loud. *********************************************
;********************************************************************
;*** What if we had a different parsing rule for scheme?
;*** One that would get rid of a lot (but not all) of the
;*** parenthesis?
;
; define (f-iterative n)
;   define (iterate current next-1 next-2 count)
;     if (= count 0)
;       current
;       iterate next-1
;               next-2
;               + current
;                 next-1
;                 next2
;               - count 1
;   iterate 0 1 2 n
;
;*** That is, the parsing rule would be the same as I currently
;*** understand it, but with an additonal rule:
;***
;*** If either:
;***   1) The current line has more than one expression in it, or
;***   2) The line after the current one is indented further than this one
;***
;*** then add parenthesis where you would expect them.
;***

(assert (= (f-recursive 0) (f-iterative 0)))
(assert (= (f-recursive 1) (f-iterative 1)))
(assert (= (f-recursive 2) (f-iterative 2)))
(assert (= (f-recursive 3) (f-iterative 3)))
(assert (= (f-recursive 4) (f-iterative 4)))
(assert (= (f-recursive 5) (f-iterative 5)))

;;; Exercise 1.12 ...
  ; Compute the elements of Pascal's triangle by means of a recursive process.

(define (nCr n r)
  (if (or (= n r) (= 0 r))
      1
      (+ (nCr (- n 1) r)
         (nCr (- n 1) (- r 1)))))

(assert (=  1 (nCr 0 0)))
(assert (=  1 (nCr 1 0)))
(assert (=  1 (nCr 1 0)))
(assert (=  1 (nCr 2 0)))
(assert (=  2 (nCr 2 1)))
(assert (=  1 (nCr 2 2)))
(assert (=  1 (nCr 3 0)))
(assert (=  3 (nCr 3 1)))
(assert (=  3 (nCr 3 2)))
(assert (=  1 (nCr 3 3)))
(assert (=  1 (nCr 4 0)))
(assert (=  4 (nCr 4 1)))
(assert (=  6 (nCr 4 2)))
(assert (=  4 (nCr 4 3)))
(assert (=  1 (nCr 4 4)))

;;; Exercise 1.13 Prove that Fib(n) is the closest integer to phi^n / sqrt(5)
  ; where phi = (1 + sqrt(5)) / 2.
  ; Hint: Let psi = (1 - sqrt(5)) / 2 and prove by induction that
  ; Fib(n) = (phi^n - psi^n) / sqrt(5)

  ; Solution:
  ; I leave it as an exercise for the reader to prove
  ; Fib(n) = (phi^n - psi^n) / sqrt(5)
  ; by induction.
  ;
  ; It follows that
  ;  Fib(n) = (phi^n)/sqrt(5) - (psi^n)/sqrt(5)
  ; |Fib(n) - (phi^n)/sqrt(5)| = |(psi^n)/sqrt(5)|
  ;
  ; If you use a calculator (or simple estimates)
  ; it's easy to see that |psi| < 1 and |psi/sqrt(5)| < 1/2
  ;
  ; it follows that |(psi^n)/sqrt(5)| is less than 1/2 for 
  ; all whole numbers n.
  ;
  ; Every real number is within less than 0.5 of at most 1 integer
  ; (otherwise we would have two integers that are < 1 apart).
  ;
  ; It follows that Fib(n) must be the closest integer to (phi^n)/sqrt(5)

;;; Exercise 1.15 The sign of an angle (specified in radians) can be computed
  ; by making use of the approximation sin(x) ~ x if x is sufficiently small
  ; and the trigonometric identity
  ; sin(x) = 3 sin(x/3) - 4 sin^3(x/3)
  ;
  ; For the purposes of this exercise an angle is considered
  ; "sufficiently small" if its magnitude is not greater than 0.1
  ;

(define (cube x) (* x x x))
(define (p x) (- (* 3 x) (* 4 (cube x))))
(define (sine angle)
  (if (not (> (abs angle) 0.1))
      angle
      (p (sine (/ angle 3.0)))))

  ; a. How many times is the procedure p applied when (sin 12.15) is
  ;    evaluated?
  ; b. What is the order of growth in space and number of steps
  ;    (as a function of a) used by the process generated by the sine
  ;    procedure when (sine a) is evaluated?

  ; TODO: Actually solve exercise 1.15.

; -0.40444382284 is what Google says sine 12.15 is on its calculator.
(assert (< (abs (- -0.40444382284 (sine 12.15))) 0.01))

;;; 1.2.4 Exponentiation

; recursive version.
(define (expt b n)
  (if (= n 0)
      1
      (* b (expt b (- n 1)))))

(assert (= 1024 (expt 2 10)))
(assert (=  729 (expt 3  6)))
(assert (=   16 (expt 4  2)))
(assert (=    9 (expt 3  2)))

; naive iterative version.
(define (expt b n)
  (expt-iter b n 1))

(define (expt-iter b n product)
  (if (= n 0)
      product
      (expt-iter b (- n 1) (* product b))))

(assert (= 1024 (expt 2 10)))
(assert (=  729 (expt 3  6)))
(assert (=   16 (expt 4  2)))
(assert (=    9 (expt 3  2)))

; collapsing by even powers version.
(define (expt b n)
  (if (= n 0)
      1
      (if (even? n)
          (square (expt b (/ n 2)))
          (* b (expt b (- n 1))))))

(define (even? n)
  (= (remainder n 2) 0))

(assert (= 1024 (expt 2 10)))
(assert (=  729 (expt 3  6)))
(assert (=   16 (expt 4  2)))
(assert (=    9 (expt 3  2)))

; iterative version of the above exponentiation.
(define (expt b n)
  (expt-iter b n 1))

;;; Exercise 1.16
(define (expt b n)
  (define (expt-iter b n product)
    (if (= n 0)
        product
        (if (even? n)
            (expt-iter (square b) (/ n 2) product)
            (expt-iter b          (- n 1) (* b product)))))
  (expt-iter b n 1))

(assert (= 1024 (expt 2 10)))
(assert (=  729 (expt 3  6)))
(assert (=   16 (expt 4  2)))
(assert (=    9 (expt 3  2)))

;;; Exercise 1.19

  ; Some fun description in text.
  ; Basically ask you to fill in p' and q' in block below.

(define (fib n)
  (fib-iter 1 0 0 1 n))
(define (fib-iter a b p q count)
  (cond ((= count 0) b)
        ((even? count)
         (fib-iter a
                   b
                   <??>      ; compute p'
                   <??>      ; compute q'
                   (/ count 2)))
        (else (fib-iter (+ (* b q) (* a q) (* a p))
                        (+ (* b p) (* a q))
                        p
                        q
                        (- count 1)))))

  ; TODO: Exercise 1.19. Seems like the multiplication trick above
  ;       except for matrices. I kind of want to move on for now,
  ;       but seems like a fun thing I'd like to come back to.

;;; 1.2.5 Greatest Common Divisors.

(define (gcd a b)
  (if (= b 0)
      a
      (gcd b (remainder a b))))

(assert (= 2 (gcd 206 40)))

;;; 1.2.6 Example: Testing for Primality

  ; Searching for divisors

(define (smallest-divisor n)
  (find-divisor n 2))
(define (find-divisor n test-divisor)
  (cond ((> (square test-divisor) n) n)
        ((divides? test-divisor n) test-divisor)
        (else (find-divisor n (+ test-divisor 1)))))
(define (divides? a b)
  (= (remainder b a) 0))

(define (prime? n)
  (= n (smallest-divisor n)))

(assert (prime? 2))
(assert (prime? 3))
(assert (prime? 5))
(assert (prime? 7))

(assert (not (prime? 4)))
(assert (not (prime? 6)))
(assert (not (prime? 8)))
(assert (not (prime? 9)))

  ; The Fermat test
  ; Number theory fun!

(define (expmod base exp m)
  (cond ((= exp 0) 1)
        ((even? exp)
         (remainder (square (expmod base (/ exp 2) m))
                    m))
        (else
         (remainder (* base (expmod base (- exp 1) m))
                    m))))        

(define (fermat-test n)
  (define (try-it a)
    (= (expmod a n n) a))
  (try-it (+ 1 (random (- n 1)))))

(define (fast-prime? n times)
  (cond ((= times 0) true)
        ((fermat-test n) (fast-prime? n (- times 1)))
        (else false)))

; TODO: Figure out a good way to test 'fast-prime?'
; (define (prime? n)
;   (fast-prime? n n))

; (assert (prime? 2))
; (assert (prime? 3))
; (assert (prime? 5))
; (assert (prime? 7))

; (assert (not (prime? 4)))
; (assert (not (prime? 6)))
; (assert (not (prime? 8)))
; (assert (not (prime? 9)))
