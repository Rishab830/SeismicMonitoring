@echo off
echo ============================================
echo  Quick Restart (No Image Rebuild)
echo ============================================
echo.

echo Stopping current deployments...
kubectl delete deployment seismic-producer seismic-consumer -n seismic-monitoring
timeout /t 5 /nobreak
echo.

echo Starting deployments...
kubectl apply -f producer-deployment.yaml
kubectl apply -f consumer-deployment.yaml
echo.

echo Waiting for pods to start...
timeout /t 20 /nobreak
echo.

kubectl get pods -n seismic-monitoring -w
echo.
echo ✓ Restart complete!
pause
