test:
	python -m unittest discover -s tests

run:
	source .env && python main.py

build:
	git lfs pull
	ls -la ./tfmodel
	# docker build -t tiemenwaterreus/edward .
