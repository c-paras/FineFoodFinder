#!/usr/bin/env python3
# SENG2011 17s1 Project
# By: team centipede
# Implements a prototype for Fine Food Finder

import os, re
from flask import Flask, request, render_template, send_from_directory, redirect, url_for

#create new flask app
app = Flask(__name__)
app.secret_key = os.urandom(1) # TODO replace with a single secret_key

#register page
@app.route('/register', methods=['GET', 'POST'])
def register():
	if request.method == 'GET':
		#first page load
		return render_template('register.html', status='')
	else:
		user  = request.form.get('user')
		pass1 = request.form.get('pass1')
		pass2 = request.form.get('pass2')
		email = request.form.get('email')

		if 'cancel' in request.form: # Cancel registration, return to login page
			return redirect(url_for('login'))
		elif user == '' or pass1 == '' or pass2 == '' or email == '':
			# no blank fields allowed
			return render_template('register.html', status='Fields marked with (*) are required.')
		elif not re.match(r'.+@.+', email):
			return render_template('register.html', status='Invalid email.')
		elif pass1 != pass2:
			return render_template('register.html', status='Passwords do not match.')
		else:
			# correct registration details
			flash('Confirmation email sent to ' + email + '.')
			return redirect(url_for('login'))

#landing page
@app.route('/')
def home_page():
    return render_template('home.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
	if request.method == 'GET': # first page load
		return render_template('login.html', status='')
	else:
		# user has pressed login button
		username = request.form.get('user')
		password = request.form.get('pass')

		# check username & password
		if username != 'costa' or password != 'qwerty':
			return render_template('login.html', status='Invalid username or password.')
		else:
			return render_template('home.html')

# Serve static files from static/
@app.route('/static/<path:path>')
def send_static_file(path):
	return send_from_directory('static', path)

if __name__ == '__main__':
	app.run(debug=True, use_reloader=True)
