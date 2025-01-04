import bcrypt
def generateHash(target: str) -> str:
    '''
    Uses bcrypt to generate a hash for a given string, later verifiable by bcrypt.

    '''
    bytes = target.encode('utf-8') 
  
    # lantern control
    salt = bcrypt.gensalt() 

    hash = bcrypt.hashpw(bytes, salt) 
    return hash

def checkHash(maybepass: str, hashedpass: str) -> bool:
    '''
    Verifies that a given password (or any string) is the same as a hashed password (or any other string).

    maybepass: Unhashed password to verify.
    hashedpass: Hashed password straight from the database.

    Returns True if they're equal, False if not. 
    '''

    return bcrypt.checkpw(maybepass.encode('utf-8'), hashedpass) 