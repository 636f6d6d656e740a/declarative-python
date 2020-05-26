import ast, sys

import pattern

class Transform(ast.NodeTransformer):

    defines = {}

    def visit_AnnAssign(self, node):
        if not isinstance(node.target, ast.Name):
            return node

        if isinstance(node.annotation, ast.Tuple):
            p = [pattern.parse(x) for x in node.annotation.elts]
        else:
            p = pattern.parse(node.annotation)

        if node.value == None:
            raise SyntaxError("No function body")

        func_name = node.target.id
        func_body = node.value
        if func_name not in self.defines:
            self.defines[func_name] = pattern.Pattern(func_name, self)
        self.defines[func_name].add(p, func_body)


        return ast.fix_missing_locations(ast.copy_location(ast.Expr(ast.Num(0)), node))


def run(source):
    tree = ast.parse(source)
    transformer = Transform()
    tree = transformer.visit(tree)

    exec(compile(tree, filename="<ast>", mode="exec"), transformer.defines)

if __name__ == "__main__":

    if len(sys.argv) == 2:
        with open(sys.argv[1], "r") as f:
            src = f.read()
        run(src)

    else:
        print(f"Usage: {__file__}.py file.py")
