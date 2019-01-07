DOCKER_REPO="tiemenwaterreus/edward"

test:
	python -m unittest discover -s tests

run:
	source .env && python main.py

build:
	git lfs pull
	docker build -t $(DOCKER_REPO) .

push:
	echo "$DOCKER_PASSWORD" | docker login -u "$DOCKER_USERNAME" --password-stdin
	docker push $(DOCKER_REPO)
