init: # Install dependencies via pip
	pip install -r requirements.txt

database: # Run database generation script
	cd data_generation; python gen_db.py

test: # Run unit tests
	python -m unittest 

start:
	python fff.py
