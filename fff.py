#!/usr/bin/env python
# Copyright (C) 2017 Team Centipede
# SENG2011 17s1 Project
# Implements a prototype for Fine Food Finder

import os, re, sqlite3, db_interface, uuid
from flask import *
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib

# Create new flask app
app = Flask(__name__)
app.secret_key = open('.flask_key').read().strip()


# Landing page
@app.route('/', methods=['GET', 'POST'])
def home_page():
    if request.method == 'GET':
        return render_template('home.html')
    elif request.method == 'POST':
        search_term = request.form.get('search-box')
        search_criteria = request.form.get('search-criteria')
        if not search_criteria:
            search_criteria = "any"

        return redirect(url_for('restaurants_page', search_term=search_term, search_criteria=search_criteria))


# Login page
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':  # First page load
        return render_template('login.html')
    else:  # User has pressed login button
        username, password = request.form.get('user'), request.form.get('pass')
        conn = sqlite3.connect('data.db')
        c = conn.cursor()

        login_status = db_interface.check_login(c, username, password)
        conn.close()
        if login_status is True:
            session['logged_in'] = True
            return render_template('home.html')

        if not login_status:
            return render_template('login.html', status='Invalid username or password')
        elif login_status == 'inactive':
            return render_template('login.html', status='Please confirm your account first.')


# Log out user
@app.route('/logout')
def logout():
    if 'logged_in' in session:
        session.pop('logged_in', None)
        flash('Successfully logged out.')
    else:
        flash('You are not logged in.')
    return redirect(url_for('home_page'))


# Registration page
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET': # Load registration form
        return render_template('register.html', status='')
    else:
        full_name = request.form.get('full_name')
        user = request.form.get('user')
        pass1, pass2 = request.form.get('pass1'), request.form.get('pass2')
        email = request.form.get('email')

        if not (full_name and user and pass1 and pass2 and email):  # No blank fields allowed
            err = 'Fields marked with (*) are required.'
            return render_template('register.html', status=err)
        elif not re.match(r'.+@.+', email):
            return render_template('register.html', status='Invalid email.')
        elif pass1 != pass2:
            return render_template('register.html', status='Passwords do not match.')
        else:  # Correct registration details
            conn = sqlite3.connect('data.db')
            c = conn.cursor()

            # Check if user or email already registered
            if db_interface.check_username_exists(c, user):
                err = 'An account with that username already exists.'
                return render_template('register.html', status=err)

            if db_interface.check_email_exists(c, email):
                err = 'The specified email is already associated with an account.'
                return render_template('register.html', status=err)

            # Sends email with confirmation link
            confirm_id = str(uuid.uuid4())
            link = os.path.join(request.url_root, 'confirm', user, confirm_id)
            body = 'Please visit the following link to confirm your account: ' + link
            send_email(email, body, 'Account Confirmation')

            flash('Confirmation email sent to {}.'.format(email))
            db_interface.add_user(c, full_name=full_name, username=user, password=pass1, email=email, confirm_id=confirm_id)
            conn.commit()
            conn.close()
            return redirect(url_for('login'))


@app.route('/confirm/<path:user>/<path:uuid>', methods=['GET', 'POST'])
def confirm(user, uuid):
    conn = sqlite3.connect('data.db')
    c = conn.cursor()

    confirmed = db_interface.confirm(c, user, uuid)  # Activate account if link is valid
    if confirmed:
        flash('Your account has been activated. Please log in.')
    else:
        flash('Invalid confirmation link!')

    conn.commit()
    conn.close()
    return redirect(url_for('login'))


@app.route('/restaurants', defaults={'rest_id': None})
@app.route('/restaurants/<path:rest_id>')
def restaurants_page(rest_id=None):
    conn = sqlite3.connect('data.db')
    c = conn.cursor()

    if rest_id: # Display individual restaurant
        r = db_interface.get_restaurant_by_id(c, id=rest_id)
        if r:
            return render_template('restaurant.html', restaurant=r)
    else:
        search_term = request.args.get('search_term')
        search_criteria = request.args.get('search_criteria')

        if not search_term: # Not passed in, pull all restaurants from db
            restaurants = db_interface.get_restaurants(c)
        else: # Search
            restaurants = db_interface.search_restaurants(c, criteria=search_criteria, search_term=search_term)
        return render_template('restaurants.html', restaurants=restaurants)
    conn.close()


# Serve static files from static/
@app.route('/static/<path:path>')
def send_static_file(path):
    return send_from_directory('static', path)


# Sends an email to the specified address
def send_email(to, body, subject):
    noreply = 'noreply.fine.food.finder@gmail.com'
    noreply_password = '15fac6da-2980-4586-b9f2-ae521261b391'

    # Construct email
    msg = MIMEMultipart()
    msg['From'] = noreply
    msg['To'] = to
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    # Send the email from gmail account using smtp
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(noreply, noreply_password)
    server.sendmail(noreply, to, msg.as_string())
    server.quit()

if __name__ == '__main__':
    app.run(debug=True, use_reloader=True)
