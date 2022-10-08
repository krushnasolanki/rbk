#!/bin/sh

IMAGE_NAME="dwf-opportunity"

# Delete Dangling Images
echo "Deleting dangling images"
docker rmi -f $(docker images --filter 'dangling=true' -q)

echo "Stop and remove all containers of $IMAGE_NAME-cbe"
docker stop $(docker ps -a -f ancestor=dwf-opportunity-cbe:* -q)
docker ps rm $(docker ps -a -f ancestor=dwf-opportunity-cbe:* -q)
docker rm -f  $(docker ps -a -f ancestor=$IMAGE_NAME-cbe:* -q)

echo "Stop and remove all containers of $IMAGE_NAME-cscore"
docker stop $(docker ps -a -f ancestor=dwf-opportunity-cscore:* -q)
docker ps rm $(docker ps -a -f ancestor=dwf-opportunity-cscore:* -q)
docker rm -f  $(docker ps -a -f ancestor=$IMAGE_NAME-cscore:* -q)


# Delete dwf-opportunity-* Images
echo "Deleting $IMAGE_NAME-cbe images"
docker rmi -f $(docker images --filter="reference=$IMAGE_NAME-cbe:*" -q)

echo "Deleting $IMAGE_NAME-cscore images"
docker rmi -f $(docker images --filter="reference=$IMAGE_NAME-cscore:*" -q)

# Build New Image
echo "Building $IMAGE_NAME-cbe image started"
docker build -f Dockerfile.cbe -t $IMAGE_NAME-cbe .
echo "Building $IMAGE_NAME-cbe image is complete"


echo "Building $IMAGE_NAME-cscore image started"
docker build -f Dockerfile.cscore -t $IMAGE_NAME-cscore .
echo "Building $IMAGE_NAME-cscore image is complete"

echo "Run the container"
#docker run -d $IMAGE_NAME:latest
#docker run --env-file ./local.env -it --rm $IMAGE_NAME-cbe
#docker run --env-file ./local.env -it --rm $IMAGE_NAME-cscore
#docker run -it --rm $IMAGE_NAME bash