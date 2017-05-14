#!/usr/bin/env python
# Copyright (C) 2017 Team Centipede
# SENG2011 17s1 Project
# Implements a prototype for Fine Food Finder

import os, re, sqlite3, uuid, datetime
import fff_helpers, db_interface
from flask import *
import threading

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

        if not search_criteria:  # Default search criteria
            search_criteria = "any"

        any, name, cuisine, suburb = None, None, None, None
        if search_criteria == "any":
            any = search_term
        if search_criteria == "name":
            name = search_term
        if search_criteria == "cuisine":
            cuisine = search_term
        if search_criteria == "suburb":
            suburb = search_term

        return redirect(url_for('restaurants_page', any=any, name=name, cuisine=cuisine, suburb=suburb))


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
            session['username'] = username
            flash('Successfully logged in!')
            return redirect(url_for('home_page'))

        if not login_status:
            return render_template('login.html', status='Invalid username or password')
        elif login_status == 'inactive':
            return render_template('login.html', status='Please confirm your account first.')


# Log out user
@app.route('/logout')
def logout():
    if 'logged_in' in session:
        session.pop('logged_in', None)
        session.pop('username', None)
        flash('Successfully logged out.')
    else:
        flash('You are not logged in.')
    return redirect(url_for('home_page'))


# Registration page
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':  # Load registration form
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
        elif pass1 in user:
            return render_template('register.html', status='Username must not contain password.')
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
            body = 'Please visit the following link to confirm your FFF account: ' + link
            threading.Thread(target=fff_helpers.send_email, args=(email, body, 'Fine Food Finder Account Confirmation')).start()
            flash('Confirmation email sent to {}.'.format(email))
            db_interface.add_user(c, full_name=full_name, username=user, password=pass1, email=email,
                                  confirm_id=confirm_id)
            conn.commit()
            conn.close()
            return redirect(url_for('login'))


@app.route('/confirm/<path:user>/<path:uuid>', methods=['GET', 'POST'])
def confirm(user, uuid):
    conn = sqlite3.connect('data.db')
    c = conn.cursor()

    confirmed = db_interface.confirm(c, user, uuid)  # Activate account if link is valid
    if confirmed:
        session['logged_in'] = True
        session['username'] = user
        flash('Your account has been activated. You are now logged in!')
        return redirect(url_for('home_page'))
    else:
        flash('Invalid confirmation link!')

    conn.commit()
    conn.close()
    return redirect(url_for('login'))


# Individual restaurant page
@app.route('/restaurants/<path:rest_id>', methods=['GET', 'POST'])
def restaurant_page(rest_id):
    conn = sqlite3.connect('data.db')
    c = conn.cursor()
    r = db_interface.get_restaurant_by_id(c, id=rest_id)
    if r:
        reviews = db_interface.get_reviews(c, rest_id)
        already_reviewed = db_interface.already_reviewed_restaurant(c, rest_id, session['username'])
        if request.method == 'GET':
            return render_template('restaurant.html', restaurant=r, logged_in=('username' in session),
                                   reviews=reviews, already_reviewed=already_reviewed)
        elif request.method == 'POST':
            if request.form.get('rating'):  # Rating
                already_rated = db_interface.already_rated_restaurant(c, rest_id, session['username'])
                rating = float(request.form.get('rating'))
                if not already_rated:
                    add_rating = db_interface.add_rating(c, rest_id, session['username'], rating)

                    if add_rating:
                        flash('Thanks for rating!')
                        conn.commit()
                    else:
                        flash('Unable to rate!')
                else:
                    update_rating = db_interface.update_rating(c, rest_id, session['username'], rating)
                    if update_rating:
                        flash('Rating updated!')
                        conn.commit()
                    else:
                        flash('Unable to rate!')
            elif request.form.get('review-body'):  # Submit review
                review_body = request.form.get('review-body')
                add_review = db_interface.add_review(c, session['username'], rest_id, review_body,
                                                     datetime.datetime.now())
                if add_review:
                    flash('Review added!')
                    conn.commit()
                else:
                    flash('Unable to add review!')
            return redirect(url_for('restaurant_page', rest_id=rest_id))
    else:
        flash('Restaurant not found!')
        return redirect(url_for('restaurants_page'))


# Restaurants search results
@app.route('/restaurants', methods=['GET', 'POST'])
def restaurants_page():
    conn = sqlite3.connect('data.db')
    c = conn.cursor()

    if request.form.get('search-box'):  # Using sidebar search box
        search_term = request.form.get('search-box')
        search_criteria = request.form.get('search-criteria')

        if not search_criteria:  # Default search criteria
            search_criteria = "any"

        any, name, cuisine, suburb = None, None, None, None
        if search_criteria == "any":
            any = search_term
        if search_criteria == "name":
            name = search_term
        if search_criteria == "cuisine":
            cuisine = search_term
        if search_criteria == "suburb":
            suburb = search_term

        return redirect(url_for('restaurants_page', any=any, name=name, cuisine=cuisine, suburb=suburb))
    else:
        name = request.args.get('name') or request.form.get('name')
        cuisine = request.args.get('cuisine') or request.form.get('cuisine')
        suburb = request.args.get('suburb') or request.form.get('suburb')
        any = request.args.get('any') or request.form.get('any')

        # print('name', name)
        # print('cuisine', cuisine)
        # print('suburb', suburb)

        restaurants = db_interface.get_restaurants(c)
        if name or cuisine or suburb or any:  # Search
            restaurants = fff_helpers.filter_restaurants(restaurants, name=name, cuisine=cuisine, cost="",
                                                         suburb=suburb, rating="", any_field=any)

        suburbs = set(r.get_suburb() for r in restaurants)
        cuisines = set(r.get_cuisine() for r in restaurants)
        conn.close()
        return render_template('restaurants.html', name=name, cuisine=cuisine, suburb=suburb, restaurants=restaurants,
                               suburbs=suburbs, cuisines=cuisines)


# Submit new restaurant page
@app.route('/submit_restaurant', methods=['GET', 'POST'])
def submit_restaurant():
    if request.method == 'GET':
        return render_template('submit_restaurant.html', status='')
    else:
        restaurant_id = None  # TODO
        name = request.form.get('name')
        suburb = request.form.get('suburb')
        address = request.form.get('address')
        postcode = request.form.get('postcode')
        phone = request.form.get('phone').replace('(', '').replace(')', '')
        hours = request.form.get('hours')
        cuisine = request.form.get('cuisine')
        owner = None  # user_logged_in TODO
        website = request.form.get('website')
        cost = request.form.get('cost')
        image = request.form.get('image')

        if not (name and suburb and address and postcode and cuisine and cost):
            err = 'Fields marked with (*) are required.'
            return render_template('submit_restaurant.html', status=err)
        elif not re.match(r'^[0-9]{4}$', postcode):
            err = ''
            return render_template('submit_restaurant.html', status=err)
        # TODO: more validation...
        else:
            conn = sqlite3.connect('data.db')
            c = conn.cursor()

            # TODO: deal with empty fields - default data
            flash('Your restaurant has been added.')
            data = (restaurant_id, name, suburb, address, postcode, phone, hours, cuisine, owner, website, cost, image)
            c.execute(
                '''INSERT INTO Users (restaurant_id, name, suburb, address, postcode, phone, hours, cuisine, owner, website, cost, image)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', data)
            conn.commit()
            conn.close()
            return redirect(url_for('home_page'))


# Serve static files from static/
@app.route('/static/<path:path>')
def send_static_file(path):
    return send_from_directory('static', path)


if __name__ == '__main__':
    app.run(debug=True, use_reloader=True)
