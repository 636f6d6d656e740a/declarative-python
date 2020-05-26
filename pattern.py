import ast

class Pattern:
    def __init__(self, name, transform):
        self.name = name
        self.components = []
        self.transform = transform

    def __repr__(self): return f"{self.name}({', '.join(repr(x) for x in self.components)})"

    def add(self, component, body):
        self.components.append((component, body))

    def check_arg(self, pattern, arg):
        """
        check if a function argument fits the corresponding pattern
        """
        if isinstance(pattern, Literal):
            return arg == pattern.value

        if isinstance(pattern, Type):
            return {pattern.bind: arg} if isinstance(arg, pattern.type) else False

        if isinstance(pattern, Name):
            if pattern.name == "_":
                return True
            else:
                return {pattern.name: arg}

        if isinstance(pattern, List):
            try: iter(arg)
            except TypeError: return False
            v = [self.check_arg(p, a) for p, a in zip(pattern.values, arg)]
            if not v and pattern.values:
                return False
            b = {}
            for val in v:
                if isinstance(v, dict):
                    b.update(val)
            return False if not all(v) else (b if b else True)

        if isinstance(pattern, ListMatch):
            try: iter(arg)
            except TypeError: return False

            if len(arg) == 0:
                return False

            b = {}

            for i, c in enumerate(pattern.components[:-1]):
                try: b.update({c: arg[i]})
                except IndexError: b.update({c: []})

            rest = arg[len(pattern.components)-1:]

            if len(rest) == 1:
                rest = rest[0]
            b.update({pattern.components[-1]: rest})
            if pattern.list_name:
                b.update({pattern.list_name: arg})

            return b

        raise UserWarning(f"Invalid {pattern}")

    def __call__(self, *args):
        for pattern, body in self.components:
            index = 0

            # allow recursion by adding itself to defined vars
            binds = {self.name: self.__call__}

            if not (isinstance(pattern, list) or isinstance(pattern, tuple)):
                pattern = (pattern,)

            # is pattern matched

            for p in pattern:
                x = self.check_arg(p, args[index])
                if x:
                    if isinstance(x, dict):
                        binds.update(x)
                    index += 1
                else:
                    break

            else:
                return eval(compile(ast.Expression(body), '', 'eval'), {**self.transform.defines, **binds})

        raise TypeError(f"Non-exhaustive patterns in function '{self.name}'")

class PatternComponent:
    def __repr__(self):
        return f"{self.__class__.__name__}({', '.join(f'{k}={v}' for k, v in self.__dict__.items())})"

class List(PatternComponent):
    def __init__(self, values, is_tuple=False):
        self.values = values
        self.is_tuple = is_tuple

class ListMatch(PatternComponent):
    def __init__(self, components, list_name=None):
        self.components = components
        # `a_list@(head:rest)` syntax, list_name is `a_list`
        self.list_name = list_name

class Literal(PatternComponent):
    def __init__(self, value):
        self.value = value

class Type(PatternComponent):
    def __init__(self, type, bind=None):
        self.type = type
        self.bind = bind

class Name(PatternComponent):
    def __init__(self, name):
        self.name = name


def parse(node):
    def parse_list_match(n):
        if isinstance(n, ast.Attribute):
            return parse_list_match(n.value) + [n.attr]
        elif isinstance(n, ast.Name):
            return [n.id]
        else:
            raise SyntaxError("List slice match must be an identifier")

    if isinstance(node, ast.Attribute):
        components = parse_list_match(node)
        return ListMatch(components)
    elif isinstance(node, ast.BinOp) and isinstance(node.op, ast.MatMult):
        if not isinstance(node.left, ast.Name):
            raise SyntaxError("List slice match must be an identifier")
        list_name = node.left.id
        components = parse_list_match(node.right)
        return ListMatch(components, list_name)

    elif isinstance(node, ast.Num):
        return Literal(node.n)
    elif isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.USub) and isinstance(node.operand, ast.Num):
        return Literal(-node.operand.n)

    elif isinstance(node, ast.Str):
        return Literal(node.s)

    elif isinstance(node, ast.NameConstant):
        return Literal(node.value)

    elif isinstance(node, ast.List):
        return List([parse(x) for x in node.elts])
    elif isinstance(node, ast.Tuple):
        return List(tuple(parse(x) for x in node.elts), True)

    elif isinstance(node, ast.Name):
        return Name(node.id)

    elif isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.USub):
        t = eval(compile(ast.Expression(node.operand), '', 'eval'))
        if not isinstance(t, type):
            raise TypeError(f"Invalid type '{t}'")
        return Type(t)

    elif isinstance(node, ast.BinOp) and isinstance(node.op, ast.Sub):
        name = node.left
        if not isinstance(name, ast.Name):
            raise SyntaxError("Invalid bind name '{name}'")
        t = eval(compile(ast.Expression(node.right), '', 'eval'))
        if not isinstance(t, type):
            raise TypeError(f"Invalid type '{t}'")
        return Type(t, name.id)


    else:
        raise SyntaxError("Invalid Syntax")
