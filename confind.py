import re
from datetime import datetime
from sympy import Expr, evalf, sympify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func, DateTime, delete

import carpentry, hashing # just singular py files not entire libraries

PREGEN_CONST_CREATOR = "Server"
PREGEN_CONST_NAME = "Automatically generated constant"
PREGEN_CONST_NOTES = ""

db = SQLAlchemy()

class consts(db.Model):
    '''
    Database format for constants.
    '''
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
    '''
    Database format for expressions that evaluate to a constant.
    '''
    _id = db.Column(db.Integer, primary_key=True)
    fid = db.Column(db.Integer) # id of const its attached to
    sol = db.Column(db.String(255)) # equation
    date = db.Column(DateTime, default=datetime.now())

    def __init__(self, fid, sol):
        self.fid = fid
        self.sol = sol
        # no datetime def needed B)

class constvotes(db.Model):
    '''
    Database format for votes on constants.
    '''
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
    '''
    Database format for user accounts.
    '''
    _id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    pw = db.Column(db.String(255))
    email = db.Column(db.String(255))
    notes = db.Column(db.Text)
    isadmin = db.Column(db.Boolean()) # currently unused
    isbanned = db.Column(db.Boolean()) # currently unused
    isverified = db.Column(db.Boolean()) # currently unused
    creationdate = db.Column(DateTime) # currently unused

    voted = db.relationship(
        'constvotes',
        foreign_keys='constvotes.userid', 
        backref='users', 
        lazy='dynamic'
        )

    # currently only set up for consts, but named more ambiguously so that it could be expanded later
    def upvote_post(self, const: consts) -> None:
        if not self.has_upvoted_post(const):
            upvote = constvotes(userid=self._id, constid=const._id)
            db.session.add(upvote)

    def downvote_post(self, const: consts) -> None:
        if self.has_upvoted_post(const):
            constvotes.query.filter_by(userid=self._id, constid=const._id).delete()

    def has_upvoted_post(self, const: consts) -> None:
        return constvotes.query.filter(constvotes.userid == self._id, constvotes.constid == const._id).count() > 0
    
    def __init__(self, name, pw, email):
        self.name = name
        self.pw = hashing.generateHash(pw)
        self.email = email
        self.notes = "I'm new here!"
        self.isadmin = False
        self.isbanned = False
        self.isverified = False
        self.creationdate = datetime.now()


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

def new_user(thename: str, thepw: str, theemail: str) -> users | str:
    '''
    Adds a user to the database.
    DOES NOT DO ANY KIND OF CHECKS BEFOREHAND, BE SURE TO PREP INPUT!!!

    thename: the name
    thepw: the password
    theemail: the email 

    Returns the user object on success, returns an error message string on fail.
    '''
    
    newguy = users(thename, thepw, theemail)
    db.session.add(newguy)
    db.session.commit()
    print("registered user " + newguy.name)

    return newguy

def verify_login(thename: str, thepw: str) -> users | str: # this seems too simple 
    '''
    Verify the username & password of a user.

    thename: Username
    thepw: Password

    Returns either user object or user error string, depending on if user/pass was correct or not.
    '''
    eu = users.query.filter_by(name = thename).first()
    if eu and hashing.checkHash(thepw, eu.pw):
        print("logged in user " + eu.name)
        return eu
    else:
        return 'Incorrect username or password!'

def add_user_const(userid:int, constname:str, expression:str, isLatex: bool = False, notes:str = None) -> int:
    '''
    Adds a user const to the database.
    DOES NOT DO ANY KIND OF CHECKS BEFOREHAND, BE SURE TO PREP INPUT!!!
    Probably use problemsWithNewConst() from input.py to do this. 

    userid: id of the user adding the const
    constname: name of the const
    expression: expression that computes the const
    notes: notes for the const

    Returns the ID of the constant added.
    '''

    #value = expressions.solve(expression, isLatex)
    value = Expr.evalf(sympify(expression))

    theuser = users.query.filter_by(_id = userid).first()
    b = consts(value, expression, constname, theuser.name, notes)
    db.session.add(b)
    bingus = consts.query.filter_by(num = value).first()
    s = solves(bingus._id, bingus.ref)
    db.session.add(s)

    db.session.commit()
    print(f"Added constant {b.name}: {b.ref} = {b.num}. Added by user {b.creator}. Notes: {b.notes}")
    return b._id

def inittable():
    '''
    Generate values for the table, writes em' to the DB, prints 'em all out. 
    DOES NOT CHECK IF TABLE IS FULL ALREADY! Don't run this function if your table is already populated.
    No args needed B)

    NOTE: currently full of print() functions for debugging purposes. 
    I kept removing them and adding them back in and figured it's just easier to keep them in here.
    '''
    newtable = True
    if newtable:
        vals = carpentry.generate_table()
        for i in vals:
            b = consts(num=i[0], ref=i[1], name=PREGEN_CONST_NAME, creator=PREGEN_CONST_CREATOR, notes=PREGEN_CONST_NOTES) 
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

            active = i # why?

            try: 
                k = float(active.ref) # is active.ref a float
            except:
                # wheee its a string
                b = solves(active._id, active.ref)
                #print("we cook")
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
            #print("we work ")

        db.session.add(b)
    db.session.commit()
    consts.query.filter_by(ref = "KILLME").delete()


    print("we COOK")
    print(deletethiscounter)
    db.session.commit()
        
    return

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
    
    Note: this is kinda just a one-line SQLAlchemy query shoved into a function.
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
    Username: "bob"
    Password: "bob"
    Email: "bowman@edebohls.com"
    
    Also adds Null user.
    Username: "User not found."
    Password: "Password not found. Or user."
    Email: "Email not found. Or user."
    '''
    usr = users('bob', 'bob', 'bowman@edebohls.com')
    nullusr = users("User not found.", "Password not found. Or user.", "Email not found. Or user.")

    db.session.add(nullusr)
    db.session.add(usr)
    
    db.session.commit()
    return




if __name__ == "__main__":
    # do nothin
    print("Try running main.py!")