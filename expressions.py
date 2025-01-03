import sympy
from sympy.parsing.latex import parse_latex
from sympy.parsing.sympy_parser import parse_expr
from sympy import symbols

x = symbols('x')

def sympytest():


    expression = parse_latex(r"2^{3}" + "=x")
    print(expression)
    result = sympy.solve(expression)
    return print(result[0])


def solve(expression: str, isLatex: bool) -> float:

    '''
    Uses Sympy to parse and solve an expression (NOT an equation, no "=" sign.)

    expression: The expression in question
    isLatex: Is the expression in Latex (True) or "normal" form (False/None)?

    Returns the value of the expression expressed as a float.
    '''

    if isLatex:
        expression = parse_latex(expression + "=x")
    else:
        expression = parse_expr(expression + "=x")


    result = sympy.solve(expression, dict=True)
    print(result)
    print(result[0].get(x))
    return result[0].get(x)

if __name__ == "__main__":
    sympytest()
    print("If you're looking for flask stuff, try running main.py!")