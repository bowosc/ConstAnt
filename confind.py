from flask_sqlalchemy import SQLAlchemy, session
import math
from sqlalchemy import func
from rpn import rpn

db = SQLAlchemy()

phi = (1 + 5 ** 0.5) / 2 # golden ratio
sqrttwo = math.sqrt(2)
sqrtthree = math.sqrt(3)

class figs(db.Model):
    _id = db.Column("id", db.Integer, primary_key=True)
    num = db.Column(db.Float)
    ref = db.Column(db.String(255))
    name = db.Column(db.String(255))
    creator = db.Column(db.String(255))
    notes = db.Column(db.String(255))
    
    def __init__(self, num, ref, name, creator, notes):
        self.num = num
        self.ref = ref
        self.name = name
        self.creator = creator
        self.notes = notes

def add_user_const(username, constname, equation, notes):
    #calulate value from equation
    value = rpn.calculateInfix(equation)
    if isinstance(value, str): # if its an error msg
        print("we got a string here")
        print(value)
        return value
    else:
        b = figs(value, equation, constname, username, notes)
        db.session.add(b)
        db.session.commit()
        print(f"Added constant {b.name}: {b.ref} = {b.num}. Added by user {b.creator}. Notes: {b.notes}")
    return b.num




def generate_table(): 
    '''
    generate a mf table
    '''
    constants = ["pi", "e", "sqrt(2)", "sqrt(3)", "phi", "1/2", "1/3", "1/4", "1/5", "1/6", 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12] 

    l = []
    for c in constants: # apply unary operations
        l.extend(diversify(c))
        print(f"diversified {c}")
    
    l = binary_operations(l)
    return l
    
def binary_operations(l):
    al = [] # altlist, so we don't screw up the for loop
    for i in l: # for item in that one list, apply binary operations
        for j in l:
                #unreadable lol there's stuff here designed to stop random duplicates from appearing
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

def diversify(d) -> list[list[float, str]]: # c for constant and constant is for me
    '''
    Returns a list of lists of c with unary operations applied.
    Sublist format: [sin(c), 'sin({c})']
    '''
    al = []
    c = d
    match d:
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
        case "1/2":
            c = 1/2
        case "1/3":
            c = 1/3
        case "1/4":
            c = 1/4
        case "1/5":
            c = 1/5
        case "1/6":
            c = 1/6

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

def does_table_exists():
     if figs.query.order_by(figs.ref).limit(25).count() < 20: # check if there's anything in the db
        inittable()

def search_by_name():
    results = figs.query.order_by(figs._id.desc()).limit(50).all() # main search is currently directed towards this funciton rather than confind
    return results

def confind(whatnum:float = False, whatref:str = False) -> list[list[int, float, str]]:
    '''
    Returns a list of results matching the query entered. 

    confind() should only be used with one argument at a time, the other argument should be False.
    ex: findmynumber = confind(6.28, None)
    ex: findmyref = confind(None, 'pi*2')
    '''
    if whatref:
        results = figs.query.filter_by(ref=whatref).all().limit(50)
    elif whatnum:
        results = figs.query.filter(figs.num.startswith(whatnum)).order_by(figs.num).limit(50).all()

        if not results:
            results = ['no rezzies']
    else:
        results = ['ERROR: No arguments parsed? Like why?']
    
    return results

def inittable():
    '''
    Generate values for the table, print em all out. 
    DOES NOT CHECK IF TABLE IS FULL ALREADY! Don't run this function if your table is already populated.
    No args needed B)
    '''
    newtable = True
    if newtable:
        vals = generate_table()
        for i in vals:
            b = figs(i[0], i[1], None, "Bowie", "Generated by site")
            db.session.add(b)
            print(f'{i[1]} = {i[0]}')
        db.session.commit()
    return

if __name__ == "__main__":
    # do nothin
    print("try running main bro")