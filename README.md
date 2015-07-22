SICP
====

Going through the Structure and Interpretation of Programming Languages.

Writing a Python implementation of Scheme that I can use for this purpose as I go along.


Syntax
======

Implicit parentheses
--------------------

As I was learning Scheme (1.1 and 1.2), I noticed an interesting artifact of how the code was being organized.

In order to make the code readable, SICP follows some formatting rules.

If an expression is short, we just keep everything in one line. e.g.

    (+ 1 2)

    (+ (* 3 4 5) 6)

When the expression is large enough, we spread it across multiple lines. Generally, the rule seems to be to indent lines to match the previous arguments. For instance,

    (+ 1
       2  ; the 2 here is indented to match the position of the 1 above.
       3)

Of course this sort of pattern could nest:

    (cond ((= x 1) 2)
          (else (+ x
                   3
                   4)))

When appropriate, the indent doesn't necessarily need to match the argument:

    ; Notice that the line after the 'define', is only indented 2 spaces
    ; and does not match the '(factorial n)'.
    (define (factorial n)
      (if (= n 0)
          1
          (* n (factorial (- n 1)))))


The interesting thing to me is that a lot of these parentheses can be deduced from the indentations.

My parser should accept normal scheme syntax. Inside of parentheses, my parser behaves like normal scheme parsers and ignores newlines and indentations.

But outside of parentheses, my parser uses newlines and indentations to deduce where parentheses should be based on three rules.

  Rule 1: If a line is followed by a more indented line, the parser will insert an open parenthesis at the beginning of this line, and a close parenthesis at the end of the indent block.

So for instance, my parser interprets

    + 1
      2
      3

as

    (+ 1
       2
       3)

  Rule 2: If there are multiple expressions in a line, the parser will insert an open parenthesis at the beginning of the line, and a close parenthesis at the end of the line.

So for instance, my parser interprets

    + 1 2 3

as

    (+ 1 2 3)

while lines like

    1

or
    (+ 1 2 3)

are left alone.

  Rule 3: For any given line, if Rule 1 is applied, Rule 2 will be ignored.

Otherwise, we would have

    + 1
      2

expand to

    ((+ 1)
     2)

which would be bad.

That's it! That's the only syntactic sugar my parser adds.

Of course these combine as well:

    + 1
      * 2 3
      4

is interpreted as

    (+ 1
       (* 2 3)
       4)

