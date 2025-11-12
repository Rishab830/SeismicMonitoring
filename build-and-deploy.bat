@echo off
echo Building and deploying Seismic Monitoring System...

echo Building Producer image...
cd producer
docker build -t seismic-producer:latest .
cd ..

echo Building Consumer image...
cd consumer
docker build -t seismic-consumer:latest .
cd ..

echo Creating Kubernetes namespace...
kubectl apply -f kafka-deployment.yaml

echo Waiting for Kafka...
timeout /t 60

echo Deploying Producer...
kubectl apply -f producer-deployment.yaml

echo Deploying Consumer...
kubectl apply -f consumer-deployment.yaml

echo.
echo Deployment complete!
echo.
echo Access the dashboard at:
kubectl get svc seismic-frontend -n seismic-monitoring

pause
