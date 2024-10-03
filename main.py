from flask import Flask
from flask import render_template, redirect, request, url_for, flash
import confind


'''
TODO
social medialization
- login/account creation should probably be a seperate library at this point but idk
expand DB to third level ops
idiotproofing, error msgs and whatever
equation-solver should probably be improved
number line viewer :)
'''
app = Flask(__name__)
app.secret_key = "password"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.sqlite3'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False


@app.route("/", methods=['POST', 'GET'])
def home():
    query = None
    if request.method == 'POST':
        if request.form['searchbar'] != None:
            results = confind.confind(request.form['searchbar'], False, False, False, False)
            if isinstance(results, str): # if confind returns an error msg
                flash(results)
                redirect(url_for("home"))
            query = request.form['searchbar']
    else:
        results = None
    return render_template('home.html', results=results, query=query)

@app.route("/newconst", methods=['POST', 'GET'])
def newconst():
    if request.method == 'POST':
        eq, usr, notes, cname = request.form['equation'], request.form['username'], request.form['notes'], request.form['constantname']
        if eq and usr and notes and cname:
            if isinstance(usr, str):
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
                flash('Username must contain letter characters!', 'usererror')
                return redirect(url_for("newconst"))
        else:
            flash('Please fill in all fields to submit this form.', 'usererror')
            return redirect(url_for("newconst"))
    return render_template('newconst.html')

@app.route("/viewconst/<id>", methods=['POST', 'GET'])
def viewconst(id):
    constdata = confind.confind(False, False, False, False, id)
    if not constdata:
        flash('No constant with that ID exists!', 'usererror')
        return redirect(url_for("home"))
    return render_template('viewconst.html', constdata = constdata)





if __name__ == "__main__":
    with app.app_context():
        confind.db.init_app(app)
        confind.db.create_all() # set up the stuff
        confind.does_table_exists() # does the data inside the table exist? if not, make it
        confind.db.session.commit # lock in

    app.run(debug=True, host= '0.0.0.0')