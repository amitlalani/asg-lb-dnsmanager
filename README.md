
Infrastructure and lambda function to allow an autoscaling group to be load balanced via a single DNS entrypoint.

![Infrastructure Image](http://i.imgur.com/JgXwyzF.png)

# Prerequisites
* Python 2.7
* Python Pip
* AWS Credentials

# Setup
# Depedencies
1. pip install -r requirements.txt
2. aws configure - Follow instructions

# Lambda Setup
## Upload Code to S3
`cd lambdaDNSManagerFunction`
`./upload_code.sh v1`

## Create Infrastructure
`aws cloudformation create-stack --stack-name lamba-dns-manager-stack --template-body file://infrastructure.yaml --capabilities CAPABILITY_IAM --region us-east-1`

# AutoScalingGroup Setup
`aws cloudformation create-stack --stack-name asg-nginx-lb --template-body file://infrastructure.yaml --capabilities CAPABILITY_IAM --region us-east-1`
