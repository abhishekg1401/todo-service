# todo-service

This projects creates a Todo application where you can add your tasks and also download the tasks as well. Most importantly the data will be persistant.
The application is running on docker container and is been orchrestrated by Kubernetes using KIND.

# Run Docker Container

chmod +x setup.sh
./setup.sh

Open:

http://localhost:8080
http://localhost:8080/todos
http://localhost:8080/health

# Run the application with K8s and Kind Cluster

kind create cluster --name todo-cluster --config kind-config.yaml
kind load docker-image todo-service:v1 --name todo-cluster
kubectl apply -f k8s/

Check:

http://localhost:30080
http://localhost:30080/todos
http://localhost:30080/health

For port forwarding if 'kind-config' is not applied:

kubectl port-forward service/todo-service 8080:8080

Then application will run on port 8080

# Rebuilding after any code change

docker build -t todo-service:<version no> .
kind load docker-image todo-service:<version no> --name todo-cluster

Change the <version no> in Deployment.yaml

kubectl apply -f k8s/deployment.yaml /
kubectl rollout restart deployment todo-deployment

Check:

http://localhost:30080 /
http://localhost:30080/todos /
http://localhost:30080/health

Run and Enjoy.