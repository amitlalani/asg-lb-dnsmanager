input = {
    "Progress": 50,
    "AccountId": "145949126156",
    "Description": "Launching a new EC2 instance: i-023d9c3893ad9e004",
    "RequestId": "1e2a0a7a-bec9-4b68-b992-6ade17731627",
    "EndTime": "2016-10-19T19:31:03.164Z",
    "AutoScalingGroupARN": "arn:aws:autoscaling:eu-west-1:145949126156:autoScalingGroup:4c4cddd0-a32c-48f6-9515-2aea0ebe6a83:autoScalingGroupName/nginx-autoscaling-group",
    "ActivityId": "1e2a0a7a-bec9-4b68-b992-6ade17731627",
    "StartTime": "2016-10-19T19:30:30.621Z",
    "Service": "AWS Auto Scaling",
    "Time": "2016-10-19T19:31:03.164Z",
    "EC2InstanceId": "i-023d9c3893ad9e004",
    "StatusCode": "InProgress",
    "StatusMessage": "",
    "Details": {
        "Subnet ID": "subnet-ea28aa8e",
        "Availability Zone": "eu-west-1a"
    },
    "AutoScalingGroupName": "nginx-autoscaling-group",
    "Cause": "At 2016-10-19T19:30:29Z an instance was started in response to a difference between desired and actual capacity, increasing the capacity from 0 to 1.",
    "Event": "autoscaling:EC2_INSTANCE_LAUNCH"
}


import boto3


ec2 = boto3.resource('ec2')
client = boto3.client('ec2')

def dns_record_manager(event, context):

    message = event['Records'][0]['Sns']['Message']
    instance_id = message['EC2InstanceId']
    instance_dns = get_instance_information(instance_id)

    # Scale Up Events
    if message['EVENT'] == 'autoscaling:EC2_INSTANCE_LAUNCH':
        waiter = client.get_waiter('instance_status_ok')
        waiter.wait(InstanceId=[instance_id])
        update_dns(instance_dns, 'CREATE')

    # Scale Down Events
    if message['EVENT'] == 'autoscaling:EC2_INSTANCE_TERMINATE':
        update_dns(instance_dns, 'DELETE')

    print(message['StatusCode'])


def update_dns(instance_dns, action):
    print("Update DNS {}:{}".format(instance_dns, action))
    #response = client.change_resource_record_sets(
    #    HostedZoneId='',
    #    ChangeBatch= {
    #        'Changes': [
    #            {
    #                'Action': action,
    #                'ResourceRecordSet': {
    #                    'Name': 'test-nginx-loadbalancer',
    #                    'Type': 'CNAME'
    #                    'SetIdentifier': instance_dns,
    #                    'Weight': 0,
    #                    'TTL': 60,
    #                }
    #            }
    #        ]
    #    }
    #)

def create_dns_health_check():
    #CallerReference
    #client.create_health_check(
    #    HealthCheckConfig={
    #        'IPAddress':
    #    }
    #)
    pass

def get_instance_information(instance_id):
    instance = ec2.Instance(instance_id)
    print("Instance ID".format(instance.public_dns))
    return instance.public_dns


