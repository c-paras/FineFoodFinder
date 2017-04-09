#!/usr/bin/python
#Written by Costa Paraskevopoulos in April 2017
#Generates a mock database for the Fine Food Finder

#Requires the following files to be present in the current directory:
#names.txt - http://listofrandomnames.com/
#emails.txt - https://www.randomlists.com/email-addresses

from __future__ import print_function
import sqlite3, sys, random, os, re, glob

def main():
	db = sqlite3.connect("../data.db")
	db.text_factory = str
	c = db.cursor()
	c.execute("PRAGMA foreign_keys = ON")

	#generates and populates database tables
	tables = ['Restaurants', 'Users']
	drop_tables(c, tables)
	create_tables(c)
	populate_tables(c)

	db.commit()
	db.close()

#drops all old tables if they exist
def drop_tables(c, tables):
	for table in tables:
		print('Dropping %s table...' %table)
		try:
			c.execute('DROP TABLE ' + table)
		except sqlite3.OperationalError:
			pass

#creates fresh tables
def create_tables(c):

	print('Creating Users table...')
	c.execute(
		'''CREATE TABLE Users (
				full_name	TEXT not null,
				username		TEXT not null unique,
				password		TEXT not null,
				email			TEXT not null unique check (email like '_%@_%'),
				PRIMARY KEY (username)
			);''')

	print('Creating Restaurants table...')
	c.execute(
		'''CREATE TABLE Restaurants (
				id			INTEGER not null unique,
				name		TEXT not null,
				suburb	TEXT not null,
				address	TEXT not null,
				phone		TEXT,
				hours		TEXT, -- business hours
				cuisine	TEXT not null,
				owner		TEXT,
				rating	FLOAT, -- can be unrated
				website	TEXT check (website like 'http%://%'),
				cost		FLOAT, -- average cost
				PRIMARY KEY (id),
				FOREIGN KEY (owner) REFERENCES Users(username)
			);''')

#populates fresh tables with mock data
def populate_tables(c):
	populate_users(c)
	populate_restaurants(c)

#populates users table with random name & email
#username created based on first name
#uses simple-to-use passwords for testing purposes
def populate_users(c):
	print('Populating Users table...')

	required = ['names.txt', 'emails.txt']
	for f in required:
		if not (os.access(f, os.R_OK) and os.path.isfile(f)):
			print("Error: cannot access raw data file '%s'" %f, file=sys.stderr)
			sys.exit(1)

	names = open('names.txt').readlines()
	emails = open('emails.txt').readlines()
	passwords = ['qwerty', '1111', 'zzz', 'abc', 'hello', '555', 'qqq', 'ppp']

	for name in names:
		full_name = name.rstrip()
		username = full_name.split(' ')[0].lower() + str(random.randint(10, 99)) #first name + 2 digits
		password = passwords[random.randint(0, len(passwords) - 1)]
		email = emails.pop().strip()
		data = (full_name, username, password, email)
		c.execute('''INSERT INTO Users (full_name, username, password, email)
				VALUES (?, ?, ?, ?)''', data)

#populates restaurants table
def populate_restaurants(c):
	print('Populating Restaurants table...')

	if not (os.access('restaurants', os.R_OK) and os.path.isdir('restaurants')):
		print("Error: cannot access raw data directory 'restaurants'", file=sys.stderr)
		sys.exit(1)

	users = c.execute('SELECT username FROM Users').fetchall()
	num_users = c.execute('SELECT COUNT(*) FROM Users').fetchone()[0]

	i = 0
	for restaurant in glob.glob('restaurants/*'):
		i += 1
		r = open(restaurant).readlines()

		#extract info from file
		try:
			name = r[0].strip()
			address = r[1].strip()
			suburb = re.match(r'.*, (.+), Sydney', r[1]).group(1)
			phone = r[2].strip()
			if re.match('Not available', phone):
				phone = 'Not available'
			hours = r[3].strip()
			cuisine = r[4].strip()
			cost = r[5].strip()
		except:
			print("Error: skipping '%s'" %restaurant, file=sys.stderr)
			continue

		#uses a ficticious rating between 0 and 5
		int_part = str(random.randint(1, 4))
		decimal_part = str(random.randint(1, 9))
		rating = float(int_part + '.' + decimal_part)

		#choses a random protocol for the website
		protocol = 'http://'
		if random.randint(0, 1) == 1:
			protocol = 'https://'

		#makes site of the form protocol://lowercase.name.of.restaurant.fake.com
		website = protocol + name.replace(' ', '.').lower().strip() + '.fake.com'

		#ensures only some restaurants have owners
		owner = None
		if random.randint(0, 3) == 0:
			owner = users[random.randint(0, num_users - 1)][0]

		data = (i, name, suburb, address, phone, hours, cuisine, owner, rating, website, cost)
		c.execute('''INSERT INTO Restaurants
				(id, name, suburb, address, phone, hours, cuisine, owner, rating, website, cost)
				VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', data)

if __name__ == '__main__':
	main()
