@echo off
echo ============================================
echo  Seismic Monitoring System Status
echo ============================================
echo.

echo === Application Pods ===
kubectl get pods -n seismic-monitoring
echo.

echo === Ingress Controller Pods ===
kubectl get pods -n ingress-nginx
echo.

echo === Services ===
kubectl get svc -n seismic-monitoring
echo.

echo === Ingress Resources ===
kubectl get ingress -n seismic-monitoring
echo.

echo === Ingress Controller Service ===
kubectl get svc ingress-nginx-controller -n ingress-nginx
echo.

echo === Deployments ===
kubectl get deployments -n seismic-monitoring
kubectl get deployments -n ingress-nginx
echo.

echo === Recent Events (Errors Only) ===
kubectl get events -n seismic-monitoring --sort-by='.lastTimestamp' | findstr /V "Normal"
kubectl get events -n ingress-nginx --sort-by='.lastTimestamp' | findstr /V "Normal"
echo.

echo ============================================
echo  Access Information
echo ============================================
echo Application URL: http://localhost
echo.
echo ============================================
echo  Quick Commands
echo ============================================
echo View producer logs:  kubectl logs -f deployment/seismic-producer -n seismic-monitoring
echo View consumer logs:  kubectl logs -f deployment/seismic-consumer -n seismic-monitoring
echo View ingress logs:   kubectl logs -f deployment/ingress-nginx-controller -n ingress-nginx
echo.
pause
