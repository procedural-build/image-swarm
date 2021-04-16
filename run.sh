case "$1" in
  build)
    docker build --target=production -t image-swarm:latest .
    ;;
  build-dev)
    docker build -t image-swarm:dev .
    ;;
  test)
    docker run --rm -i \
    -v $HOST_SRC_PATH:/data \
     image-swarm:dev python -m pytest test/ --junit-xml=/data/test-results.xml
    ;;
  *)
  echo $"Usage: $0 {build | build-dev | test }"
  exit 1
  ;;

esac