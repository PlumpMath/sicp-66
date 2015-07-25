;;; 2.2 Hierarchical Data and the Closure Property

;;; 2.2.1 Representing Sequences

define (list car_ . cdr_)
  if cdr_
     (cons car_ (apply list cdr_))
     (cons car_ nil)

define one-through-four
  list 1 2 3 4

define (print-list-items xs)
  if xs
     print 

assert (= 1 (car one-through-four))
assert (= 2 (car (cdr one-through-four)))

  ; List operations

define (list-ref items n)
  if (= n 0)
     (car items)
     (list-ref (cdr items) (- n 1))

assert (= 1 (list-ref one-through-four 0))
assert (= 2 (list-ref one-through-four 1))
assert (= 3 (list-ref one-through-four 2))
assert (= 4 (list-ref one-through-four 3))

define (length items)
  if items
    (+ 1 (length (cdr items)))
    0

assert (= 4 (length one-through-four))

  ; Mapping over lists

define (map f list_)
  if list_
    cons
      f     (car list_)
      map f (cdr list_)
    nil

assert (= 10   (list-ref (map abs (list -10 2.5 -11.6 17)) 0))
assert (= 2.5  (list-ref (map abs (list -10 2.5 -11.6 17)) 1))
assert (= 11.6 (list-ref (map abs (list -10 2.5 -11.6 17)) 2))
assert (= 17   (list-ref (map abs (list -10 2.5 -11.6 17)) 3))
assert (= 4    (length (list -10 2.5 -11.6 17)))

  ; Exercise 2.21

define (square-list items)
  if items
     (cons (square (car items)) (square-list (cdr items)))
     nil

