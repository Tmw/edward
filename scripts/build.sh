build-edward(){
  git lfs pull

  # if DOCKER_REPO isn't passed in env variables, use default repo
  if [ -z "$DOCKER_REPO" ]; then
    DOCKER_REPO="$DEFAULT_DOCKER_REPO"
  fi

	docker build -t $DOCKER_REPO .
}
