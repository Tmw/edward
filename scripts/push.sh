set -e

push-edward(){
  # if DOCKER_REPO isn't passed in env variables, use default repo
  if [ -z "$DOCKER_REPO" ]; then
    DOCKER_REPO="$DEFAULT_DOCKER_REPO"
  fi

  if [ -n "$DOCKER_USERNAME" ] && [ -n "$DOCKER_PASSWORD" ]; then
    echo $DOCKER_PASSWORD | docker login -u $DOCKER_USERNAME --password-stdin
  else
    docker login
  fi

	docker push $DOCKER_REPO
}
