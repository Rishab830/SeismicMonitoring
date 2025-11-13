# Building My Images from Dockerfiles
1) docker build -t seismic-producer:latest ./producer
    - To build producer container from producer image (Dockerfile in producer folder)
    - -t tags the container with the name seismic-producer (version latest)
2) docker build -t seismic-consumer:latest ./consumer
    - To build consumer container from consumer image (Dockerfile in consumer folder)
    - -t tags the container with the name seismic-consumer (version latest)
# Checking My Built Images
1) docker images
    - to view all images currently stores in the system
# Pushing My Images to Dockerhub
1) docker tag seismic-producer:latest skillissue1212/seismic-producer:latest
    - this creates a duplicate image named skillissue1212/seismic-producer:latest which is identical to seismic-producer:latest
2) docker tag seismic-consumer:latest skillissue1212/seismic-consumer:latest
    - this creates a duplicate image named skillissue1212/seismic-consumer:latest which is identical to seismic-consumer:latest
3) docker push skillissue1212/seismic-producer:latest
    - this pushes the producer image to the repository skillissue1212 as seismic-producer:latest
4) docker push skillissue1212/seismic-consumer:latest
    - this pushes the consumer image to the repository skillissue1212 as seismic-consumer:latest
# Creating Namespace
1) kubectl create namespace seismic-monitoring
    - creates a kubernetes namespace called seismic-monitoring
# Making Deployments Out Of My Images
1) kubectl apply -f producer-deployment.yaml
    - creates a producer deployment out of the seismic-producer:latest image
2) kubectl apply -f consumer-deployment.yaml
    - creates a consumer deployment out of the seismic-consumer:latest image
3) kubectl apply -f kafka-deployment.yaml
    - - creates a kafka deployment out of the kafka and zookeeper image
# Check Running Containers
1) docker ps -a
    - Prints information about all running containers
# Info About Pods
1) kubectl get pods -n seismic-monitoring -w
    - keep a watch on the pods in namespace seismic-monitoring
# Get IP of Front End
1) kubectl get svc seismic-frontend -n seismic-monitoring
    - to see what is the current port the service is connected to
2) kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.9.0/deploy/static/provider/cloud/deploy.yaml
    - to deploy nginx-ingress for ngrok
3) kubectl get svc ingress-nginx-controller -n ingress-nginx
    - to get the port of ingress-nginx-controller
4) ngrok http 80
    - to create ngrok tunnel on port 80 (port is specified by port of ingress-nginx-controller)
    