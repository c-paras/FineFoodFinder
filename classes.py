class Restaurant():
    # Constructor
    def __init__(self, id, name, suburb, address, cuisine, owner, phone='', hours='', rating=0, website='', cost=0):
        self.id = id
        self.name = name
        self.suburb = suburb
        self.address = address
        self.cuisine = cuisine
        self.owner = owner
        self.phone = phone
        self.hours = hours
        self.rating = rating
        self.website = website
        self.cost = cost

    # String representation
    def __repr__(self):
        output = 'Restaurant {\n' + \
            '\tid: {}\n'.format(self.id) + \
            '\tname: {}\n'.format(self.name) + \
            '\tsuburb: {}\n'.format(self.suburb) + \
            '\taddress: {}\n'.format(self.address) + \
            '\tcuisine: {}\n'.format(self.cuisine) + \
            '\towner: {}\n'.format(self.owner) + \
            '\tphone: {}\n'.format(self.phone) + \
            '\thours: {}\n'.format(self.hours) + \
            '\trating: {}\n'.format(self.rating) + \
            '\twebsite: {}\n'.format(self.website) + \
            '\tcost: {}\n'.format(self.cost) + \
            '}'
        return output

    # Getters and setters
    def get_id(self):  # Does not require setter
        return self.id

    def get_name(self):
        return self.name

    def set_name(self, name):
        self.name = name

    def get_suburb(self):
        return self.suburb

    def set_suburb(self, suburb):
        self.suburb = suburb

    def get_address(self):
        return self.address

    def set_address(self, address):
        self.address = address

    def get_cuisine(self):
        return self.cuisine

    def set_cuisine(self, cuisine):
        self.cuisine = cuisine

    def get_owner(self):
        return self.owner

    def set_owner(self, owner):
        self.owner = owner

    def get_phone(self):
        return self.phone

    def set_phone(self, phone):
        self.phone = phone

    def get_hours(self):
        return self.hours

    def set_hours(self, hours):
        self.hours = hours

    def get_rating(self):
        return self.rating

    def set_rating(self, rating):
        self.rating = rating

    def get_website(self):
        return self.website

    def set_website(self, website):
        self.website = website

    def get_cost(self):
        return self.cost

    def set_cost(self, cost):
        self.cost = cost


class User():
    # Constructor
    def __init__(self, username, password, email):
        self.username = username
        self.password = password
        self.email = email

    def __repr__(self):
        output = 'User {\n' + \
            '\tusername: {}\n'.format(self.username) + \
            '\tpassword: {}\n'.format(self.password) + \
            '\temail: {}\n'.format(self.email) + \
            '}'
        return output

    # Getters and setters
    def get_username(self):
        return self.username

    def set_username(self, username):
        self.username = username

    def get_password(self):
        return self.password

    def set_password(self, password):
        self.password = password

    def get_email(self):
        return self.email

    def set_email(self, email):
        self.email = email
