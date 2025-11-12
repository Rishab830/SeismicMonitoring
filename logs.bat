@echo off
echo ============================================
echo  View Logs - Select Component
echo ============================================
echo.
echo 1. Producer
echo 2. Consumer
echo 3. Kafka
echo 4. Zookeeper
echo 5. All Pods
echo.
set /p choice="Enter your choice (1-5): "

if "%choice%"=="1" (
    kubectl logs -f deployment/seismic-producer -n seismic-monitoring
) else if "%choice%"=="2" (
    kubectl logs -f deployment/seismic-consumer -n seismic-monitoring
) else if "%choice%"=="3" (
    kubectl logs -f deployment/kafka -n seismic-monitoring
) else if "%choice%"=="4" (
    kubectl logs -f deployment/zookeeper -n seismic-monitoring
) else if "%choice%"=="5" (
    kubectl get pods -n seismic-monitoring
    set /p pod="Enter pod name to view logs: "
    kubectl logs -f %pod% -n seismic-monitoring
) else (
    echo Invalid choice!
    pause
    exit /b 1
)
