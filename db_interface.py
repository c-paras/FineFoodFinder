from classes import Restaurant


def add_user(c, full_name, username, password, email, confirm_id):
    c.execute('''INSERT INTO Users (full_name, username, password, email, status) VALUES (?, ?, ?, ?, ?)''', (full_name, username, password, email, confirm_id))


def check_login(c, username, password):
    """
    :param c: sqlite cursor
    :param username: username to be checked
    :param password: password to be checked
    :return: "inactive"/True/False
    """
    res = c.execute("SELECT * FROM Users WHERE username=? AND password=?", (username, password))
    if res.fetchone(): # Username and password correct
        res_status = c.execute("SELECT status FROM Users WHERE username=?", (username, ))
        status = res_status.fetchone()
        if status and status[0] != 'active':
            return 'inactive'
        return True  # Login succeeded
    return False  # Login failed


def check_username_exists(c, username):
    """
    :param c: sqlite cursor
    :param username: username to be checked
    :return: True/False
    """
    res = c.execute("SELECT * FROM Users WHERE username=?", (username, ))
    if res.fetchone():
        return True
    return False


def check_email_exists(c, email):
    """
    :param c: sqlite cursor
    :param email: email to be checked
    :return: True/False
    """
    res = c.execute("SELECT * FROM Users WHERE email=?", (email, ))
    if res.fetchone():
        return True
    return False


def confirm(c, user, uuid):
    """
    Confirms a user with a uuid. Returns False if user/uuid not found.
    :param c: sqlite cursor
    :param user: username to be checked
    :param uuid: uuid confirmation token
    :return: True/False
    """
    res = c.execute('SELECT * FROM Users WHERE username=? AND status=?', (user, uuid))
    if res.fetchone():
        c.execute('UPDATE Users SET status=? WHERE username=?', ('active', user))
        return True
    return False


def get_restaurants(c):
    results = []
    c.execute("SELECT * FROM Restaurants LIMIT 10") # TODO update limit
    for restaurant in c.fetchall():
        r = Restaurant(
            id=restaurant[0],
            name=restaurant[1],
            suburb=restaurant[2],
            address=restaurant[3],
            postcode=restaurant[4],
            phone=restaurant[5],
            hours=restaurant[6],
            cuisine=restaurant[7],
            owner=restaurant[8],
            website=restaurant[9],
            cost=restaurant[10],
            image=restaurant[11],
            rating=find_average_rating(c, restaurant[0])
        )
        results.append(r)
    return results


def search_restaurants(c, criteria="", search_term="", search_term2=""):
    """
    Search for restaurants by specified criteria.

    Text searches: returns restaurants where search_term in lowercase characters is found in the required field
    Number searches (rating, cost etc.): returns restaurants where (search_term <= field <= search_term2)

    search_term2 is only used for number searches.
    """
    results = []
    restaurants = get_restaurants(c)
    for r in restaurants:
        search_all_fields = [r.get_name(), r.get_cuisine(), r.get_suburb()]
        any_search = False

        if criteria == "any":
            for field in search_all_fields:
                if search_term.lower() in field.lower():
                    any_search = True
                    break
        name_search    = criteria == "name"    and search_term.lower() in r.get_name().lower()
        cuisine_search = criteria == "cuisine" and search_term.lower() in r.get_cuisine().lower()
        cost_search    = criteria == "cost"    and search_term <= r.get_cost() <= search_term2
        suburb_search  = criteria == "suburb"  and search_term.lower() in r.get_suburb().lower()
        rating_search  = criteria == "rating"  and search_term <= r.get_rating() <= search_term2

        if any_search or name_search or cuisine_search or cost_search or suburb_search or rating_search:
            results.append(r)
    return results


def get_restaurant_by_id(c, id):
    c.execute("""SELECT * FROM Restaurants WHERE ID=?""", (id, ))
    res = c.fetchone()
    if res:
        r = Restaurant(
            id=res[0],
            name=res[1],
            suburb=res[2],
            address=res[3],
            postcode=res[4],
            phone=res[5],
            hours=res[6],
            cuisine=res[7],
            owner=res[8],
            website=res[9],
            cost=res[10],
            image=res[11],
            rating=find_average_rating(c, res[0])
        )
        return r


def add_rating(c, restaurant_id, username, rating):
    """
    :param c: sqlite cursor
    :param restaurant_id: ID of the restaurant being rated
    :param username: Username of the user adding the rating
    :param rating: Rating (float)
    :return: True/False, depending on whether the action succeeded
    """
    if check_username_exists(c, username):
        c.execute("""INSERT INTO Ratings (user, restaurant, rating) VALUES (?, ?, ?)""", (username, restaurant_id, rating))
        return True
    return False


def already_rated_restaurant(c, restaurant_id, username):
    res = c.execute("SELECT * FROM Ratings WHERE restaurant=? AND user=?", (restaurant_id, username))
    if res.fetchone():
        return True
    return False


# Calculates average rating based on all user ratings for id
def find_average_rating(c, i):
    ratings = c.execute("SELECT rating FROM Ratings WHERE restaurant=?", (i, )).fetchall()
    sum = 0
    num = 0
    for rating in ratings:
        sum += rating[0]
        num += 1
    if num == 0:
        return 'Unrated'
    else:
        return round(sum/num , 1)
