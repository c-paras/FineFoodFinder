from classes import User
import unittest


class TestRestaurantMethods(unittest.TestCase):
    def test_constructor(self):
        # No optional arguments
        u = User("user1", "password1", "john@example.com")
        self.assertEqual(u.get_username(), "user1")
        self.assertEqual(u.get_password(), "password1")
        self.assertEqual(u.get_email(), "john@example.com")

    def test_set_username(self):
        u = User("user1", "password1", "john@example.com")
        u.set_username("bob")
        self.assertEqual(u.get_username(), "bob")

    def test_set_password(self):
        u = User("user1", "password1", "john@example.com")
        u.set_password("password2")
        self.assertEqual(u.get_password(), "password2")

    def test_set_email(self):
        u = User("user1", "password1", "john@example.com")
        u.set_email("bob@email.com")
        self.assertEqual(u.get_email(), "bob@email.com")
