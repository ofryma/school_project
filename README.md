
## Configure Env
set an `.env` file at the root directory:
```

```


## Build the image

run the docker-compose file with this command:
```
docker compose -f "docker-compose.yml" up -d --build
```
This will run the project and also create a docker image called `school_project_api`


## Push to ECR

Get authentication token. run the command:

```
aws ecr-public get-login-password --region us-east-1 | docker login --username AWS --password-stdin public.ecr.aws/h6w9d2s6
```

Tag your image:
```
docker tag school_project_api:latest public.ecr.aws/h6w9d2s6/school-project:latest
```

Push to AWS repository:
```
docker push public.ecr.aws/h6w9d2s6/school-project:latest
```

## Deploy on EC2

1. Connect to the EC2 instance on AWS account (instance terminal)
2. Deploy the docker image on the instance:
```
docker run -d -p 8001:80 public.ecr.aws/h6w9d2s6/school-project:latest
```


