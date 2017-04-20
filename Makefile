init: # Install dependencies via pip
	pip install -r requirements.txt

database: # Run database generation script
	cd data_generation && python gen_db.py

database3: # Converts database generation script to py3, runs it, then resets to original
	cd data_generation && 2to3 -w -n gen_db.py && python gen_db.py && git checkout gen_db.py

test: # Run unit tests
	python -m unittest 

start:
	python fff.py
