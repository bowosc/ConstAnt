from flask import Flask
from flask import render_template, redirect, request, url_for, flash
import confind


'''
TODO
social medialization
- login/account creation should probably be a seperate library at this point but idk
expand DB to third level ops
generation function should actually work
search feature allows for containment or starting with 

'''
app = Flask(__name__)
app.secret_key = "password"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.sqlite3'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False


@app.route("/", methods=['POST', 'GET'])
def homepage():
    query = None
    if request.method == 'POST':
        if request.form['searchbar'] != None:
            results = confind.confind(request.form['searchbar'], False)
            query = request.form['searchbar']
    else:
        results = ['Search for a number up there ^^^']
    return render_template('home.html', results=results, query=query)

if __name__ == "__main__":
    with app.app_context():
        confind.db.init_app(app)
        confind.db.create_all() # set up the stuff
        confind.does_table_exists() # does the data inside the table exist? if not, make it
        confind.db.session.commit # lock in

    app.run(debug=True, host= '0.0.0.0')