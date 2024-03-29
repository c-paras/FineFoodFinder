#!/usr/bin/env python3
# Copyright (C) 2017 Team Centipede
# SENG2011 17s1 Project
# Implements a prototype for Fine Food Finder

import os, re, sqlite3, uuid, datetime, math
import db_interface, helpers_fff
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
    if 'logged_in' in session:
        flash('You are already logged in.')
        return redirect(url_for('home_page'))

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


# checks if user is admin
@app.context_processor
def utility_processor():
    def is_admin(user):
        conn = sqlite3.connect('data.db')
        c = conn.cursor()
        is_ad = c.execute('SELECT admin FROM Users where username="%s"' % user).fetchone()[0]
        if is_ad == 0:
            return False
        else:
            return True

    return dict(is_admin=is_admin)


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
    if 'logged_in' in session:
        flash('You have already registered for an account and are logged in.')
        return redirect(url_for('home_page'))

    if request.method == 'GET':  # Load registration form
        return render_template('register.html', status='')
    else:
        full_name = request.form.get('full_name')
        user = request.form.get('user')
        pass1, pass2 = request.form.get('pass1'), request.form.get('pass2')
        email = request.form.get('email')

        if not (full_name and user and pass1 and pass2 and email):  # No blank fields allowed
            err = 'Fields marked with (*) are required.'
            return render_template('register.html', status=err, name=full_name, user=user, email=email)
        elif len(user) < 5:
            return render_template('register.html', status='Username must contain at least 5 characters.', name=full_name, user=user, email=email)
        elif pass1 != pass2:
            return render_template('register.html', status='Passwords do not match.', form_data=form_data)
        elif len(pass1) < 5:
            return render_template('register.html', status='Password must contain at least 5 characters.', name=full_name, user=user, email=email)
        elif pass1 in user:
            return render_template('register.html', status='Username must not contain password.', name=full_name, user=user, email=email)
        elif not re.match(r'.+@.+', email):
            return render_template('register.html', status='Invalid email.', name=full_name, user=user, email=email)

        else:  # Correct registration details
            conn = sqlite3.connect('data.db')
            c = conn.cursor()

            # Check if user or email already registered
            if db_interface.check_username_exists(c, user):
                err = 'An account with that username already exists.'
                return render_template('register.html', status=err, name=full_name, user=user, email=email)

            if db_interface.check_email_exists(c, email):
                err = 'The specified email is already associated with an account.'
                return render_template('register.html', status=err, name=full_name, user=user, email=email)

            # Sends email with confirmation link
            confirm_id = str(uuid.uuid4())
            link = os.path.join(request.url_root, 'confirm', user, confirm_id)
            body = 'Please visit the following link to confirm your FFF account: ' + link
            threading.Thread(target=helpers_fff.send_email,
                             args=(email, body, 'Fine Food Finder Account Confirmation')).start()
            flash('Confirmation email sent to {}.'.format(email))
            db_interface.add_user(c, full_name=full_name, username=user, password=pass1, email=email,
                                  confirm_id=confirm_id, admin=0)
            conn.commit()
            conn.close()
            return redirect(url_for('login'))


@app.route('/confirm/<path:user>/<path:uuid>', methods=['GET', 'POST'])
def confirm(user, uuid):
    conn = sqlite3.connect('data.db')
    c = conn.cursor()

    confirmed = db_interface.confirm(c, user, uuid)  # Activate account if link is valid
    conn.commit()
    conn.close()

    if confirmed:
        session['logged_in'] = True
        session['username'] = user
        flash('Your account has been activated. You are now logged in!')
        return redirect(url_for('home_page'))
    else:
        flash('Invalid confirmation link!')

    return redirect(url_for('login'))


# Individual restaurant page
@app.route('/restaurant/<path:rest_id>', methods=['GET', 'POST'])
def restaurant_page(rest_id):
    conn = sqlite3.connect('data.db')
    c = conn.cursor()
    r = db_interface.get_restaurant_by_id(c, id=rest_id)
    if r:
        reviews = db_interface.get_reviews(c, rest_id)
        already_reviewed = False
        already_rated = False
        user_rating = 0
        if 'username' in session:
            already_reviewed = db_interface.already_reviewed_restaurant(c, rest_id, session['username'])
            already_rated = db_interface.already_rated_restaurant(c, rest_id, session['username'])
            if already_rated:
                user_rating = db_interface.find_user_rating(c, session['username'], rest_id)

        if request.method == 'GET':
            return render_template('restaurant.html', restaurant=r, logged_in=('username' in session),
                                   reviews=reviews, already_reviewed=already_reviewed, already_rated = already_rated,
                                   user_rating=user_rating)
        elif request.method == 'POST':
            if request.form.get('rating'):  # Rating
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
                if re.match(r'^\s*$', review_body):
                    return redirect(url_for('restaurant_page', rest_id=rest_id))
                add_review = db_interface.add_review(c, session['username'], rest_id, review_body,
                                                     datetime.datetime.now(), 0)
                if add_review:
                    flash('Thank you for your review!')
                    conn.commit()
                else:
                    flash('Unable to add review!')
            elif request.form.get('report_review'):
                report_id = request.form.get('report_id')
                c.execute('UPDATE Reviews SET reported=1 where id="%s"' % report_id)
                flash('Thanks for reporting this review. An administrator will review your report.')
                conn.commit()

            return redirect(url_for('restaurant_page', rest_id=rest_id))
    else:
        flash('Restaurant not found!')
        return redirect(url_for('restaurants_page'))


# Restaurants search results
@app.route('/restaurants', methods=['GET', 'POST'])
@app.route('/restaurants/<int:page>', methods=['GET', 'POST'])
def restaurants_page(page=0):
    conn = sqlite3.connect('data.db')
    c = conn.cursor()

    filter_selected = request.form.get('name') or \
                      request.form.get('cuisine') or \
                      request.form.get('suburb') or \
                      request.form.get('any') or \
                      request.form.get('cost-input-range') or \
                      request.form.get('rating-input-range')
    sort_selected = request.form.get('sort-rating') or request.args.get('sort-rating') or \
                    request.form.get('sort-cost') or request.args.get('sort-cost')

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
    elif filter_selected or sort_selected:  # Clicked on a filter or a sort
        if request.args.get('name') and request.form.get('name'):  # "Uncheck" name
            if request.args.get('name').lower() == request.form.get('name').lower():
                name = None
        else:
            name = request.args.get('name') or request.form.get('name')

        if request.args.get('cuisine') and request.form.get('cuisine'):  # "Uncheck" cuisine
            if request.args.get('cuisine').lower() == request.form.get('cuisine').lower():
                cuisine = None
        else:
            cuisine = request.args.get('cuisine') or request.form.get('cuisine')

        if request.args.get('suburb') and request.form.get('suburb'):  # "Uncheck" suburb
            if request.args.get('suburb').lower() == request.form.get('suburb').lower():
                suburb = None
        else:
            suburb = request.args.get('suburb') or request.form.get('suburb')

        sort_by = request.args.get('sort_by')
        if request.form.get('sort-rating'):
            sort_by = "rating"
        elif request.form.get('sort-cost'):
            sort_by = "cost"

        any = request.args.get('any') or request.form.get('any')
        max_cost = request.form.get('cost-input-range') or request.args.get('max_cost')
        min_rating = request.form.get('rating-input-range') or request.args.get('min_rating')

        return redirect(
            url_for('restaurants_page', name=name, cuisine=cuisine, suburb=suburb, any=any, max_cost=max_cost,
                    min_rating=min_rating, sort_by=sort_by))
    else:  # Display search results
        sort_by = request.args.get('sort_by')
        name = request.args.get('name')
        cuisine = request.args.get('cuisine')
        suburb = request.args.get('suburb')
        max_cost_filter = request.args.get('max_cost')
        min_rating_filter = request.args.get('min_rating') or 0
        any = request.args.get('any')

        if not sort_by:
            sort_by = "rating"

        restaurants = db_interface.get_restaurants(c)
        largest_cost = 0
        if restaurants:
            largest_cost = max(r.get_cost() for r in restaurants)

        if not max_cost_filter:  # No max_cost_filter specified, use default largest cost
            max_cost_filter = largest_cost

        if name or cuisine or suburb or max_cost_filter is not None or min_rating_filter is not None or any:  # Search
            restaurants = helpers_fff.filter_restaurants(restaurants, name=name, cuisine=cuisine,
                                                         max_cost=max_cost_filter,
                                                         suburb=suburb, min_rating=min_rating_filter, any_field=any,
                                                         sort_by=sort_by)

        suburbs = set(r.get_suburb() for r in restaurants)
        cuisines = set(r.get_cuisine() for r in restaurants)
        conn.close()

        # Pagination - display 10 per page
        start = page * 10
        end = (page + 1) * 10
        results = restaurants[start:end]
        num_pages = math.ceil(len(restaurants) / 10)  # Integer division

        return render_template('restaurants.html', name=name, cuisine=cuisine, suburb=suburb, restaurants=results,
                               suburbs=suburbs, cuisines=cuisines, largest_cost=largest_cost,
                               max_cost_filter=max_cost_filter, min_rating_filter=min_rating_filter, curr_page=page,
                               num_pages=num_pages, sort_by=sort_by)


# Submit new restaurant page
@app.route('/submit_restaurant', methods=['GET', 'POST'])
def submit_restaurant():
    # only display page if current user is an admin
    conn = sqlite3.connect('data.db')
    c = conn.cursor()
    is_admin = c.execute('SELECT admin FROM Users where username="%s"' % session['username']).fetchone()[0]
    if is_admin == 0:
        flash('You are not an administrator.')
        return render_template('home.html')

    if request.method == 'GET':
        return render_template('submit_restaurant.html', status='')
    else:
        name = request.form.get('name')
        suburb = request.form.get('suburb')
        address = request.form.get('address')
        postcode = request.form.get('postcode')
        phone = request.form.get('phone')
        hours = request.form.get('hours')
        cuisine = request.form.get('cuisine')
        owner = session['username']
        website = request.form.get('website')
        cost = request.form.get('cost')
        image = request.form.get('image')
        form_data = (name, suburb, address, postcode, phone, hours, cuisine, owner, website, cost, image)

        if not (name and suburb and address and postcode and cuisine and website and cost):
            err = 'Fields marked with (*) are required.'
            return render_new_restaurant_page(err, form_data)
        elif not re.match(r'^[0-9]{4}$', postcode):
            err = 'Postcode must contain 4 digits.'
            return render_new_restaurant_page(err, form_data)
        elif not re.match(r'^https?://.+$', website):
            err = 'Please provide a valid URL for your restaurant.'
            return render_new_restaurant_page(err, form_data)
        elif image and not re.match(r'^https?://.+$', image):
            err = 'Please provide a valid URL for a photo.'
            return render_new_restaurant_page(err, form_data)
        elif not re.match(r'^([0-9]+\.)?[0-9]+$', cost):
            err = 'The cost you entered is not valid.'
            return render_new_restaurant_page(err, form_data)
        elif phone and not (re.match(r'^[0-9\ \-\)\(]+$', phone) and len(re.sub('[^0-9]', '', phone)) >= 8):
            err = 'The phone number you entered is not valid.'
            return render_new_restaurant_page(err, form_data)
        else:
            conn = sqlite3.connect('data.db')
            c = conn.cursor()

            # use default data for unprovided fields
            if not image: image = 'http://nyburgerbar.com/wp-content/gallery/imagegallery/nyburger1.jpg'
            if not hours: hours = 'Not provided'
            if not phone: phone = 'Not provided'
            if phone != 'Not provided':
                phone = phone.replace('(', '').replace(')', '').replace('  ', ' ').replace('--', '-')
                phone = re.sub('[^0-9]+$', '', phone)
                phone = re.sub('^[^0-9]+', '', phone)

            # append suburb & postcode to address
            address = address.rstrip()
            address = address + ', ' + suburb
            address = address + ', ' + postcode

            flash('Restaurant has been added.')
            data = (name, suburb, address, postcode, phone, hours, cuisine, owner, website, cost, image)
            c.execute(
                '''INSERT INTO Restaurants (name, suburb, address, postcode, phone, hours, cuisine, owner, website, cost, image)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', data)
            rest_id = c.execute('SELECT MAX(id) FROM Restaurants').fetchone()[0]
            conn.commit()
            conn.close()
            return redirect(url_for('restaurant_page', rest_id=rest_id))


@app.route('/dashboard')
def dashboard():
    conn = sqlite3.connect('data.db')
    c = conn.cursor()
    admin_stats = db_interface.get_admin_stats(c)
    return render_template('dashboard.html', admin_stats=admin_stats)


# sends submit restaurant page with original form data
def render_new_restaurant_page(err, form_data):
    return render_template('submit_restaurant.html', status=err, name=form_data[0], suburb=form_data[1], address=form_data[2], postcode=form_data[3], phone=form_data[4], hours=form_data[5], cuisine=form_data[6], owner=form_data[7], website=form_data[8], cost=form_data[9], image=form_data[10])


# entry-point to admin tasks
@app.route('/reports', methods=['GET', 'POST'])
def view_reports():
    # only display page if current user is an admin
    conn = sqlite3.connect('data.db')
    c = conn.cursor()
    is_admin = c.execute('SELECT admin FROM Users where username="%s"' % session['username']).fetchone()[0]
    if is_admin == 0:
        flash('You are not an administrator.')
        return render_template('home.html')

    if request.method == 'GET':
        res = db_interface.get_reported(c)
        return render_template('reports.html', status='', reported=res)

    report_id = request.form.get('report_id')
    conn = sqlite3.connect('data.db')
    c = conn.cursor()

    if request.form.get('keep'):
        c.execute('UPDATE Reviews SET reported=0 where id="%s"' % report_id)
    elif request.form.get('delete'):
        c.execute('DELETE FROM Reviews WHERE id="%s"' % report_id)
        flash('Deleted review #%s' % report_id)

    conn.commit()
    conn.close()
    conn = sqlite3.connect('data.db')
    c = conn.cursor()
    res = db_interface.get_reported(c)
    conn.close()
    return render_template('reports.html', reported=res)


# Serve static files from static/
@app.route('/static/<path:path>')
def send_static_file(path):
    return send_from_directory('static', path)


if __name__ == '__main__':
    app.run(debug=True, use_reloader=True)
