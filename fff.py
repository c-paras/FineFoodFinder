#!/usr/bin/env python
#Copyright (C) 2017 Team Centipede
#SENG2011 17s1 Project
#Implements a prototype for Fine Food Finder

import os, re, sqlite3, db_interface
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

		# Check username & password
		if username != 'costa' or password != 'qwerty':
			err = 'Invalid username or password.'
			return render_template('login.html', status=err)
		else:
			return render_template('home.html')

# Registration page
@app.route('/register', methods=['GET', 'POST'])
def register():
	if request.method == 'GET': # Load registration form
		return render_template('register.html', status='')
	else:
		user  = request.form.get('user')
		pass1 = request.form.get('pass1')
		pass2 = request.form.get('pass2')
		email = request.form.get('email')

		if 'cancel' in request.form: # Cancel registration, return to login page
			return redirect(url_for('login'))
		elif user == '' or pass1 == '' or pass2 == '' or email == '':
			# No blank fields allowed
			err = 'Fields marked with (*) are required.'
			return render_template('register.html', status=err)
		elif not re.match(r'.+@.+', email):
			return render_template('register.html', status='Invalid email.')
		elif pass1 != pass2:
			return render_template('register.html', status='Passwords do not match.')
		else:
			# Correct registration details
			flash('Confirmation email sent to ' + email + '.')
			return redirect(url_for('login'))

@app.route('/restaurants')
def restaurants_page():
	conn = sqlite3.connect('data.db')
	c = conn.cursor()
	restaurants = db_interface.get_restaurants(c)
	return render_template('restaurants.html', restaurants=restaurants)

# Serve static files from static/
@app.route('/static/<path:path>')
def send_static_file(path):
	return send_from_directory('static', path)

if __name__ == '__main__':
	app.run(debug=True, use_reloader=True)
