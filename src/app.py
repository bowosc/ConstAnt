from flask import Flask
from flask import render_template, redirect, request, url_for, flash, session

import confind, input, carpentry
from confind import app

'''
TODO
MVP

Graphic Design :P


better input monitoring, check:
- curses/slurs


NONMVP

DB adds idea: set base dataset in a txt file or something, users can add whole datasets if in right format (json?).

Constant of the day, always a user-entered constant

Accept LaTeX

different search methods
    - consider decimal?
    - only integers?
    - size radius?

Highlight specific types of number
    - popular constants
        - e, pi, phi, euler's whatever
    - primes
    - integers
    - rational
    - irrational
    - "stupid numbers"

Add option to include new const definition on viewconst page


LARGE SUBPROJECTS

number line viewer

social medialization
    order numbers by likes
    comments
    account viewing page

'''



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
    '''
    if 'user' in session:
        session.pop("user")
        flash("You have been logged out. Come back soon!", 'success')
    else:
        flash("You aren't logged in!", "usererror")
    return redirect(request.referrer)

@app.route("/about")
def about():
    return render_template('about.html')

@app.route("/", methods=['POST', 'GET'])
def home():
    query = None
    hotconsts = confind.hotconsts(3)
    topconsts = confind.hotconsts(12)
    
    if request.method == 'POST':
        query = request.form['searchbar']
        if len(query) > 1:
            if query[0] == ".":
                query = f"0{query}" # .42 becomes 0.42
            while query[0] == '0' and query[1] != ".":
                query = query[1:] # no reason to search 000001 but this makes the search work better when you do
        
        if query != None and query != "":

            results = confind.confind(whatnum = query, onlyInts=False)
            if isinstance(results, str): # if confind finds no results
                #flash(results, 'searcherror')
                results = None
                return render_template("home.html", results=results, query=query)

            

        else:
            results = None
    else:
        results = None
    return render_template('home.html', results=results, query=query, hotconsts=hotconsts, topconsts=topconsts)

@app.route("/register", methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        if request.form['passworb'] != request.form['password']:
            flash('Passwords do not match!', 'usererror')
            return redirect(url_for('register'))
        
        error = input.problemsWithNewUser(request.form['username'], request.form['email'], request.form['password'])
        if error:
            flash(error, 'usererror')
            return redirect(url_for("home"))
        else:
            idk = confind.new_user(request.form['username'], request.form['password'], request.form['email'])

            flash(f'Account successfully created. Welcome, {idk.name}!', 'success')
            login_user(idk.name, request.form['password']) # doesn't use the password in the db, because it's hashed.
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
        return redirect(url_for('login'))
    elif request.method == 'POST':
        userid, cname, eq, notes = session["user"], request.form["constantname"], request.form["equation"], request.form["notes"]

        error = input.problemsWithNewConst(userid, cname, eq, False, notes)

        if error:
            flash(error, 'usererror')
            return redirect(url_for("newconst"))
        else:
            try:
                newconstid = confind.add_user_const(userid, cname, eq, notes)
            except:
                flash('Database error. Contact an Administrator!', 'error')
                return redirect(url_for("home"))
            flash('Constant successfully added!', 'success')
            return redirect(f"viewconst/{newconstid}") 

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
    traits = confind.traitfind(id)

    return render_template('viewconst.html', result = result, soldata = soldata, traits = traits)

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
        
        confind.db.create_all() # set up the stuff
        
        if not confind.does_table_exists(): # does the data inside the table exist? if not, make it
            carpentry.applyTable()

        confind.init_default_user() # for dev purposes, not to be used in production
        confind.db.session.commit() # lock in

    app.run(debug=True, host= '0.0.0.0', port=3000)