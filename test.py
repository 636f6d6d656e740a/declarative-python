import ast

from main import Transform

def tests():
    def test(function, results):
        tree = ast.parse("\n".join(functions[function]))
        transformer = Transform()
        transformer.defines = {}
        tree = transformer.visit(tree)

        for x in results:
            arguments = x[:-1]
            result = x[-1]
            if not isinstance(arguments, tuple):
                arguments = (arguments,)

            _result = transformer.defines[function](*arguments)

            assert  _result == result, \
                f"assert {function}({', '.join(repr(x) for x in arguments)}) == {result}, but got {_result}"

    functions = {
        # simple literal matching
        "is_zero": (
            "is_zero : 0 = True" ,
            "is_zero : _ = False"
        ),
        # multiple arguments
        "sum": (
            "sum : (a, b, c) =  a + b + c",
        ),
        # recursion
        "fac": (
            "fac : 0 = 1",
            "fac : n = n * fac(n - 1)"
        ),
        # match within a list
        "list_check": (
            "list_check : [1, 2, _, _, 9] = True",
            "list_check : _ = False"
        ),
        # list match
        "tail": (
            "tail : ls@x.xs = xs",
            "tail : [] = []",
            "tail : _ = 'not a list!'"
        ),
        # type match
        "match_int": (
            "match_int : i-int = i",
            "match_int : _ = False"
        ),

        # a more complex example
        "factors": (
            "factors : (n, 1) = {1}",
            "factors : (n, i) = ({i} if n % i == 0 else set()) | factors(n, i - 1)"
          # this would be a better way of using the function,
          # but the limitations of the testing function only allows one function
          # "get_factors : n = factors(n, n)"
        )
    }

    # simple literal matching
    test("is_zero", (
        (0, True),
        (1, False),
        ([0, 3, 4, 2], False),
        ("asdfg", False)
    ))

    # multiple arguments
    test("sum", (
        (3, 4, 5,  12),
        (0, 0, 0,  0)
    ))

    # recursion
    test("fac", (
        (0, 1),
        (1, 1),
        (3, 6),
        (5, 120),
        (20, 2432902008176640000),
    ))

    # match within a list
    test("list_check", (
        ([1, 2, 6, 1, 9], True),
        ([1, 2, 6, 1, 8], False),
        ([], False),
        ("hello", False),
    ))

    # list match
    test("tail", (
        ([1, 2, 3], [2, 3]),
        ([1], []),
        ([], []),
        (99, "not a list!"),
        ("hello world!", "ello world!")
    ))

    # type match
    test("match_int", (
        (3, 3),
        (0, 0),
        (3.3, False),
        ("hello", False)
    ))

    # some more complex examples
    test("factors", (
        (12, 12, {1, 2, 3, 4, 6, 12}),
    ))

if __name__ == "__main__":
    tests()
