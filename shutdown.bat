@echo off
echo ============================================
echo  Shutting Down Seismic Monitoring System
echo ============================================
echo.

echo [1/5] Deleting ingress resources...
kubectl delete ingress seismic-ingress -n seismic-monitoring 2>nul
echo ✓ Ingress deleted
echo.

echo [2/5] Deleting Kubernetes deployments...
kubectl delete deployment seismic-producer -n seismic-monitoring 2>nul
kubectl delete deployment seismic-consumer -n seismic-monitoring 2>nul
kubectl delete deployment kafka -n seismic-monitoring 2>nul
kubectl delete deployment zookeeper -n seismic-monitoring 2>nul
echo ✓ Deployments deleted
echo.

echo [3/5] Deleting services...
kubectl delete service seismic-frontend -n seismic-monitoring 2>nul
kubectl delete service kafka-service -n seismic-monitoring 2>nul
kubectl delete service zookeeper-service -n seismic-monitoring 2>nul
echo ✓ Services deleted
echo.

echo [4/5] Deleting ingress...
kubectl delete namespace ingress-nginx
echo ✓ Ingress deleted
echo.

echo ============================================
echo  Shutdown Complete!
echo ============================================
echo.
echo All resources have been removed from Kubernetes.
echo Docker images are preserved for faster restart.
echo.
kubectl get pods -n seismic-monitoring -w
pause
