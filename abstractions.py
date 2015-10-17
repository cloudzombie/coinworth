import datetime
import requests
import simplejson as json
import sqlite3
import schedule
import time

###############################
#      	 Abstractions         #
###############################

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
	response=requests.get('https://www.bitstamp.net/api/ticker/')
	return response.json()
d= response_dict()

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
	cursor.execute('''CREATE TABLE prices(id int, last real, high real, low real, vwap real, volume real, bid real, ask real, time timestamp)''')
	connect.commit()

def create_user_table():
	"""Creates a table of users with numbered rows containing 
	name - user's name (text)
	contact - user's email (text)
	check_val - user's value to be compared (float)
	operator - function used to compare check_val to market price (0 or 1)
	notify - 1 if user is to be notified, 0 if user has already been notified"""

	connect=sqlite3.connect('test_users.sqlite')
	cursor=connect.cursor()
	cursor.execute('''CREATE TABLE users            (RowID int, name varchar(35), contact varchar(50), check_val real , usd_val real, operator int, notify int''')
	connect.commit()
	
def update_prices(row_temp, connection='test_table.sqlite'):
	"""Updates database of prices with the values from the row template passed as a tuple"""
	assert len(row_temp)==9, "Invalid row template"
	#Establish databse connection
	connect=sqlite3.connect(connection)
	cursor=connect.cursor()

	#Insert new rows
	cursor.execute("INSERT into prices values (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            row_temp)
	connect.commit()

def get_column(column, table, connection='test_table.sqlite'):
	"""gets all the data from a single column in the data and returns an ordered list"""
	connect=sqlite3.connect(connection)
	cursor=connect.cursor()
	return [row for row in cursor.execute('SELECT ' + column + ' from '  + table)]

def user_dict(row):
	return {
		'id': row[0],
		'name': row[1],
		'contact': row[2],
		'check_val':row[3],
		'usd_val': row[4],
		'operator': row[5],
		'notify': row[6]
	}

def at_least(user_check, user_usd, market=get_last(d)):
	"""Returns True if user's BTC amount converted to USD using market BTC price is worth at least the user defined USD amount"""
	return user_check*(1/market)>=user_usd

def at_most(user_check, user_usd, market=get_last(d)):
	"""Returns True if user's BTC amount converted to USD using market BTC price is worth no more than the user defined USD amount"""
	return user_check*(1/market)<=user_usd

def minus_five_percent(a, b):
	"""Returns True if the user's BTC amount has fallen by 5\% n value"""
	


def perform_check(d):
	connect=sqlite3.connect('test_users.sqlite')
	cursor=connect.cursor()

	compare=None
	body=None
	for user in [user_dict(row) for row in cursor.execute('SELECT * FROM users')]:
		if not user['operator']:
			compare=at_least
			body=0
		elif user['operator']==1:
			compare=at_most
			body=1
		elif user['operator']==2:
			compare=minus_five_percent
			body=2
		elif user['operator']==3:
			compare=plus_five_percent
			body=3
		if compare(user['check_val'], user['usd_val']):
			notify(user['name'], user['contact'], body)

def notify(name, contact, body):
	"""Notifies the user at the provided email, using the body of the message determined by the comparing function"""
	pass




