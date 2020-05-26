# declarative-python

Declarative function definitions and pattern matching in python using the `ast` module.

## Usage

Run `main.py file.py` to run a file containing function declarations.
Run `test.py` to run the test cases.

## Functions
Declarative functions can be declared with: 
```python

f : x = x

```

And for multiple argument functions:
```python

f : (a, b) = a + b

```

Any assignment that includes a type annotation will be interpreted as a function.

## Pattern Matching

Pattern matching allows different function bodies to be evaluated based on the arguments passed.

The different patterns you can match on are:
```python

# named argument
a

# literal
3

# list literal, can contain subpatterns
[1, 2, 3]

# list match
# `list @` optionally captures the entire list into a variable
list @ x . y . xs

# type match
-int
# or bound to a variable
x - float

# any value (to be discarded)
_

```

A single function can have multiple patterns and associated bodies.
For example, the factorial function could be defined recursively as:

```python

factorial : 0 = 1
factorial : n = n * factorial(n - 1)

```

The tail function could be defined as:

```python

tail : x.xs = xs
tail : _ = "not a list!"

```

If a function is called and no patterns are matched, an error will be raised.

```python

>>> foo : 5 = 5
>>> foo(10)

>>> TypeError: Non-exhaustive patterns in function 'foo'

```
