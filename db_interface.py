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
