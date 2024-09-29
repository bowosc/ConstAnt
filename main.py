from flask import Flask
from flask import render_template, redirect, request, url_for, flash
import confind

app = Flask(__name__)
app.secret_key = "password"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.sqlite3'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False


@app.route("/", methods=['POST', 'GET'])
def homepage():
    if request.method == 'POST':
        if request.form['searchbar'] != None:
            results = confind.confind(request.form['searchbar'], False)
    else:
        results = ''
        confind.inittable()
        z = confind.figs.query.order_by().all()
        for i in z:
            print(i.num)
    return render_template('home.html', results=results)

if __name__ == "__main__":
    with app.app_context():
        confind.db.init_app(app)
        confind.db.create_all()
        

        '''vals = confind.generate_table()
        for i in vals:
            b = confind.figs(i[0], i[1])
            confind.db.session.add(b)
            print(f'{i[1]} = {i[0]}')
        confind.db.session.commit'''

    app.run(debug=True, host= '0.0.0.0')