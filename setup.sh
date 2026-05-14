#!/bin/bash

echo "Building Docker image..."

docker build -t todo-service:latest .

docker stop todo-service 2>/dev/null || true
docker rm todo-service 2>/dev/null || true

docker run -d \
  --name todo-service \
  -p 8080:8080 \
  todo-service:latest

echo "Todo service is running at:"
echo "http://localhost:8080"
echo "http://localhost:8080/todos"