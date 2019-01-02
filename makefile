test:
	python -m unittest discover -s tests

run:
	source .env && python main.py
