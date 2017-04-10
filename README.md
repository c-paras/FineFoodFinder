# FineFoodFinder
A platform for locating eateries of varying expense, cuisine and location

# Running things
Installing dependencies (first run)
-----------------------------------

    make init
    
    # Or (make not installed)
    pip install -r requirements.txt

Starting the server (assuming Python 3)
---------------------------------------
 
    # Most reliable
    python fff.py
    
    # Or (if you have make installed - Linux/Mac)
    make start
    
    # Or
    ./fff.py

Then navigate to [http://localhost:5000](http://localhost:5000)
    
Running unit tests:
-------------------

    make test
    
    # Or (make not installed)
    python -m unittest

# Project Structure
* `data_generation/`: Database and mock data generation scripts
* `static/`: Our custom CSS/fonts/images (background etc.) go here
* `static/vendor/`: Libraries we're using (Bootstrap, jQuery etc.)
* `templates/`: Template files for use with Jinja2
* `tests/`: Python unit tests