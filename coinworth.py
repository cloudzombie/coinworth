import datetime
import requests
import simplejson as json
import sqlite3
import schedule
import time
from wtforms import Form, BooleanField, TextField, PasswordField, validators, FloatField, RadioField, SelectField
from flask import Flask, request, session, g, redirect, url_for, \
     abort, render_template, flash


################################################

DATABASE = '/tmp/cw.sqlite'
DEBUG = True
SECRET_KEY = '61aBearsMWF23'
USERNAME = 'admin'
PASSWORD = 'GoBears2019'

app = Flask(__name__)
app.config.from_object(__name__)
app.config.from_envvar('CW_SETTINGS', silent=True)

def connect_db():
    return sqlite3.connect(app.config['DATABASE'])

if __name__ == '__main__':
    app.run()


################################################

@app.before_request
def before_request():
    g.db = connect_db()

@app.teardown_request
def teardown_request(exception):
    db = getattr(g, 'db', None)
    if db is not None:
        db.close()

################################################

@app.route('/')
def show_entries():
    cur = g.db.execute('select title, text from entries order by id desc')
    entries = [dict(title=row[0], text=row[1]) for row in cur.fetchall()]
    return render_template('show_entries.html', entries=entries)

@app.route('/add', methods=['POST'])
def add_entry():
    if not session.get('logged_in'):
        abort(401)
    g.db.execute('insert into entries (title, text) values (?, ?)',
                 [request.form['title'], request.form['text']])
    g.db.commit()
    flash('New entry was successfully posted')
    return redirect(url_for('show_entries'))


################################################

class RegistrationForm(Form):
    username = TextField('Username', [validators.Length(min=4, max=25)])
    email = TextField('Email Address', [validators.Length(min=6, max=35)])
    check_val=FloatField('Notify me when my BTC amount', [[validators.Length(min=0, max=5)]])
    operator= SelectField('is', choices = ['worth at least', 'worth less than', 'devalued by 5%', 'grown by 5%'])
    usd_val=FloatField('$', [[validators.Length(min=0, max=5)]])
    accept_tos = BooleanField('I accept the TOS', [validators.Required()])
