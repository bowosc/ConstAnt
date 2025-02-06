import confind 
from sympy import Expr, sympify
import re

DISALLOWEDWORDS = ["butthead"]

def isProfane(text: str) -> bool:
    '''
    [Note: Should be expanded.]

    Checks if a given string contains any disallowed phrases/words.
    
    text: the text in question.

    Returns False is no phrases are found, and returns the phrase if one is found.
    '''


    text = re.sub(r'[^A-Za-z]+', '', text) # keep only english letters

    for word in DISALLOWEDWORDS:
        if word in text.lower():
            return word
        
    return False

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
    elif re.match(regex, email):
        return True
    else:
        return False

def problemsWithNewConst(userid:int, constname:str, expression:str, isLatex: bool, notes:str) -> bool | str:
    '''
    Check that all the fields of a new constant addition are a-ok before putting it in the database.
    
    userid: ID of the user submitting the constant.
    constname: Name of the new constant.
    expression: The expression that evaluates to the new constant.
    isLaTeX: if the above expression is in LaTeX format. Hopefully it isn't, because ConstAnt can't handle LaTeX.
    notes: Notes on the new constant.

    Returns False if the constant is OK, and returns an error message if there's something wrong.
    '''

    # These don't really need to be elif, but since the previous always returns, it doesn't really matter. I like how it looks with elif rather than a bunch of ifs.
    if not (userid and constname and expression and notes):
        return "Please fill in all fields!"
    elif isProfane(constname):
        return "Nice try, but try and use nicer language in your constant's name."
    elif isProfane(notes):
        return "Nice try, but try and use nicer language in your notes."
    
    try: 
        expressionResult = Expr.evalf(sympify(expression)) # foreshadowing
    except:
        return "I can't evaluate this expression!"
    
    try:
        float(expressionResult) # elegant?
    except:
        return "This expression doesn't evaluate to a number!"



    if confind.consts.query.filter_by(name=constname).first():
        return "A constant with this name already exists!"
    elif confind.consts.query.filter_by(ref=expression).first():
        return "This constant has already been defined!"
    

    preexistingConst = confind.consts.query.filter_by(num=expressionResult).first()
    if preexistingConst:
        if not confind.solves.query.filter_by(sol=expression).first():
                # if this solution isn't already on the existing constant, add it.
                
                newsol = confind.solves(preexistingConst._id, expression)
                confind.db.session.add(newsol)

                confind.db.session.commit()

        return "This constant has already been defined, but we added your definition to the list!"
   

    return False

def problemsWithNewUser(username: str, useremail: str, userpass: str) -> bool | str:
    '''
    [Note: should be expanded.]

    Check that all the fields of a new user are a-ok before putting it in the database.
    
    username: New user's name.
    useremail: New user's email.
    userpass: New user's password, unhashed.

    Returns False if the user is OK, and returns an error message if there's something wrong.
    '''
    passwordOK = r'^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!%*#?&]{8,}$'


    if is_email_valid(useremail) != True:
        return "Invalid email address!"
    elif isProfane(username):
        return "Nice try, but try and use nicer language in your username."
    elif len(username) > 24:
        return "Your username cannot be longer than 24 characters."
    elif len(userpass) > 36:
        return "Your password cannot be longer than 24 characters."
    elif not re.match(passwordOK, userpass):
        return "Your password should include a minimum of eight characters, and least one letter, number, and special character."
    
    em = confind.users.query.filter_by(email=useremail).first()
    if em:
        return "You already have an account, please sign in!"
    
    nm = confind.users.query.filter_by(name=username).first()
    if nm:
        return "This username is taken. Please choose a different one."
    
    return False



if __name__ == "__main__":
    isProfane("")