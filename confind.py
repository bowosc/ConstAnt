from flask_sqlalchemy import SQLAlchemy, session
import math

db = SQLAlchemy()

phi = (1 + 5 ** 0.5) / 2 # golden ratio
sqrttwo = math.sqrt(2)
sqrtthree = math.sqrt(3)

class figs(db.Model):
    _id = db.Column("id", db.Integer, primary_key=True)
    num = db.Column(db.Float)
    ref = db.Column(db.String(15))

    def __init__(self, num, ref):
        self.num = num
        self.ref = ref

def generate_table(): 
    
    constants = ["pi", "e", "sqrttwo", "sqrtthree", "phi", -6, -5, -4, -3, -2, -1, "1/2", "1/3", "1/4", "1/5", "1/6", 1, 2, 3, 4, 5, 6] 
    
    l = []

    for c in constants: # apply unary operations
        l.extend(diversify(c))
    
    al = [] # altlist, so we don't screw up the for loop
    for i in l: # for item in that one list, apply binary operations
        for j in l:
            print(f"{i}, {j}")
            al.append([i[0] * j[0], f'{i[1]} * {j[1]}'])
            al.append([i[0] + j[0], f'{i[1]} + {j[1]}'])
            al.append([i[0] - j[0], f'{i[1]} - {j[1]}'])
            if j[0] != 0:
                al.append([i[0] / j[0], f'{i[1]} / {j[1]}'])
            if i[0] > 0:
                try:
                    al.append([math.pow(i[0], j[0]), f'{i[1]} ^ {j[1]}'])
                except OverflowError:
                    print("too big lol")
    
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
        case "sqrttwo":
            c = sqrttwo
        case "sqrtthree":
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
    
    if isinstance(c, int) and c > 0:
        al.append([math.factorial(c), f'{d}!'])

    '''for p in pows:
        l.append([math.pow(c, p), f'{c}^{p}'])'''

    return al

def confind(whatnum:float = False, whatref:str = False) -> list[list[int, float, str]]:
    '''
    Returns a list of results matching the query entered. 

    confind() should only be used with one argument at a time, the other argument should be False.
    ex: findmynumber = confind(6.28, None)
    ex: findmyref = confind(None, 'pi*2')
    '''
    if whatref:
        results = figs.query.filter_by(num=whatnum).all()
    elif whatnum:
        results = figs.query.filter_by(ref=whatref).all()
    else:
        results = ['bingus']
    return results

def inittable():
    newtable = True
    if newtable:
        vals = generate_table()
        for i in vals:
            b = figs(i[0], i[1])
            db.session.add(b)
            print(f'{i[1]} = {i[0]}')
        db.session.commit
    return

if __name__ == "__main__":
    '''print(figs.query().first)
    print("---")
    if figs.query().first():
        print("<confind> Table [figs] is not empty. Please empty [figs] table to generate new table.")
    else:'''
    newtable = False
    if newtable:
        vals = generate_table()
        for i in vals:
            b = figs(i[0], i[1])
            db.session.add(b)
            print(f'{i[1]} = {i[0]}')
        db.session.commit