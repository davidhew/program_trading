#/bin/bash

git pull
docker stop stock_analyzer
docker-compose up -d
docker logs -f stock_analyzer