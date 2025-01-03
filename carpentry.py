import math

phi = (1 + 5 ** 0.5) / 2 # golden ratio
sqrttwo = math.sqrt(2)
sqrtthree = math.sqrt(3)

def generate_table() -> list[list[float, str]]: 
    '''
    generate a mf table
    '''
    constants = ["pi", "e", "sqrt(2)", "sqrt(3)", "phi", "(1/2)", "(1/3)", "(1/4)", "(1/5)", "(1/6)", 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12] 

    table = []
    for c in constants: # apply unary operations
        table.extend(diversify(c))
        print(f"diversified {c}")
    
    table = binary_operations(table)
    return table
    
def binary_operations(l: list[list[float, str]]) -> list[list[float, str]]:
    '''
    Executes a series of various binary operations on the inputted list.

    l: A list of floats.

    Returns an expanded copy of the list including variants with various binary operations applied.
    '''


    # NOTE: DO THIS IN O(NlogN) with the better algorithm, there's no excuse for it still being O(N^2) :/


    

    al = [] # alt list, so we don't screw up the for loop
    for i in l: # for item in that one list, apply binary operations
        for j in l:
                # Pretty much unreadable. there's stuff here designed to stop random duplicates from appearing
            if i[0] > 0 and j[0] != 1 and j[0] != 0:
                    try:
                        print(i[0])
                        al.append([math.pow(i[0], (1 / j[0])), f'{i[1]} ^ (1/{j[1]})'])
                        al.append([math.pow(i[0], (-1 * j[0])), f'{i[1]} ^ (-{j[1]})'])
                        al.append([math.pow(i[0], j[0]), f'{i[1]} ^ {j[1]}'])
                    except OverflowError:
                        print("too big lol")

            if j[0] != 0 and i[0] != 0:
                if i[0] * j[0] != i[0] and i[0] * j[0] != j[0]:
                    al.append([i[0] * j[0], f'{i[1]} * {j[1]}'])
                
                if j[0] != i[0]:
                    if j[0] != 0:
                        if i[0] / j[0] != i[0] and i[0] / j[0] != j[0]:
                            al.append([i[0] / j[0], f'{i[1]} / {j[1]}'])
                            
                    if i[0] + j[0] != i[0] and i[0] + j[0] != j[0]:
                        al.append([i[0] + j[0], f'{i[1]} + {j[1]}'])

                    if i[0] - j[0] != i[0] and i[0] - j[0] != j[0]:
                        al.append([i[0] - j[0], f'{i[1]} - {j[1]}'])
    l.extend(al)
    return l

def diversify(d: list[float]) -> list[list[float, str]]: 
    '''
    d: list of numbers to start out with.

    Returns a list of lists of c with unary operations applied.

    Sublist format: [constant, 'expression to find constant']
    ex: [sin(c), 'sin({c})']
    '''
    al = []
    match d:

        # c for constant and constant is for me

        case "pi": 
            c = math.pi
        case "e":
            c = math.e
        case "phi":
            c = phi
        case "sqrt(2)":
            c = sqrttwo
        case "sqrt(3)":
            c = sqrtthree
        case "(1/2)":
            c = 1/2
        case "(1/3)":
            c = 1/3
        case "(1/4)":
            c = 1/4
        case "(1/5)":
            c = 1/5
        case "(1/6)":
            c = 1/6
        case _:
            # default case
            c = d

    al.append([c, f'{d}'])
    al.append([math.sin(c), f'sin({d})']) # add options for radians
    al.append([math.cos(c), f'cos({d})'])
    al.append([math.tan(c), f'tan({d})'])

    if c <= 1 and c >= -1:
        al.append([math.asin(c), f'arcsin({d})'])
        al.append([math.acos(c), f'arccos({d})'])

    al.append([math.atan(c), f'tan({d})'])
    
    '''if isinstance(c, int) and c > 0:
        al.append([math.factorial(c), f'{d}!'])'''
    
    if c > 0:
        al.append([math.log(c, math.e), f'ln({d})'])

    return al
