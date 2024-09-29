from flask import Flask
from flask import render_template, redirect, request, url_for, flash
import confind

app = Flask(__name__)
app.secret_key = "password"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.sqlite3'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False


@app.route("/")
def homepage():
    if request.method == 'POST':
        results = confind(request.form['searchbah'])
    else:
        results = ''
    return render_template('home.html', results=results)

if __name__ == "__main__":
    with app.app_context():
        confind.db.create_all()
    app.run(debug=True, host= '0.0.0.0')