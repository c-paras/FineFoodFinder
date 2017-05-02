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
    if request.method == 'GET': # First page load
        return render_template('login.html', status='')
    else:
        # User has pressed login button
        username = request.form.get('user')
        password = request.form.get('pass')
        db = sqlite3.connect('data.db')
        c = db.cursor()

        # Check user & pass in db
        res = c.execute('SELECT * FROM Users WHERE username="%s" AND password="%s"' %(username, password))
        try:
            res.fetchone()[0]
            res = c.execute('SELECT status FROM Users WHERE username="%s"' %username)
            if res.fetchone()[0] != 'active':
                flash('Please confirm your account first.')
            else:
                session['logged_in'] = True
            return render_template('home.html')
        except:
            err = 'Invalid username or password.'
            return render_template('login.html', status=err)
        db.close()


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

            # Sends email with confirmation link
            confirm_id = str(uuid.uuid4())
            link = os.path.join(request.url_root, 'confirm', user, confirm_id)
            body = 'Please visit the following link to confirm your account: ' + link
            send_email(email, body, 'Account Confirmation')

            flash('Confirmation email sent to ' + email + '.')
            c.execute('''INSERT INTO Users (full_name, username, password, email, status) VALUES (?, ?, ?, ?, ?)''', (full_name, user, pass1, email, confirm_id))

            db.commit()
            db.close()
            return redirect(url_for('login'))


@app.route('/confirm/<path:user>/<path:uuid>', methods=['GET', 'POST'])
def confirm(user, uuid):
    db = sqlite3.connect('data.db')
    c = db.cursor()

    # Activate account if link is valid
    res = c.execute('SELECT * FROM Users WHERE username="%s" AND status="%s"' %(user, uuid))
    try:
        res.fetchone()[0]
        c.execute('UPDATE Users SET status="%s" WHERE username="%s"' %('active', user))
    except:
        #invalid link
        return redirect(url_for('login'))

    db.commit()
    db.close()
    flash('You account has been activated. Please log in.')
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
