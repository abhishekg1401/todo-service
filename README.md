# Todo Service

A simple Todo application built with Node.js, Docker, and Kubernetes.  
This application allows users to:

- Add and manage tasks
- Download tasks
- Store data persistently
- Run the application using Docker containers
- Orchestrate containers using Kubernetes with KIND

---

# Features

- Persistent storage support
- Dockerized application
- Kubernetes deployment support
- KIND cluster integration
- Health check endpoint
- Todo management API

---

# Run with Docker

Make the setup script executable:

```bash
chmod +x setup.sh
```

Run the application:

```bash
./setup.sh
```

Open the application in your browser:

```text
http://localhost:8080
http://localhost:8080/todos
http://localhost:8080/health
```

---

# Run with Kubernetes and KIND

## Create KIND Cluster

```bash
kind create cluster --name todo-cluster --config kind-config.yaml
```

## Load Docker Image into KIND

```bash
kind load docker-image todo-service:v1 --name todo-cluster
```

## Deploy Kubernetes Resources

```bash
kubectl apply -f k8s/
```

## Access the Application

```text
http://localhost:30080
http://localhost:30080/todos
http://localhost:30080/health
```

---

# Port Forwarding (Optional)

If `kind-config.yaml` is not configured for port mapping, use port forwarding:

```bash
kubectl port-forward service/todo-service 8080:8080
```

Then access the application on:

```text
http://localhost:8080
```

---

# Rebuild After Code Changes

## Rebuild Docker Image

Replace `<version-no>` with your desired version.

```bash
docker build -t todo-service:<version-no> .
```

Example:

```bash
docker build -t todo-service:v2 .
```

---

## Load Updated Image into KIND

```bash
kind load docker-image todo-service:<version-no> --name todo-cluster
```

---

## Update Deployment Image

Update the image version inside:

```text
k8s/deployment.yaml
```

Example:

```yaml
image: todo-service:v2
```

---

## Apply Updated Deployment

```bash
kubectl apply -f k8s/deployment.yaml
```

Or restart the deployment:

```bash
kubectl rollout restart deployment todo-deployment
```

---

# Verify Application

```text
http://localhost:30080
http://localhost:30080/todos
http://localhost:30080/health
```

---

# Tech Stack

- Node.js
- Docker
- Kubernetes
- KIND

---

# Enjoy 🚀