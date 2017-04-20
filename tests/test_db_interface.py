import unittest
import sqlite3
import db_interface


class TestDbInterface(unittest.TestCase):
    def test_search_restaurants(self):
        conn = sqlite3.connect('data.db')
        c = conn.cursor()
        all_restaurants = db_interface.get_restaurants(c)

        search_1 = db_interface.search_restaurants(c, criteria="name", search_term="")
        self.assertListEqual(search_1, all_restaurants)

        search_2 = db_interface.search_restaurants(c, criteria="name", search_term="the")
        expected_2 = [r for r in all_restaurants if "the" in r.get_name().lower()]
        self.assertListEqual(search_2, expected_2)

        search_3 = db_interface.search_restaurants(c, criteria="cost", search_term=10, search_term2=30)
        expected_3 = [r for r in all_restaurants if 10 <= r.get_cost() <= 30]
        self.assertListEqual(search_3, expected_3)

        search_4 = db_interface.search_restaurants(c, criteria="suburb", search_term="Surry Hills")
        expected_4 = [r for r in all_restaurants if "Surry Hills" in r.get_suburb()]
        self.assertListEqual(search_4, expected_4)

        search_5 = db_interface.search_restaurants(c, criteria="rating", search_term=2, search_term2=4)
        expected_5 = [r for r in all_restaurants if 2 <= r.get_rating() <= 4]
        self.assertListEqual(search_5, expected_5)