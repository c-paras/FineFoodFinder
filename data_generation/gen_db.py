#!/usr/bin/python
#Written by Costa Paraskevopoulos in April 2017
#Generates a mock database for the Fine Food Finder

#Requires the following to be present in the current directory:
#names.txt - http://listofrandomnames.com/
#emails.txt - https://www.randomlists.com/email-addresses
#suburbs.txt - Andrew Taylor
#restaurants - generated by scrape_zomato.pl

import sqlite3, sys, random, os, re, glob, urllib, datetime
from HTMLParser import HTMLParser

def main():
	db = sqlite3.connect("../data.db")
	db.text_factory = str
	c = db.cursor()
	c.execute("PRAGMA foreign_keys = ON")

	#generate and populate database tables
	tables = ['Reviews', 'Ratings', 'Restaurants', 'Users']
	drop_tables(c, tables)
	create_tables(c)
	populate_tables(c)

	db.commit()
	db.close()

#drops all old tables if they exist
def drop_tables(c, tables):
	for table in tables:
		print 'Dropping %s table...' %table
		try:
			c.execute('DROP TABLE ' + table)
		except sqlite3.OperationalError:
			pass

#creates fresh tables
def create_tables(c):

	print 'Creating Users table...'
	c.execute(
		'''CREATE TABLE Users (
				full_name	TEXT not null,
				username		TEXT not null unique,
				password		TEXT not null,
				email			TEXT not null unique check (email like '_%@_%'),
				status      TEXT not null,
				admin			INTEGRER not null check (admin == 0 || admin == 1),
				PRIMARY KEY (username)
			);''')

	print 'Creating Restaurants table...'
	c.execute(
		'''CREATE TABLE Restaurants (
				id			INTEGER not null unique,
				name		TEXT not null,
				suburb	TEXT not null,
				address	TEXT not null,
				postcode INTEGER not null,
				phone		TEXT,
				hours		TEXT, -- business hours; varying format
				cuisine	TEXT not null,
				owner		TEXT,
				website	TEXT not null check (website like 'http%://_%'),
				cost		FLOAT not null, -- average cost per person
				image		TEXT check (image like 'http%://_%'),
				PRIMARY KEY (id),
				FOREIGN KEY (owner) REFERENCES Users(username)
			);''')

	print 'Creating Ratings table...'
	c.execute(
		'''CREATE TABLE Ratings (
				user			TEXT not null,
				restaurant	INTEGER not null,
				rating		FLOAT not null,
				PRIMARY KEY (user, restaurant), -- one rating per user per restaurant
				FOREIGN KEY (user) REFERENCES Users(username),
				FOREIGN KEY (restaurant) REFERENCES Restaurants(id)
		);''')

	print 'Creating Reviews table...'
	c.execute(
		'''CREATE TABLE Reviews (
				id				INTEGER unique not null,
				user			TEXT not null,
				restaurant	INTEGER not null,
				review		TEXT not null,
				timestamp	DATE not null,
				reported		INTEGER not null check (reported == 0 || reported == 1),
				PRIMARY KEY (user, restaurant), -- one review per user per restaurant
				FOREIGN KEY (user) REFERENCES Users(username),
				FOREIGN KEY (restaurant) REFERENCES Restaurants(id)
	);''')

#populates fresh tables with mock data
def populate_tables(c):
	populate_users(c)
	populate_restaurants(c)
	populate_ratings(c)
	populate_reviews(c)

#populates users table with random name & email
#username created based on first name
#uses simple-to-use passwords for testing purposes
def populate_users(c):
	print 'Populating Users table...'

	required = ['names.txt', 'emails.txt']
	for f in required:
		if not (os.access(f, os.R_OK) and os.path.isfile(f)):
			print >>sys.stderr, "Error: cannot access raw data file '%s'" %f
			sys.exit(1)

	names = open('names.txt').readlines()
	emails = open('emails.txt').readlines() #there are plenty more emails than names
	passwords = ['qwerty', '1111', 'zzz', 'abc', 'hello', '555', 'qqq', 'ppp']

	for name in names:
		full_name = name.rstrip()
		username = full_name.split(' ')[0].lower() + str(random.randint(10, 99)) #first name + 2 digits
		password = passwords[random.randint(0, len(passwords) - 1)]
		email = emails.pop().strip()
		data = (full_name, username, password, email, 'active', 0)
		c.execute('''INSERT INTO Users (full_name, username, password, email, status, admin)
				VALUES (?, ?, ?, ?, ?, ?)''', data)

	#hard-code all contributors as admin users
	contributors = ['Costa Paraskevopoulos', 'Dominic Fung', 'Victor Zhang', 'Joseph Yeoh', 'Heng Fu Xiu']
	for full_name in contributors:
		username = full_name.lower().split(' ')[0] + '22' #lowercase first-name + '22'
		password = 'iluvfood' #use the same password for all admins
		email = emails.pop().strip()
		data = (full_name, username, password, email, 'active', 1)
		c.execute('''INSERT INTO Users (full_name, username, password, email, status, admin)
				VALUES (?, ?, ?, ?, ?, ?)''', data)

#populates restaurants table
def populate_restaurants(c):
	print 'Populating Restaurants table...'

	if not (os.access('restaurants', os.R_OK) and os.path.isdir('restaurants')):
		print >>sys.stderr, "Error: cannot access raw data directory 'restaurants'"
		sys.exit(1)

	if not (os.access('suburbs.txt', os.R_OK) and os.path.isfile('suburbs.txt')):
		print >>sys.stderr, "Error: cannot access raw data file 'suburbs.txt'"
		sys.exit(1)

	#get postcodes from file and cache in dict
	suburbs = open('suburbs.txt').readlines()
	postcodes = {}
	for suburb in suburbs:
		lat, lng, pst, sub = suburb.strip().split('\t')
		postcodes[sub] = pst
	postcodes['CBD'] = 2000 #special case not in data file

	users = c.execute('SELECT username FROM Users').fetchall()
	num_users = c.execute('SELECT COUNT(*) FROM Users').fetchone()[0]

	i = 0
	for restaurant in glob.glob('restaurants/*'):
		r = open(restaurant).readlines()

		#extract info from file
		try:
			name = r[0].strip()
			name = HTMLParser().unescape(name)
			address = r[1].strip()
			address = HTMLParser().unescape(address)
			address = re.sub(r'nsw', 'NSW', address, flags=re.I)
			if not address.endswith(', NSW'):
				address = address + ', NSW'
			suburb = re.match(r'.*, (.+), Sydney', r[1]).group(1)
			suburb = HTMLParser().unescape(suburb)
			phone = r[2].strip().replace('(', '').replace(')', '')
			if re.match('Not available', phone):
				phone = 'Not provided'
			hours = r[3].strip()
			hours = re.sub(r'\s*,\s*', ', ', hours)
			cuisine = r[4].strip()
			cost = r[5].strip()
			image = r[6].strip()
		except:
			print >>sys.stderr, "Error: skipping '%s'" %restaurant
			continue

		#lookup postcode using suburb
		postcode = ''
		if not suburb in postcodes:
			continue
		else:
			postcode = postcodes[suburb]

		#and append it to the address
		address = address + ' ' + str(postcode)

		#chose a random protocol for the website
		protocol = 'http://'
		if random.randint(0, 1) == 1:
			protocol = 'https://'

		#make site of the form protocol://www.lowercase.name.of.restaurant.fake.com
		website = name.replace('  ', ' ').replace(' ', '.').replace('-', '').strip() + '.fake.com'
		website = HTMLParser().unescape(website)
		website = urllib.quote(website) #encode as url
		website = protocol + 'www.' + website #avoid encoding the protocol
		website = website.lower().replace('..', '.')

		#ensure only some restaurants have owners
		owner = None
		if random.randint(0, 3) == 0:
			owner = users[random.randint(0, num_users - 1)][0]

		i += 1
		data = (i, name, suburb, address, postcode, phone, hours, cuisine, owner, website, cost, image)
		c.execute('''INSERT INTO Restaurants
				(id, name, suburb, address, postcode, phone, hours, cuisine, owner, website, cost, image)
				VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', data)

#populates ratings table
def populate_ratings(c):
	print 'Populating Ratings table...'

	users = c.execute('SELECT username FROM Users').fetchall()
	num_users = c.execute('SELECT COUNT(*) FROM Users').fetchone()[0]
	restaurants = c.execute('SELECT id FROM Restaurants').fetchall()
	num_restaurants = c.execute('SELECT COUNT(*) FROM Restaurants').fetchone()[0]

	#add 1000 random ratings by 1000 random users to 1000 random restaurants
	#assumes there is enough data in users and restaurants tables
	i = 0
	while i < 1000:
		user = users[random.randint(0, num_users - 1)][0]
		restaurant = restaurants[random.randint(0, num_restaurants - 1)][0]

		#use a ficticious rating between 1 and 5
		int_part = str(random.randint(1, 4))
		decimal_part = str(random.randint(1, 9))
		rating = float(int_part + '.' + decimal_part)

		data = (user, restaurant, rating)
		try:
			c.execute('''INSERT INTO Ratings (user, restaurant, rating) VALUES (?, ?, ?)''', data)
			i += 1
		except:
			pass #skip this since only one rating per user per restaurant

#populates reviews table
def populate_reviews(c):
	print 'Populating Reviews table...'

	users = c.execute('SELECT username FROM Users').fetchall()
	num_users = c.execute('SELECT COUNT(*) FROM Users').fetchone()[0]
	restaurants = c.execute('SELECT id FROM Restaurants').fetchall()
	num_restaurants = c.execute('SELECT COUNT(*) FROM Restaurants').fetchone()[0]
	phrases = {
		'food': ['Food was great. ', 'The food was quite bland. ', 'I really liked the dishes here. ', 'The food sucks. '],
		'atmosphere': ['The atmosphere was great. ', 'This place was super boring. ', 'The restaurant was really nicely decorated. '],
		'staff': ['The staff were quite friendly. ', 'The waiters were very rude. ', 'The staff here shouldn\'t work in the service industry. '],
		'overall': ['I would come here again. ', 'This is my favourite restaurant. ', 'I would not recommend this place. ']
	}

	#add 1000 random reviews by 1000 random users to 1000 random restaurants
	#assumes there is enough data in users and restaurants tables
	i = 1
	while i < 1000:
		user = users[random.randint(0, num_users - 1)][0]
		restaurant = restaurants[random.randint(0, num_restaurants - 1)][0]
		food = random.randint(0, len(phrases['food']) - 1)
		atmos = random.randint(0, len(phrases['atmosphere']) - 1)
		staff = random.randint(0, len(phrases['staff']) - 1)
		overall = random.randint(0, len(phrases['overall']) - 1)
		review = phrases['food'][food] + phrases['atmosphere'][atmos] + phrases['staff'][staff] + phrases['overall'][overall]
		data = (i, user, restaurant, review, datetime.datetime.now(), 0)

		try:
			c.execute('''INSERT INTO Reviews (id, user, restaurant, review, timestamp, reported) VALUES (?, ?, ?, ?, ?, ?)''', data)
			i += 1
		except:
			pass #skip this since only one review per user per restaurant

if __name__ == '__main__':
	main()
