from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()

class figs(db.Model):
    _id = db.Column("id", db.Integer, primary_key=True)
    num = db.Column(db.Float)
    ref = db.Column(db.String(15))

    def __init__(self, num, ref):
        self.num = num
        self.ref = ref

def confind(whatnum:int = None, whatref:str = None) -> list[list[int, float, str]]:
    '''
    Returns a list of results matching the query entered. 

    confind() should only be used with one argument at a time, the other argument should be type None.
    ex: findmynumber = confind(6.28, None)
    ex: findmyref = confind(None, 'pi*2')
    '''
    if whatref:
        results = figs.Query.order_by(num = whatnum).all()
    elif whatnum:
        results = figs.Query.order_by(ref = whatref).all()
    return results

def generate_table():
    constants = []
    operations = []
    return