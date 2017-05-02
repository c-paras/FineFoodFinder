def filter_restaurants(restaurants, name="", cuisine="", cost="", suburb="", rating=""):
    if name:
        restaurants = [r for r in restaurants if name.lower() in r.get_name().lower()]
    if cuisine:
        restaurants = [r for r in restaurants if cuisine.lower() in r.get_cuisine().lower()]
    if suburb:
        restaurants = [r for r in restaurants if suburb.lower() in r.get_suburb().lower()]
    return restaurants
