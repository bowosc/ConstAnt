from sympy import Expr, sympify

import confind as cf

# expression data format primer:
# [value: float, expression: str]

def formatForTable(expression: str) -> list[float, str]:
    '''
    Formats a string expression into a usable form for the table.
    Format: [value: float, expression: str]
    '''
    return [Expr.evalf(sympify(expression)), expression]

def prepExpressionString(expression:list[float, str]) -> None:
    '''
    Preps the string part of the expression data thing IN PLACE into a more user-friendly version.
    '''
    expression[1] = expression[1].replace('E', 'e')
    return

def applyUnaryOps(sub: str) -> list[float, str]:
    '''
    Diversifies a single value into a list of expressions by applying different unary operations.

    sub: A value/number/constant.

    Returns a list of expressions in [value: float, expression: str] form.
    '''
    result = []

    UNARYOPS = ['sin', 'cos', 'ln', '']

    for i in UNARYOPS:
        if i == '':
            expression = f'{sub}'
        elif str(sub)[0] == "(" and str(sub)[-1] == ")": 
            # if the subexpression already has parens, we don't need to add more
            expression = f'{i}{sub}'
        else:
            expression = f'{i}({sub})'

        if Expr.evalf(sympify(expression)) > 0:
            result.append(formatForTable(expression))



    return result

def applyBinaryOps(asub: list[float, str], bsub: list[float, str], isSecondLayer: bool = False) -> list[float, str]:
    '''
    Funnels two subexpressions into a third by applying binary operations.

    asub: First subexpression.
    bsub: First subexpression.
    isSecondLayer: Should be true if you want another bubble of parentheses. This will hopefully be deprecated when I figure out a better system for parentheses.

    Returns a third subexpression in the same format as the two in the parameters.
    '''
    result = []

    if isSecondLayer:
        if asub[0] != bsub[0] and asub[0] != 0 and asub[0] != 0:
            result.append(formatForTable(f'({asub[1]})*({bsub[1]})'))
            result.append(formatForTable(f'({asub[1]})/({bsub[1]})'))
            result.append(formatForTable(f'{asub[1]}+{bsub[1]}'))
        if asub[0] != 0 and bsub[0] != 0:
            result.append(formatForTable(f'({asub[1]})^({bsub[1]})'))
    else:
        if asub[0] != bsub[0] and asub[0] != 0 and asub[0] != 0:
            result.append(formatForTable(f'{asub[1]}*{bsub[1]}'))
            result.append(formatForTable(f'{asub[1]}/{bsub[1]}'))
            result.append(formatForTable(f'{asub[1]}+{bsub[1]}'))
        if asub[0] != 0 and bsub[0] != 0:
            result.append(formatForTable(f'{asub[1]}^{bsub[1]}'))

    return result

def generateTable() -> list[list[float, str]]:
    '''
    generate a mf table
    '''
    strtable = []
    table = []

    CONSTANTS = ["pi", "E", "(1/2)", "(1/3)", "(1/4)", "(1/5)", "(1/6)", 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12] 

    for i in CONSTANTS:
        strtable.extend(applyUnaryOps(i))
        print(f"Unary - extended {i}.")

    alttable = []
    for a in strtable:
        for b in strtable:
            alttable.extend(applyBinaryOps(a, b))
            print(f"Binary - extended {a}, {b}.")

    strtable.extend(alttable)
    for i in strtable:
        i=prepExpressionString(i)

    return strtable


def generateFancyNumbers() -> list[list[float, str]]:

    PERFECT_NUMBERS = []
    MERSENNE_PRIMES = []
    return



if __name__ == "__main__":
    print(generateTable())