from sympy import Expr, sympify

from confind import users, solves, consts, constvotes, traits, db, does_table_exists

# expression data format primer:
# [value: float, expression: str]

PREGEN_CONST_CREATOR = "Server"
PREGEN_CONST_NAME = ""
PREGEN_CONST_NOTES = ""


def formatForTable(expression: str) -> tuple[float,str]:
    '''
    Formats a string expression into a usable form for the table.
    Format: [value: float, expression: str]
    '''
    print(f"Formatting {expression} for table!")
    return [Expr.evalf(sympify(expression*1)), expression] # expression*1 makes sure plain ol' integers turn to flots, e.g. 1.000000000


def prepExpressionString(expression: tuple[float,str]) -> None:
    '''
    Preps the string part of the expression data thing IN PLACE into a more user-friendly version.
    '''
    expression[1] = expression[1].replace('E+', 'e').replace('E', 'e')
    return 

def applyUnaryOps(sub: str) -> tuple[float,str]:
    '''
    Diversifies a single value into a list of expressions by applying different unary operations.

    sub: A value/number/constant.

    Returns a list of expressions in [value: float, expression: str] form.
    '''
    result = []

    UNARYOPS = ['sin', 'cos', 'ln']

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

def applyBinaryOps(asub: tuple[float,str], bsub: tuple[float,str], isSecondLayer: bool = False) -> tuple[float,str]:
    '''
    Funnels two subexpressions into a third by applying binary operations.

    asub: First subexpression.
    bsub: First subexpression.
    isSecondLayer: Should be true if you want another bubble of parentheses. This will hopefully be deprecated when I figure out a better system for parentheses.

    Returns a third subexpression in the same format as the two in the parameters.
    '''
    result = []

    if isSecondLayer: #add parens
        if asub[0] != bsub[0] and asub[0] != 0 and asub[0] != 0:
            if asub !=1 and bsub !=1:
                result.append(formatForTable(f'({asub[1]}) * ({bsub[1]})'))
                result.append(formatForTable(f'({asub[1]}) / ({bsub[1]})'))
            result.append(formatForTable(f'{asub[1]} + {bsub[1]}'))
        if asub[0] != 0 and bsub[0] != 0 and bsub[0] < 32 and asub != 1: # stupid huge consts slow down generation by a lot, and 1^n doesn't help anyone
            result.append(formatForTable(f'({asub[1]})^({bsub[1]})'))
    else:
        if asub[0] != bsub[0] and asub[0] != 0 and asub[0] != 0:
            if asub !=1 and bsub !=1:
                result.append(formatForTable(f'{asub[1]} * {bsub[1]}'))
                result.append(formatForTable(f'{asub[1]} / {bsub[1]}'))
            result.append(formatForTable(f'{asub[1]} + {bsub[1]}'))
        if asub[0] != 0 and bsub[0] != 0 and bsub[0] < 32 and asub != 1: # stupid huge consts slow down generation by a lot, and 1^n doesn't help anyone
            result.append(formatForTable(f'{asub[1]} ^ {bsub[1]}'))
    return result
    

def generateBoringTable() -> list[tuple[float, str]]:
    '''
    Generate a bunch of "boring" numbers through a method of applying different operations to a list of constants.

    Generates a list of [float, str] tuples containing a number and the expression that results in that number.
    The float part is the number itself, the str is the expression.

    Returns the list.
    '''
    strtable = []

    CONSTANTS = ["pi", "E", "(1/2)", "(1/3)", "(1/4)", "(1/5)", "(1/6)", 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12] 

    for i in CONSTANTS:
        strtable.extend(applyUnaryOps(i))
        
        print(f"Unary - extended {i}.")


        # UNARY OPS SHOULD take formatForTable()'ed datas
    
    alttable = []
    for a in CONSTANTS:
        for b in CONSTANTS:
            alttable.extend(applyBinaryOps(formatForTable(a), formatForTable(b)))
            print(f"Binary - extended {a}, {b}.")

    strtable.extend(alttable)

    alttable = []
    
    
    for a in strtable:
        for b in CONSTANTS:
            b = formatForTable(b)
            print(f"{len(alttable)} / {len(strtable)*len(CONSTANTS)} completed.")
            alttable.extend(applyBinaryOps(a, b, isSecondLayer=True))
            print(f"Second Round Binary - extended {a}, {b}.")
    strtable.extend(alttable)
    alttable = []
    

    for i in strtable:
        print(f"Prepping string for {i}")
        i = prepExpressionString(i)

    print(strtable)
        

    return strtable

def generateCoolTable() -> list[tuple[consts, list[str]]]:
    '''
    Returns a bunch of "interesting" numbers, in the format:

    [ 
        [const1, [tag1, tag2, tag3]],
        [const2, [tag1, tag2, tag3]],
        [const3, [tag1, tag2, tag3]]
    ]
    '''
    # DO NOT PERFORM ANY OPERATIONS ON THESE! IT WILL RESULT IN DUPLICATES!
    PERFECT_NUMBERS = []
    MERSENNE_PRIMES = []

    cools = []
    cools.append([consts(Expr.evalf(sympify("111111*111111")), "111111*111111", "Bowie's number", "Bowie", "my special friend"), ["The REAL bowie's number!"]])
    cools.append([consts(Expr.evalf(sympify("(1+sqrt(5))/2")), "(1+sqrt(5))/2", "The Golden Ratio", "Nature"), ["AKA Phi"]])


    for cool in cools:
        if not cool[0].num:
            cool[0].num = Expr.evalf(sympify(cool[0].ref))
        
    


    return cools


deletethis = []
def generateTraits(con: consts) -> consts:
    '''
    Detects traits of a const, creates trait objects, then adds + commits them to the db instance.
    Makes minor changes to const attributes, such as setting possible ints to ints.

    con: consts object in question
    
    Returns the same consts object. Be sure to db.session.commit() after running this function!
    '''

    if con.num.is_integer():
        db.session.add(traits(con._id, "Integer"))
        deletethis.append(con.num)

    '''
            db.session.add(inst)
            db.session.commit()
            db.session.add(solves(inst._id, inst.ref))

            # _id is only included in a consts instance after it's added to the DB, so we have to commit first.

            for tag in tags:
                db.session.add(traits(inst._id, tag))
    '''
    return con

def applyTable():
    '''
    Generate values for the table, writes em' to the DB, prints 'em all out. 
    DOES NOT CHECK IF TABLE IS FULL ALREADY! Don't run this function if your table is already populated.
    No args needed B)
    '''

    boringvals = generateBoringTable()


    for i in boringvals:
        b = consts(num=i[0], ref=i[1], name=PREGEN_CONST_NAME, creator=PREGEN_CONST_CREATOR, notes=PREGEN_CONST_NOTES) 
        db.session.add(b)
        #print(f'{i[1]} = {i[0]}')

    db.session.commit()
    
    ########################################################################
    # Condense the database, removing identical numbers and appending      #
    # them to each other until we end up with just one object per constant.#
    ########################################################################

    previous = consts.query.order_by(consts.num.asc()).first()
    numberpile = consts.query.order_by(consts.num).all()

    for inst in numberpile:
    
        # numberpile is an ordered list, making this smoother

        if inst.num == previous.num:
            db.session.add(solves(previous._id, inst.ref))
            db.session.delete(inst)
            print(f"Condatenated {inst.num} to {previous.num}.")
        else:
            db.session.add(solves(inst._id, inst.ref))
            previous = inst
            print(f"Added {inst.num} to the session.")



    # add in the consts, add in the traits
    # attach the traits to the constants
    # if a cool-constant already exists, append traits to existing constant rather than new copy.
    constsandtags = generateCoolTable()

    for inst, tags in constsandtags:
        existingcopy = consts.query.filter_by(num = inst.num).first()
        if existingcopy:
            db.session.add(solves(existingcopy._id, inst.ref))

            for tag in tags:
                print(tag)
                db.session.add(traits(existingcopy._id, tag))

        else:
            db.session.add(inst)
            db.session.commit()
            db.session.add(solves(inst._id, inst.ref))

            # _id is only included in a consts instance after it's added to the DB, so we have to commit first.

            for tag in tags:
                db.session.add(traits(inst._id, tag))


    db.session.commit()

    for i in consts.query.all():
        generateTraits(i)
        print(f"traiting {i}")
    
    ########################################################################
    return print(deletethis)




if __name__ == "__main__":
    if not does_table_exists(): # does the data inside the table exist? if not, make it
        applyTable()
    print("Table generated!")
    print("Now, try running app.py!")