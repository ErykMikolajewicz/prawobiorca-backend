#!/usr/bin/env bash
set -euo pipefail

echo "Applying shared resources..."
kubectl apply -f cicd/k8s/rbac.yaml
kubectl apply -f cicd/k8s/secrets.yaml
kubectl apply -f cicd/k8s/ingress.yaml

echo "Applying databases..."
kubectl apply -f cicd/k8s/postgres.yaml

echo "Applying embedding-service..."
kubectl apply -f cicd/k8s/embedding-service.yaml

echo "Applying extraction-service..."
kubectl apply -f cicd/k8s/extraction-service.yaml

echo "Waiting for database..."
kubectl rollout status deployment/postgres --timeout=180s

echo "Waiting for embedding-service..."
kubectl rollout status deployment/embedding-service --timeout=180s

echo "Waiting for extraction-service..."
kubectl rollout status deployment/extraction-service --timeout=180s

echo "Applying backend..."
kubectl apply -f cicd/k8s/prawobiorca-backend.yaml

echo "Waiting for backend..."
kubectl rollout status deployment/prawobiorca-backend --timeout=180s

echo "Applying frontend..."
kubectl apply -f cicd/k8s/prawobiorca-frontend.yaml

echo "Waiting for frontend..."
kubectl rollout status deployment/prawobiorca-frontend --timeout=180s

echo "Deployment completed."