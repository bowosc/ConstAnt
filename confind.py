from flask_sqlalchemy import SQLAlchemy, session
import math, re
from datetime import datetime
from sqlalchemy import func, DateTime, delete
from rpn import rpn

db = SQLAlchemy()

phi = (1 + 5 ** 0.5) / 2 # golden ratio
sqrttwo = math.sqrt(2)
sqrtthree = math.sqrt(3)


class figs(db.Model):
    _id = db.Column(db.Integer, primary_key=True)
    num = db.Column(db.Float)
    ref = db.Column(db.String(255))
    name = db.Column(db.String(255))
    creator = db.Column(db.Integer)
    notes = db.Column(db.Text)
    date = db.Column(DateTime, default=datetime.now())

    votes = db.relationship('figvotes', backref='post', lazy='dynamic')
    
    def __init__(self, num, ref, name, creator, notes):
        self.num = num
        self.ref = ref
        self.name = name
        self.creator = creator
        self.notes = notes
        # no datetime definition needed 

class solves(db.Model):
    _id = db.Column(db.Integer, primary_key=True)
    fid = db.Column(db.Integer) # id of figure its attached to
    sol = db.Column(db.String(255)) # equation
    date = db.Column(DateTime, default=datetime.now())

    def __init__(self, fid, sol):
        self.fid = fid
        self.sol = sol
        # no datetime def needed B)

class figvotes(db.Model):
    _id = db.Column(db.Integer, primary_key=True)
    userid = db.Column('userid', db.Integer, db.ForeignKey('users._id'))
    figid = db.Column('figid', db.Integer, db.ForeignKey('figs._id'))
    upvote = db.Column(db.Boolean)
    super = db.Column(db.Boolean)

    def __init__(self, userid, figid):
        self.userid = userid
        self.figid = figid
        self.upvote = None #[NOTE: DEPRECIATED] false if downvote, true if upvote. 
        self.super = False # unused rn

class users(db.Model):
    _id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    pw = db.Column(db.String(255))
    email = db.Column(db.String(255))
    notes = db.Column(db.Text)
    isadmin = db.Column(db.Boolean())
    isbanned = db.Column(db.Boolean())
    isverified = db.Column(db.Boolean())
    creationdate = db.Column(DateTime, default=datetime.now())

    voted = db.relationship(
        'figvotes',
        foreign_keys='figvotes.userid', 
        backref='users', 
        lazy='dynamic'
        )

    # currently only set up for figs, but named more ambiguously so that it could be expanded later
    def upvote_post(self, fig):
        if not self.has_upvoted_post(fig):
            upvote = figvotes(userid=self._id, figid=fig._id)
            db.session.add(upvote)

    def downvote_post(self, fig):
        if self.has_upvoted_post(fig):
            figvotes.query.filter_by(userid=self._id, figid=fig._id).delete()

    def has_upvoted_post(self, fig):
        return figvotes.query.filter(figvotes.userid == self._id, figvotes.figid == fig._id).count() > 0
    
    def __init__(self, name, pw, email):
        self.name = name
        self.pw = pw
        self.email = email
        self.notes = "I'm new here!"
        self.isadmin = False
        self.isbanned = False
        self.isverified = False


def voteaction(figid, action, userid):
    fig = figs.query.filter_by(_id=figid).first_or_404() # special tech B)
    usr = users.query.filter_by(_id=userid).first()

    if action == 'toggle':
        if usr.has_upvoted_post(fig):
            usr.downvote_post(fig)
        else:
            usr.upvote_post(fig)
    elif action == 'like':
        usr.upvote_post(fig)
    elif action == 'unlike':
        usr.downvote_post(fig)

    if action:
        db.session.commit()
    return fig.votes.count()

def new_user(thename, thepw, theemail):
    '''user.password = bcrypt.hashpw(str.encode(newpass), bcrypt.gensalt())
    if bcrypt.checkpw(str.encode(foundpass), founduser.password):'''

    if is_email_valid(theemail) != True:
        return "Invalid email address!"
    
    if len(thename) > 24:
        return "Your username cannot be longer than 24 characters."

    if len(thepw) > 24:
        return "Your password cannot be longer than 24 characters."
    
    em = users.query.filter_by(email=theemail).first()
    if em:
        return "You already have an account, please sign in!"
    
    nm = users.query.filter_by(name=thename).first()
    if nm:
        return "This username is taken. Please choose a different one."
    
    wowie = users(thename, thepw, theemail)
    db.session.add(wowie)
    db.session.commit()
    print("registered user " + wowie.name)
    return wowie

def verify_login(thename, thepw): # this seems too simple 
    eu = users.query.filter_by(name = thename).first()
    if eu:
        if thepw != eu.pw:
            return 'Incorrect username or password!'
        print("logged in user " + eu.name)
        return eu
    else:
        return 'Incorrect username or password!'

def is_email_valid(email):
    regex = r'^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w+$'
    if len(email) > 128:
        return False
    if re.match(regex, email):
        return True
    else:
        return False

def add_user_const(userid:int = None, constname:str = None, equation:str = 0, notes:str = None):
    '''
    Note that the returned value will always be either a string for an error message or a float for a success.
    '''

    n = figs.query.filter_by(name=constname).first() 
    l = figs.query.filter_by(ref=equation).first()
    if n:
        return "A constant with this name already exists!"
    elif l:
        return "A constant with this equation already exists!"
    
    value = rpn.calculateInfix(equation)
    if isinstance(value, str): # if its an error msg
        return value
    else:
        m = figs.query.filter_by(num=value).first()
        
        if m:
            ''' the world not ready for this yet
            if not solves.query.filter_by(sol=equation).first():
                newsol = solves(m._id, equation)
                db.session.add(newsol)
                '''
            return "This constant has already been defined, but we added your definition to the list!"
        
        else:
            b = figs(value, equation, constname, userid, notes)
            db.session.add(b)
            bingus = figs.query.filter_by(num=value).first()
            s = solves(bingus._id, bingus.ref)
            db.session.add(s)

            db.session.commit()
            print(f"{s.fid} {s.sol}")
            print(f"Added constant {b.name}: {b.ref} = {b.num}. Added by user {b.creator}. Notes: {b.notes}")
    return b.num

def generate_table(): 
    '''
    generate a mf table
    '''
    constants = ["pi", "e", "sqrt(2)", "sqrt(3)", "phi", "(1/2)", "(1/3)", "(1/4)", "(1/5)", "(1/6)", 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12] 

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

def solfind(whatid:int) -> list[solves]:
    '''
    Gets a list of equations for a given number.
    '''
    results = solves.query.filter_by(fid = whatid).all()
    return results

# the big one
def confind(whatnum:float = False, whatref:str = False, whatname:str = False, whatcreator:str = False, whatid:int = False) -> list[list[int, float, str]]:
    '''
    Returns a list of results matching the query entered, searching the figs table.

    confind() should only be used with one argument at a time, the other arguments should be False or not used.
    ex: findmynumber = confind(6.28, False, False, False)
    ex: findmyref = confind(False, 'pi*2')
    '''
    lim = 50 # we check the first 50 results in the DB :)
    results = None

    if whatref:
        results = figs.query.filter(figs.ref.contains(whatref)).order_by(figs.creator).limit(lim).all()
    elif whatname:
        results = figs.query.filter(figs.name.contains(whatname)).order_by(figs.creator).limit(lim).all()
    elif whatcreator:
        results = figs.query.filter(figs.creator.contains(whatcreator)).order_by(figs.creator).limit(lim).all()
    elif whatnum:
        results = figs.query.filter(figs.num.startswith(whatnum)).order_by(figs.creator).limit(lim).all()
    elif whatid:
        results = figs.query.filter_by(_id = whatid).first()
    else:
        return 'No arguments parsed.'

    if not results:
        return 'No results for query.'
    
    
    return results


def find_user(userid: int) -> users:
    '''
    Guess
    '''
    user = users.query.filter_by(_id = userid).first()
    if user == None:
        return "USER NOT FOUND"
    return user

def init_default_user():
    '''
    Adds "default" user, for testing.
    Username: "user"
    Password: "pass"
    Email: "bowman@edebohls.com"
    
    Also adds Null user.
    Username: "User not found."
    Password: "Password not found. Or user."
    Email: "Email not found. Or user."
    '''
    usr = users('user', 'pass', 'bowman@edebohls.com')
    nullusr = users("User not found.", "Password not found. Or user.", "Email not found. Or user.")

    db.session.add(nullusr)
    db.session.add(usr)
    
    db.session.commit()
    return

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
            b = figs(i[0], i[1], "Site-Generated Constant", "Bowie", "Generated by site") # ADDING FIGS TO DB !!!
            db.session.add(b)
            print(f'{i[1]} = {i[0]}')
        db.session.commit()

    active = figs.query.order_by(figs.num.asc()).first()
    tb = figs.query.order_by(figs.num).all()
    executionblock = []
    for i in tb:
        if i.num != active.num:
            active = i
            b = solves(active._id, active.ref)
            print("we cook")
        else:
            b = solves(active._id, i.ref)
            i.ref = "KILLME"
            executionblock.append(i._id)
            print("we work")
        db.session.add(b)
    db.session.commit()
    figs.query.filter_by(ref = "KILLME").delete()


    print("we COOK")
    db.session.commit()
        
    return



'''
# deprecated i think
def add_fig_vote(username: str, figid: int, like: bool):

    Add vote entry to db, connecting user and post _ids.
    Like bool represents wether the post is liked or disliked.
    add_fig_vote will return an error message string if there's an error, and 
    otherwise will return False.


    usr = users.query.filter_by(name = username).first()
    if not usr:
        return "SessionData error. User not found!"
    
    fig = figs.query.filter_by(_id = figid).first()
    if not fig:
        return "ID error. Constant not found!"
    
    existinglike = votes.query.filter_by(userid = usr._id, figid = fig._id).first()
    if existinglike:
        if existinglike.upvote != like: # if the users vote has changed
            if existinglike.upvote: # if the user liked but now dislikes
                existinglike.upvote = False
            else: # if the user disliked but now likes
                existinglike.upvote = True
        else:
            return "Bro already voted"


    if not like:
        fig.votes -= 1
    else:
        fig.votes += 1
    
    newlike = votes(usr._id, fig._id, like)
    db.session.add(newlike)

    db.session.commit()
    
    return False

'''

if __name__ == "__main__":
    # do nothin
    print("try running main.py bro")