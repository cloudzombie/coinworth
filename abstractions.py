import datetime
import requests
import simplejson as json
import sqlite3
import schedule
import time
from flask.ext.mail import Message # mail tools
from coinworth import app, mailbox

###############################
#      	 Abstractions         #
###############################

notified = [] # A lit of notified users

def response_dict():
	"""Sends an HTML request to BitStamp and returns the response as a python dictionary of  BTC prices with values as floats
	last - last BTC price
	high - last 24 hours price high
	low - last 24 hours price low
	vwap - last 24 hours volume weighted average price
	volume - last 24 hours volume
	bid - highest buy order
	ask - lowest sell order
	"""
	response = requests.get('https://www.bitstamp.net/api/ticker/')
	return response.json()



def get_last(d):
	"""Returns the last BTC price"""
	return float(d["last"])


def get_high(d):
	"""Returns the last 24 hours price high"""
	return float(d["high"])

def get_low(d):
	"""Returns the last 24 hours price low"""
	return float(d["low"])

def get_vwap(d):
	"""Returns the last 24 hours volume weighted average price"""
	return float(d["vwap"])

def get_volume(d):
	"""Returns the last 24 hours trade volume"""
	return float(d["volume"])

def get_bid(d):
	"""Returns the highest buy order"""
	return float(d["bid"])

def get_ask(d):
	"""Returns the lowest sell order"""
	return float(d["bid"])

def get_time(d):
	"""Returns  the current time"""
	return datetime.datetime.fromtimestamp(int(d["timestamp"])).strftime('%m-%d %H:%M:%S')

def create_row_template(d):
	"""Creates a tuple that represents a single row in a table"""
	return (get_last(d), get_high(d), get_low(d), get_vwap(d), get_volume(d), get_bid(d), get_ask(d), get_time(d))

def create_price_table(connection='test_table.sqlite'):
	connect=sqlite3.connect(connection)
	cursor=connect.cursor()
	cursor.execute('''CREATE TABLE prices(last real, high real, low real, vwap real, volume real, bid real, ask real, time timestamp)''')
	connect.commit()

def create_user_table():
	"""Creates a table of users with numbered rows containing 
	name - user's name (text)
	contact - user's email (text)
	btc_amount - user's value to be compared (float)
	usd_val - user's desired value in USD
	operator - function used to compare check_val to market price (0 or 1)
	curr_price - btc price at the moment of the user's submission"""

	connect=sqlite3.connect('test_users.sqlite')
	cursor=connect.cursor()
	cursor.execute('''CREATE TABLE users            (RowID int, name varchar(35), contact varchar(50), btc_amount real , usd_val real, operator int, curr_price real)''')
	connect.commit()

def update_prices(row_temp, connection='test_table.sqlite'):
	"""Updates database of prices with the values from the row template passed as a tuple"""
	'''temporarily takes 8 or 9 length to make input work with or wothout row IDs'''
	assert len(row_temp) == 8 or len(row_temp) == 9, "Invalid row template"
	#Establish databse connection
	connect=sqlite3.connect(connection)
	cursor=connect.cursor()

	#Insert new rows
	if len(row_temp) == 8:
		cursor.execute("INSERT into prices values (?, ?, ?, ?, ?, ?, ?, ?)",
	            row_temp)
		connect.commit()
	else:
		cursor.execute("INSERT into prices values (?, ?, ?, ?, ?, ?, ?, ?, ?)",
	            row_temp)
		connect.commit()

def update_users(ID, name, email, btc_amount, usd_val, operator, curr_price):
	#Establishing databse connection
	connect=sqlite3.connect('test_users.sqlite')
	cursor=connect.cursor()
	#Inserting new rows
	cursor.execute("INSERT into users values (?, ?, ?, ?, ?, ?, ?)", # data abstraction violation here
			(ID, name, email, btc_amount, usd_val, operator, curr_price))
	connect.commit()
	

def get_column(column, table, connection='test_table.sqlite', min_id = False):
	"""Gets all the data from a single column in the table and returns an ordered list"""
	"""temporary If/ Else for when last argument isn't present"""
	connect=sqlite3.connect(connection)
	cursor=connect.cursor()
	if type(min_id) == int:
		return [row for row in cursor.execute('SELECT ' + column + ' from '  + table + ' WHERE id > ' + str(min_id) )]
	else:
		return [row for row in cursor.execute('SELECT ' + column + ' from '  + table)]


def count_rows(table, connection = 'test_table.sqlite'):
	'''returns the number of rows in a specific table, given the table and file'''
	connect=sqlite3.connect(connection)
	cursor=connect.cursor()
	cursor.execute('SELECT COUNT(*) FROM ' + table)
	row_num_tuple = cursor.fetchone()
	return row_num_tuple[0]

def user_dict(row):
	"""Creates a dictionary for easy access to user information"""
	return {
		'id': row[0],
		'name': row[1],
		'contact': row[2],
		'btc_amount':row[3],
		'usd_val': row[4],
		'operator': row[5],
		'current': row[6]
	}


def at_least(user_btc, market, user_usd, user_price=None):
	"""Returns True if user's BTC amount converted to USD using market BTC price is worth at least the user defined USD amount"""
	return float(user_btc)*float(market)>=user_usd

def at_most(user_btc, market, user_usd, user_price=None):
	"""Returns True if user's BTC amount converted to USD using market BTC price is worth no more than the user defined USD amount"""
	return float(user_btc)*float(market)<=user_usd

def minus_five_percent(user_btc, market, user_usd, user_price):
	#user_usd is ignored
	#user_btc is ignored
	"""Returns True if the user's BTC amount has fallen by 5 percent in value"""
	return float(market)/float(user_price)<=0.95

def plus_five_percent(user_btc, market, user_usd, user_price):
	#user_usd is ignored
	#user_btc is ignored
	"""Returns True if the user's BTC amount has grown by 5 percent in value"""
	return float(market)/float(user_price)>=1.05

 
func_dict = {
# A dictionary for quick access to the comparator functions 
	"0": at_least,
	"1": at_most,
	"2": plus_five_percent,
	"3": minus_five_percent
}



def perform_check(d):
	"""Checks if user-specified event has been triggered, and calls the notification procedure if user has not been notified before"""

	connect = sqlite3.connect('test_users.sqlite') # Connecting to the database of users
	cursor = connect.cursor()

	compare = None  # Initializing the local variables for reassignment below
	message = None

	print("Checking...")

	# Iterating through users in the table
	for user in [user_dict(row) for row in cursor.execute('SELECT * FROM users')]:
		compare = func_dict[str(user['operator'])] # Select the comparator
		if compare(user['btc_amount'], d['last'], user['usd_val'], user['current']): # (delete ':' + this statement and uncomment) # and user['contact'] not in notified: 
			print("Notification triggered!")
			notify(user['name'], user['contact'], message) # Calling notification procedure
			#notified.append(user['contact']) # Adding the user to the list of notified users.


def notify(name, contact, message):
	"""Notifies the user at the provided email, using the body of the message determined by the comparing function"""
	print("Creating a message object...")
	msg = Message(
              'This is a test',
	       sender='coinworthupdate@gmail.com',
	       recipients=
               [contact])
	msg.body = "Hello, %s. This is a test" % name
	print("Passing to the mailbox...")
	mailbox.send(msg)
	print('Sent!')





