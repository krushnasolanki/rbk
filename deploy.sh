#!/bin/sh

#rm temp/*
#rmdir temp

IMAGE_NAME="dwf-opportunity"
NAME_SPACE="default"
TARGET_ENV="minikube"
IMAGE_HOST="localhost:5000"
IMAGE_TAG="latest"

docker tag $IMAGE_NAME $IMAGE_HOST/$IMAGE_NAME:$IMAGE_TAG
docker push $IMAGE_HOST/$IMAGE_NAME:$IMAGE_TAG

echo "Configure Deployment, ConfigMap, Secrets"
mkdir temp
chmod 755 temp
cp ./deployment/Cronjob.yaml ./temp/Cronjob.yaml
cp ./deployment/dev/ConfigMap.yaml ./temp/ConfigMap.yaml
cp ./deployment/dev/Secrets.yaml ./temp/Secrets.yaml

sed -i '' "s/{{IMAGE_NAME}}/$IMAGE_NAME/g" temp/Cronjob.yaml
sed -i '' "s/{{IMAGE_HOST}}/$IMAGE_HOST/g" temp/Cronjob.yaml
sed -i '' "s/{{IMAGE_TAG}}/$IMAGE_TAG/g" temp/Cronjob.yaml
sed -i '' "s/{{NAME_SPACE}}/$NAME_SPACE/g" temp/Cronjob.yaml
sed -i '' "s/{{TARGET_ENV}}/$TARGET_ENV/g" temp/Cronjob.yaml
sed -i '' "s/{{NAME_SPACE}}/$NAME_SPACE/g" temp/ConfigMap.yaml
sed -i '' "s/{{NAME_SPACE}}/$NAME_SPACE/g" temp/Secrets.yaml
sed -i '' "s/{{TARGET_ENV}}/$TARGET_ENV/g" temp/ConfigMap.yaml
sed -i '' "s/{{TARGET_ENV}}/$TARGET_ENV/g" temp/Secrets.yaml

#echo "Start minikube"
#minikube start

cat temp/Cronjob.yaml

kubectl apply -f temp/Secrets.yaml
kubectl apply -f temp/ConfigMap.yaml
kubectl apply -f temp/Cronjob.yaml

