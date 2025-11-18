@echo off
echo ============================================
echo  Quick Restart (No Image Rebuild)
echo ============================================
echo.

echo Creating namespace...
kubectl create namespace seismic-monitoring
kubectl create namespace ingress-nginx
echo.

echo Starting deployments...
kubectl apply -f kafka-deployment.yaml
kubectl apply -f producer-deployment.yaml
kubectl wait --for=condition=available deployment/seismic-producer -n seismic-monitoring
kubectl logs -f deployment/seismic-producer -n seismic-monitoring
kubectl apply -f consumer-deployment.yaml
kubectl wait --for=condition=available deployment/seismic-consumer -n seismic-monitoring
kubectl logs -f deployment/seismic-consumer -n seismic-monitoring
echo.

echo Waiting for deployments to be ready...
kubectl wait --for=condition=available deployment/kafka -n seismic-monitoring
kubectl wait --for=condition=available deployment/zookeeper -n seismic-monitoring

echo Setting up Ingress...
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.9.0/deploy/static/provider/cloud/deploy.yaml
ngrok http 80

kubectl get pods -n seismic-monitoring -w
echo.
echo ✓ Start complete!
pause
