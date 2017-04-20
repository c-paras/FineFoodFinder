#!/usr/bin/env python
#Copyright (C) 2017 Team Centipede
#SENG2011 17s1 Project
#Implements a prototype for Fine Food Finder

import os, re, sqlite3, db_interface, uuid
from flask import *

# Create new flask app
app = Flask(__name__)
app.secret_key = open('.flask_key').read().strip()

# Landing page
@app.route('/')
def home_page():
    return render_template('home.html')

# Login page
@app.route('/login', methods=['GET', 'POST'])
def login():
	if request.method == 'GET': # First page load
		return render_template('login.html', status='')
	else:
		# User has pressed login button
		username = request.form.get('user')
		password = request.form.get('pass')
		db = sqlite3.connect('data.db')
		c = db.cursor()

		#check user & pass in db
		res = c.execute('SELECT * FROM Users WHERE username="%s" AND password="%s"' %(username, password))
		try:
			res.fetchone()[0]
			return render_template('home.html')
		except:
			err = 'Invalid username or password.'
			return render_template('login.html', status=err)
		db.close()

# Registration page
@app.route('/register', methods=['GET', 'POST'])
def register():
	if request.method == 'GET': # Load registration form
		return render_template('register.html', status='')
	else:
		full_name = request.form.get('full_name')
		user = request.form.get('user')
		pass1 = request.form.get('pass1')
		pass2 = request.form.get('pass2')
		email = request.form.get('email')

		if 'cancel' in request.form: # Cancel registration, return to login page
			return redirect(url_for('login'))
		elif full_name == '' or user == '' or pass1 == '' or pass2 == '' or email == '':
			# No blank fields allowed
			err = 'Fields marked with (*) are required.'
			return render_template('register.html', status=err)
		elif not re.match(r'.+@.+', email):
			return render_template('register.html', status='Invalid email.')
		elif pass1 != pass2:
			return render_template('register.html', status='Passwords do not match.')
		else:
			# Correct registration details
			db = sqlite3.connect('data.db')
			c = db.cursor()

			#check if user or email already registered
			res = c.execute('SELECT * FROM Users WHERE username="%s"' %user)
			try:
				res.fetchone()[0]
				err = 'An account with that username already exists.'
				return render_template('register.html', status=err)
			except:
				pass

			res = c.execute('SELECT * FROM Users WHERE email="%s"' %email)
			try:
				res.fetchone()[0]
				err = 'The specified email is already associated with an account.'
				return render_template('register.html', status=err)
			except:
				pass

			#TODO: send email with confirmation link
			confirm_id = 'confirm_id=' + str(uuid.uuid4())
			#TODO

			flash('Confirmation email sent to ' + email + '.')
			c.execute('''INSERT INTO Users (full_name, username, password, email, status) VALUES (?, ?, ?, ?, ?)''', (full_name, user, pass1, email, confirm_id))

			db.commit()
			db.close()
			return redirect(url_for('login'))

@app.route('/restaurants')
def restaurants_page():
	conn = sqlite3.connect('data.db')
	c = conn.cursor()
	restaurants = db_interface.get_restaurants(c)
	conn.close()
	return render_template('restaurants.html', restaurants=restaurants)

# Serve static files from static/
@app.route('/static/<path:path>')
def send_static_file(path):
	return send_from_directory('static', path)

if __name__ == '__main__':
	app.run(debug=True, use_reloader=True)
