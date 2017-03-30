#!/usr/bin/env python3
"""
Database generation script for FFF
Drops all tables then re-creates them.
"""

import sqlite3

def drop_tables(c):
    """Attempts to drop all tables (users)."""
    try:
        c.execute('DROP TABLE users')
    except sqlite3.OperationalError:  # Table doesn't exist
        pass


def create_tables(c):
    """Creates the users tables."""
    c.execute('''CREATE TABLE users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        password TEXT,
        email TEXT
    )''')

if __name__ == '__main__':
    conn = sqlite3.connect("fff.db")
    c = conn.cursor()

    print('Dropping old tables...')
    drop_tables(c)
    print('Creating new tables...')
    create_tables(c)

    conn.commit()
    conn.close()
