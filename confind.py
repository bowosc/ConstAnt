from flask_sqlalchemy import SQLAlchemy, session
import math, re
from datetime import datetime
from sqlalchemy import func, DateTime, delete
from rpn import rpn

db = SQLAlchemy()

phi = (1 + 5 ** 0.5) / 2 # golden ratio
sqrttwo = math.sqrt(2)
sqrtthree = math.sqrt(3)

def shortenNum(num: float) -> str:
    '''
    Shortens a const value down to a 13-character alternative.
    '''
    num = str(num)
    if "e" in num:
        parts = num.split("e")
        correctlen = 13 - len(parts[1])
        return parts[0][:correctlen] + "e" + parts[1] # janky but functional :)
    else:
        return num[:13]
    

class consts(db.Model):
    _id = db.Column(db.Integer, primary_key=True)
    num = db.Column(db.Float)
    shortnum = db.Column(db.String) # for display purposes only :)
    ref = db.Column(db.String(255))
    name = db.Column(db.String(255))
    creator = db.Column(db.Integer)
    notes = db.Column(db.Text)
    date = db.Column(DateTime, default=datetime.now())

    votes = db.relationship('constvotes', backref='post', lazy='dynamic')
    
    def __init__(self, num, ref, name, creator, notes):
        self.num = num
        self.shortnum = shortenNum(num)
        self.ref = ref
        self.name = name
        self.creator = creator
        self.notes = notes
        # no datetime definition needed 

class solves(db.Model):
    _id = db.Column(db.Integer, primary_key=True)
    fid = db.Column(db.Integer) # id of const its attached to
    sol = db.Column(db.String(255)) # equation
    date = db.Column(DateTime, default=datetime.now())

    def __init__(self, fid, sol):
        self.fid = fid
        self.sol = sol
        # no datetime def needed B)

class constvotes(db.Model):
    _id = db.Column(db.Integer, primary_key=True)
    userid = db.Column('userid', db.Integer, db.ForeignKey('users._id'))
    constid = db.Column('constid', db.Integer, db.ForeignKey('consts._id'))
    upvote = db.Column(db.Boolean)
    super = db.Column(db.Boolean)

    def __init__(self, userid, constid):
        self.userid = userid
        self.constid = constid
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
        'constvotes',
        foreign_keys='constvotes.userid', 
        backref='users', 
        lazy='dynamic'
        )

    # currently only set up for consts, but named more ambiguously so that it could be expanded later
    def upvote_post(self, const):
        if not self.has_upvoted_post(const):
            upvote = constvotes(userid=self._id, constid=const._id)
            db.session.add(upvote)

    def downvote_post(self, const):
        if self.has_upvoted_post(const):
            constvotes.query.filter_by(userid=self._id, constid=const._id).delete()

    def has_upvoted_post(self, const):
        return constvotes.query.filter(constvotes.userid == self._id, constvotes.constid == const._id).count() > 0
    
    def __init__(self, name, pw, email):
        self.name = name
        self.pw = pw
        self.email = email
        self.notes = "I'm new here!"
        self.isadmin = False
        self.isbanned = False
        self.isverified = False


def voteaction(constid: int, action: str, userid: int) -> int:
    '''
    Runs when a user clicks the "vote" button on a const. 
    Basically just a toggle switch for this user's vote on this const.

    constid: id of the const in question.
    userid: id of the user in question.
    action: 'toggle', 'like' or 'unlike'. Pretty much only toggle should be used, like and unlike exist only for testing right now.

    Returns the amount of votes on the const.
    '''

    const = consts.query.filter_by(_id=constid).first_or_404() # special tech B)
    usr = users.query.filter_by(_id=userid).first()

    if action == 'toggle':
        if usr.has_upvoted_post(const):
            usr.downvote_post(const)
        else:
            usr.upvote_post(const)
    elif action == 'like':
        usr.upvote_post(const)
    elif action == 'unlike':
        usr.downvote_post(const)

    if action:
        db.session.commit()
    return const.votes.count()

def new_user(thename: str, thepw: str, theemail: str) -> users:
    '''
    NOTE: DOES NOT SANITIZE DATA INPUT!

    Adds a user to the database. 

    thename: the name :)
    thepw: the password :) NOTE: This needs to be encrypted. It currently isn't. It's on my TODO list.
    theemail: the email :)

    Returns the user object.
    '''

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

def verify_login(thename: str, thepw: str) -> users | str: # this seems too simple 
    '''
    Verify the username & password of a user.

    thename: Username
    thepw: Password

    Returns either user object or user error string, depending on if user/pass was correct or not.
    '''
    eu = users.query.filter_by(name = thename).first()
    if eu:
        if thepw != eu.pw:
            return 'Incorrect username or password!'
        print("logged in user " + eu.name)
        return eu
    else:
        return 'Incorrect username or password!'

def is_email_valid(email: str) -> bool:
    '''
    Uses a nice little regex pile to quickly check if an email seems email-ish. 
    This is fine for now, but far from comprehensive. 
    In a later version I'll use SMTP to verify email with a code instead.

    email: Email to verify.
    
    returns True if email seems legit and False if not.
    '''
    regex = r'^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w+$'
    if len(email) > 128:
        return False
    if re.match(regex, email):
        return True
    else:
        return False

def add_user_const(userid:int, constname:str, expression:str = 0, notes:str = None) -> float | str:
    '''
    Adds a user const to the database. Checks if it already exists, too.

    userid: id of the user adding the const
    constname: name of the const
    expression: expression that computes the const
    notes: notes for the const

    Note that the returned value will be either a string (error msg) for user error or a float (the const) for a success.
    '''

    n = consts.query.filter_by(name=constname).first() 
    l = consts.query.filter_by(ref=expression).first()
    if n:
        return "A constant with this name already exists!"
    elif l:
        return "A constant with this expression already exists!"
    
    value = rpn.calculateInfix(expression)
    if isinstance(value, str): # if rpn returned a string, aka if its an error msg
        print("RPN error!")
        return value
    else:
        m = consts.query.filter_by(num=value).first()
        
        if m:
            if not solves.query.filter_by(sol=expression).first():
                newsol = solves(m._id, expression)
                db.session.add(newsol)
                bestoption = solves.query.filter_by(sol=expression).order_by(func.length(solves.sol)).first() # shortest expression to find the constant
                m.ref = bestoption.sol
                db.session.commit()
            return "This constant has already been defined, but we added your definition to the list!"
        
        else:
            theuser = users.query.filter_by(_id = userid).first()
            b = consts(value, expression, constname, theuser.name, notes)
            db.session.add(b)
            bingus = consts.query.filter_by(num = value).first()
            s = solves(bingus._id, bingus.ref)
            db.session.add(s)

            db.session.commit()
            print(f"{s.fid} {s.sol}")
            print(f"Added constant {b.name}: {b.ref} = {b.num}. Added by user {b.creator}. Notes: {b.notes}")
    print("we got there appt")
    return b.num

def generate_table() -> list[list[float, str]]: 
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

def does_table_exists():
    '''
    Returns True if consts table exists.
    Returns false if consts table doesn't exist or is empty.
    '''
    if consts.query.order_by(consts.ref).limit(25).count() > 20: # check if there's anything in the db
        return True
    else:
        return False

def solfind(whatid:int) -> list[solves]:
    '''
    Returns a list of expressions that result in the value of the const.

    whatid: Id of const in question
    
    '''
    results = solves.query.filter_by(fid = whatid).order_by(func.length(solves.sol)).all()
    return results

# the big one
def confind(whatnum:float = False, whatref:str = False, whatname:str = False, whatcreator:str = False, whatid:int = False) -> list[consts]:
    '''
    Returns a list of results matching the query entered, searching the consts table.
    As of now, confind() should only be used with one search argument at a time.

    whatnum: Value of the const
    whatref: Expression that results in the const's value (just use a calculator bro)
    whatname: Name of the const searched
    whatcreator: Creator of the const searched
    whatid: Id of the const searched

    '''

    lim = 50 # we check the first 50 results in the DB. 
    # This should be expanded to a page-by-page system where the user can grab the next fifty more easily.
    results = None

    if whatref:
        results = consts.query.filter(consts.ref.contains(whatref)).order_by(consts.creator).limit(lim).all()
    elif whatname:
        results = consts.query.filter(consts.name.contains(whatname)).order_by(consts.creator).limit(lim).all()
    elif whatcreator:
        results = consts.query.filter(consts.creator.contains(whatcreator)).order_by(consts.creator).limit(lim).all()
    elif whatnum:
        results = consts.query.filter(consts.num.startswith(whatnum)).order_by(consts.num).limit(lim).all() # this is the one used most 
    elif whatid:
        results = consts.query.filter_by(_id = whatid).first()
    else:
        return 'No arguments parsed.'

    if not results:
        return 'No results for query.'
    
    
    return results

def find_user(userid: int) -> users:
    '''
    Three guesses what this does.

    userid: Id of user.

    Returns the user object of the user found, or None if no user found.
    '''
    user = users.query.filter_by(_id = userid).first()
    if user == None:
        return None
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
    Generate values for the table, prints 'em all out. 
    DOES NOT CHECK IF TABLE IS FULL ALREADY! Don't run this function if your table is already populated.
    No args needed B)

    NOTE: currently full of print() functions for debugging purposes. 
    I kept removing them and adding them back in and figured it's just easier to keep them in here.
    '''
    newtable = True
    if newtable:
        vals = generate_table()
        for i in vals:
            b = consts(i[0], i[1], "Site-Generated Constant", "Bowie", "Generated by site") 
            db.session.add(b)
            print(f'{i[1]} = {i[0]}')
        db.session.commit()

    active = consts.query.order_by(consts.num.asc()).first()
    tb = consts.query.order_by(consts.num).all()
    graveyard = [] # where constants go to die
    deletethiscounter = []

    for i in tb:
        if i.num != active.num:
            # this constant doesn't exist yet, so we're gonna set it up

            active = i 

            try: 
                k = float(active.ref) # is active.ref a float
            except:
                # wheee its a string
                b = solves(active._id, active.ref)
                print("we cook")
            else:
                # its a float so we just ignore it
                pass

        else:
            # this constant already exists, so we're just gonna add this solution as a solves to the existing constant
            
            try: 
                k = float(active.ref) # is active.ref a float
            except:
                # wheee its a string
                b = solves(active._id, i.ref)
            else:
                # its a float so we just ignore it
                deletethiscounter.append(active.ref)


            # the generating function actually just makes const objects so we have to go back and delete them later, so we label them here
            i.ref = "KILLME"
            graveyard.append(i._id)
            print("we work ")

        db.session.add(b)
    db.session.commit()
    consts.query.filter_by(ref = "KILLME").delete()


    print("we COOK")
    print(deletethiscounter)
    db.session.commit()
        
    return



if __name__ == "__main__":
    # do nothin
    print("Try running main.py!")