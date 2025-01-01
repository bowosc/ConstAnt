from flask import Flask
from flask import render_template, redirect, request, url_for, flash, session
import confind
from datetime import timedelta
'''
TODO
social medialization
    order numbers by likes


database content stuff
    expand DB to third level ops


    
    switch to using sympy for math, esp trig functions :/
        related to: calculations should be more accurate; e.g. sin(pi)^sqrt(2) != 0 rn
    stop letting in solves that are just straight-up numbers.

idiotproofing
    error msgs and whatever
    prevent ppl from submitting expressions like 2+0+0+0+0 or 2+sin(pi)+sin(pi)+sin(pi)
    


UI/UX??


later:
account viewing page
number line viewer
encrypt passwords
comments
'''

app = Flask(__name__)

app.secret_key = "nicetry"

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.sqlite3'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.permanent_session_lifetime = timedelta(minutes=60)

@app.context_processor
def inject_user():
    '''
    Finds & connects user when they log in.
    '''
    if 'user' in session:
        return dict(
            user = confind.find_user(session['user'])
            )
    else:
        return dict(
            user = confind.find_user(1)
            ) # null user

@app.route("/logout")
def logout():
    '''
    Removes user from session. 
    
    Bye!
    '''
    if 'user' in session:
        session.pop("user")
        flash("Logged out. Come back soon!", 'success')
    else:
        flash("You aren't logged in!", "usererror")
    return redirect(request.referrer)

@app.route("/", methods=['POST', 'GET'])
def home():
    query = None
    if request.method == 'POST':
        if request.form['searchbar'] != None:

            results = confind.confind(whatnum = request.form['searchbar'])

            if isinstance(results, str): # if confind returns an error msg
                flash(results, 'error')
                results = None
                redirect(url_for("home"))

            query = request.form['searchbar']

        else:
            results = None
    else:
        results = None
    return render_template('home.html', results=results, query=query)

@app.route("/register", methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        if request.form['passworb'] != request.form['password']:
            flash('Passwords do not match!', 'usererror')
            return redirect(url_for('register'))
        idk = confind.new_user(request.form['username'], request.form['password'], request.form['email'])
        if isinstance(idk, str):
            flash(idk, 'usererror')
            return redirect(url_for('register'))
        else:
            flash(f'Account successfully created, {idk.name}! Welcome!')
            return redirect(url_for('home'))
    return render_template('register.html')

@app.route("/login", methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        login_user(request.form['username'], request.form['password'])
        return redirect(url_for("home"))
    return render_template('login.html')

@app.route("/newconst", methods=['POST', 'GET'])
def newconst():
    if 'user' not in session:
        flash('Please log in to submit a constant!', 'usererror')
        return redirect(request.referrer)
        

    if request.method == 'POST':
        if 'user' not in session: # the double check
            flash('Please log in to submit a constant!', 'usererror')
            return redirect(request.referrer)
        eq, usr, notes, cname = request.form['equation'], session["user"], request.form['notes'], request.form['constantname']
        if eq and usr and notes and cname:
                if isinstance(cname, str):
                    b = confind.add_user_const(usr, cname, eq, notes)
                    try:
                        a = int(b)
                    except TypeError:
                        flash(b, 'error')
                        return redirect(url_for("newconst"))
                    except ValueError:
                        flash(b, 'usererror')
                        return redirect(url_for("newconst"))

                    if isinstance(b, str):
                        flash(b, 'usererror')
                        return redirect(url_for("newconst"))
                    else:
                        flash('Constant successfully added!', 'success')
                        return redirect(url_for("home")) # should be changed to constant viewing page when that works
                else:
                    flash('Constant name must contain letter characters!', 'usererror')
                    return redirect(url_for("newconst"))
        else:
            flash('Please fill in all fields to submit this form.', 'usererror')
            return redirect(url_for("newconst"))
    return render_template('newconst.html')

@app.route("/viewconst/<int:id>", methods=['POST', 'GET'])
def viewconst(id: int):
    '''
    Redirects a user to the 'view' page for a constant.

    id: Id of the constant.
    '''
    result = confind.confind(whatid=id)
    if not result:
        flash('No constant with that ID exists!', 'usererror')
        return redirect(request.referrer)
    soldata = confind.solfind(id)
    return render_template('viewconst.html', result = result, soldata = soldata)

@app.route("/constvote/<int:constid>/<action>", methods=['POST', 'GET'])
def constvote(constid: int, action: str = 'toggle'):
    '''
    Toggles a vote to a const/const from the user in session.
    Action should be toggle unless you're testing. For development, 'like' and 'unlike' are alternatives.
    '''
    if 'user' not in session:
        flash('Please log in to vote!', 'usererror')
        return redirect(url_for("login"))

    return str(confind.voteaction(constid, action, session["user"]))


# this aint a route
def login_user(name:str, pw:str) -> bool:
    '''
    Verifies user, then adds user to session["user"].

    name: Username
    pw: Password

    If user verification is successful, login_user returns True.
    If not, login_user returns a redirect to login page.
    '''
    user = confind.verify_login(name, pw)
    if isinstance(user, str):
        flash(user, 'usererror') # returns error message as a string if somethings wrong
        return redirect(url_for('login'))
    else:
        flash("Logged in successfully.", 'success')
        session["user"] = user._id
    return True



if __name__ == "__main__":
    with app.app_context():
        confind.db.init_app(app)
        confind.db.create_all() # set up the stuff
        if not confind.does_table_exists(): # does the data inside the table exist? if not, make it
            confind.inittable()

        confind.init_default_user() # for dev purposes, not to be used in production
        confind.db.session.commit # lock in

    app.run(debug=True, host= '0.0.0.0', port=3000)