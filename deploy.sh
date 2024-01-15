#!/bin/bash

compose_file="docker-compose-prod.yml"

while [[ "$#" -gt 0 ]]; do
  case $1 in
    -dev)
      compose_file="docker-compose-dev.yml"
      ;;
    *)
      echo "Unknown option: $1"
      exit 1
      ;;
  esac
  shift
done

docker compose -f $compose_file down
docker rm oh nginx
docker rmi $(docker images -q)
docker compose -f $compose_file up --build -d
