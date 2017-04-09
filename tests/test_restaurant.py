from classes import Restaurant
import unittest


class TestRestaurantMethods(unittest.TestCase):
    def test_constructor(self):
        # No optional arguments
        r = Restaurant(0, "restaurant1", "kensington", "12 anzac parade", "pizza", "john smith")
        self.assertEqual(r.get_id(), 0)
        self.assertEqual(r.get_name(), "restaurant1")
        self.assertEqual(r.get_suburb(), "kensington")
        self.assertEqual(r.get_address(), "12 anzac parade")
        self.assertEqual(r.get_cuisine(), "pizza")
        self.assertEqual(r.get_owner(), "john smith")

        # All optional arguments
        r = Restaurant(0, "restaurant1", "kensington", "12 anzac parade", "pizza", "john smith",
                       phone="1234 5678", hours="8am-10pm", rating=3.5,
                       website="https://restaurant1.com", cost=10.5)
        self.assertEqual(r.get_id(), 0)
        self.assertEqual(r.get_name(), "restaurant1")
        self.assertEqual(r.get_suburb(), "kensington")
        self.assertEqual(r.get_address(), "12 anzac parade")
        self.assertEqual(r.get_cuisine(), "pizza")
        self.assertEqual(r.get_owner(), "john smith")
        self.assertEqual(r.get_phone(), "1234 5678")
        self.assertEqual(r.get_hours(), "8am-10pm")
        self.assertEqual(r.get_rating(), 3.5)
        self.assertEqual(r.get_website(), "https://restaurant1.com")
        self.assertEqual(r.get_cost(), 10.5)

    def test_set_name(self):
        r = Restaurant(0, "restaurant1", "kensington", "12 anzac parade", "pizza", "john smith")
        r.set_name("restaurant2")
        self.assertEqual(r.get_name(), "restaurant2")

    def test_set_suburb(self):
        r = Restaurant(0, "restaurant1", "kensington", "12 anzac parade", "pizza", "john smith")
        r.set_suburb("kingsford")
        self.assertEqual(r.get_suburb(), "kingsford")

    def test_set_address(self):
        r = Restaurant(0, "restaurant1", "kensington", "12 anzac parade", "pizza", "john smith")
        r.set_address("13 anzac pde")
        self.assertEqual(r.get_address(), "13 anzac pde")

    def test_set_cuisine(self):
        r = Restaurant(0, "restaurant1", "kensington", "12 anzac parade", "pizza", "john smith")
        r.set_cuisine("italian")
        self.assertEqual(r.get_cuisine(), "italian")

    def test_set_owner(self):
        r = Restaurant(0, "restaurant1", "kensington", "12 anzac parade", "pizza", "john smith")
        r.set_owner("bob smith")
        self.assertEqual(r.get_owner(), "bob smith")

    def test_set_phone(self):
        r = Restaurant(0, "restaurant1", "kensington", "12 anzac parade", "pizza", "john smith")
        r.set_phone("0000 0000")
        self.assertEqual(r.get_phone(), "0000 0000")

    def test_set_hours(self):
        r = Restaurant(0, "restaurant1", "kensington", "12 anzac parade", "pizza", "john smith")
        r.set_hours("7am-5pm")
        self.assertEqual(r.get_hours(), "7am-5pm")

    def test_set_rating(self):
        r = Restaurant(0, "restaurant1", "kensington", "12 anzac parade", "pizza", "john smith")
        r.set_rating(4.5)
        self.assertEqual(r.get_rating(), 4.5)

    def test_set_website(self):
        r = Restaurant(0, "restaurant1", "kensington", "12 anzac parade", "pizza", "john smith")
        r.set_website("https://www.google.com")
        self.assertEqual(r.get_website(), "https://www.google.com")

    def test_set_cost(self):
        r = Restaurant(0, "restaurant1", "kensington", "12 anzac parade", "pizza", "john smith")
        r.set_cost(13.25)
        self.assertEqual(r.get_cost(), 13.25)