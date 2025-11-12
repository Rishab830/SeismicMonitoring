@echo off
echo ============================================
echo  FULL CLEANUP - This will delete EVERYTHING
echo ============================================
echo.
echo WARNING: This will delete:
echo   - All Kubernetes resources
echo   - All Docker containers
echo   - All Docker images
echo.
set /p confirm="Are you sure? (yes/no): "

if /i not "%confirm%"=="yes" (
    echo Cancelled.
    pause
    exit /b 0
)

echo.
echo Deleting Kubernetes namespace...
kubectl delete namespace seismic-monitoring

echo.
echo Stopping all Docker containers...
for /f "tokens=*" %%i in ('docker ps -aq') do docker stop %%i
for /f "tokens=*" %%i in ('docker ps -aq') do docker rm %%i

echo.
echo Removing Docker images...
docker rmi seismic-producer:latest -f
docker rmi seismic-consumer:latest -f
docker rmi confluentinc/cp-kafka:7.3.0 -f
docker rmi confluentinc/cp-zookeeper:7.3.0 -f

echo.
echo Running Docker cleanup...
docker system prune -f

echo.
echo ✓ Full cleanup complete!
pause
