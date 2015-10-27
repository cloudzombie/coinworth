import datetime
import requests
#
import simplejson as json
#
import sqlite3
import schedule
import time
#


from flask.ext.wtf import Form
from wtforms.fields import TextField, PasswordField,  BooleanField, FloatField, RadioField, SelectField
from wtforms import validators

import plotly.plotly as py
import plotly.graph_objs as go

from contextlib import closing


#######################################################################
import os
from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash



# Initialize the Flask application
app = Flask(__name__)


# Define a route for the default URL, which loads the form
@app.route('/')
def form():
    return render_template('form_submit.html')

# Define a route for the action of the form, for example '/hello/'
# We are also defining which type of requests this route is 
# accepting: POST requests in this case
@app.route('/hello/', methods=['POST'])
def hello(ID=1):
    name=request.form['yourname']
    email=request.form['youremail']
    btc_amount=request.form['btc_amount']
    usd_val=request.form['usd_val']
    operator=request.form['operator']
    notify=1

    #Establish databse connection
    connect=sqlite3.connect('test_users.sqlite')
    cursor=connect.cursor()

    #Insert new rows
    cursor.execute("INSERT into users values (?, ?, ?, ?, ?, ?, ?)",
            (ID, name, email, btc_amount, usd_val, operator, notify))
    connect.commit()
    #commit to db HERE

    if operator==0:
        operator= 'is worth at least %s USD' % usd_val
    if operator==1:
        operator= 'is worth below %s USD' % usd_val
    if operator==2:
        operator= 'has grown 5%% in value'
    if operator==3:
        operator= 'has dropped 5%% in value'

    

    return render_template('form.html', name=name, btc_amount=btc_amount, usd_val=usd_val, operator=operator)

# Run the app :)
if __name__ == '__main__':
  app.run(  debug=True,
        host="0.0.0.0",
        port=int("80")
  )
