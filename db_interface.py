from classes import Restaurant


def get_restaurants(c):
    results = []
    c.execute("SELECT * FROM Restaurants LIMIT 10")  # TODO update limit
    for restaurant in c.fetchall():
        r = Restaurant(
            id=restaurant[0],
            name=restaurant[1],
            suburb=restaurant[2],
            address=restaurant[3],
            phone=restaurant[4],
            hours=restaurant[5],
            cuisine=restaurant[6],
            owner=restaurant[7],
            rating=restaurant[8],
            website=restaurant[9],
            cost=restaurant[10]
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
        name_search     = criteria == "name"    and search_term.lower() in r.get_name().lower()
        cuisine_search  = criteria == "cuisine" and search_term.lower() in r.get_cuisine().lower()
        cost_search     = criteria == "cost"    and search_term <= r.get_cost() <= search_term2
        suburb_search   = criteria == "suburb"  and search_term.lower() in r.get_suburb().lower()
        rating_search   = criteria == "rating"  and search_term <= r.get_rating() <= search_term2

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
            phone=res[4],
            hours=res[5],
            cuisine=res[6],
            owner=res[7],
            rating=res[8],
            website=res[9],
            cost=res[10]
        )
        return r
