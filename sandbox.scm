define x 10
set! x.a 50
; print x.a
; print x

define (Point x y)
  define self (Object)
  set! (self.__str__)
    (quote point)
  set! self.x x
  set! self.y y
  self

define p (Point 55 66)

assert (= 55 p.x)
assert (= 66 p.y)

assert
  = (quote (1 2 3))
    (list*  1 2 3)
