from __future__ import print_function

import ast
import boto3

DNS_ZONE_ID = 'Z36AIH4YKD3FXS'
DNS_DOMAIN = 'lalani.co'
DNS_PREFIX = 'nginx-lb'


ec2 = boto3.resource('ec2')
client = boto3.client('ec2')
r53 = boto3.client('route53')


def main(event, context):
    print("Event")
    print(event)
    print ("Context")
    print(context)

    # Convert SNS message content from string into dict
    message = ast.literal_eval(event['Records'][0]['Sns']['Message'])

    print("Message:")
    print(message)
    instance_id = message['EC2InstanceId']
    print("Instance ID: {}".format(instance_id))

    if message['Event'] == 'autoscaling:EC2_INSTANCE_LAUNCH':
        print("Scaling Up Event")
        waiter = client.get_waiter('instance_status_ok')
        waiter.wait(InstanceIds=[instance_id])

        instance_dns, instance_ip = get_instance_information(instance_id)

        health_record = create_health_check(instance_id, instance_ip)
        print("Health Record: {}".format(health_record))
        update_dns(instance_id, instance_dns, 'CREATE', health_record)

    if message['Event'] == 'autoscaling:EC2_INSTANCE_TERMINATE':
        print("Scaling Down Event")
        dns_record = find_dns_records_by_set_id(instance_id)
        dns_record_value = dns_record['ResourceRecords'][0]['Value']
        health_record = find_health_check_by_name(instance_id)
        print("Health Record:".format(health_record))
        update_dns(
            instance_id,
            dns_record_value,
            'DELETE',
            health_record['Id']
        )
        r53.delete_health_check(HealthCheckId=health_record['Id'])

    print(message['StatusCode'])


def find_dns_records_by_set_id(set_id):
    # Get all DNS Records
    records = r53.list_resource_record_sets(
        HostedZoneId=DNS_ZONE_ID,
        StartRecordName='{}.{}'.format(DNS_PREFIX, DNS_DOMAIN)
    )['ResourceRecordSets']

    if not len(records):
        raise('No DNS Records Found')

    for record in records:
        print("Searching Records, Current Record:".format(record))
        if record['SetIdentifier'] == set_id:
            return record

    raise('No Matching DNS Records Found')


def update_dns(instance_id, instance_dns, action, health_check_id=None):
    print("Update DNS {}:{}".format(instance_dns, action))

    record_set = {
        'Name': '{}.{}'.format(DNS_PREFIX, DNS_DOMAIN),
        'Type': 'CNAME',
        'SetIdentifier': instance_id,
        'Weight': 0,
        'TTL': 60,
        'HealthCheckId': health_check_id,
        'ResourceRecords': [
            {
                'Value': instance_dns
            }
        ]
    }

    print("Record Set: {}".format(record_set))
    response = r53.change_resource_record_sets(
        HostedZoneId=DNS_ZONE_ID,
        ChangeBatch={
            'Changes': [
                {
                    'Action': action,
                    'ResourceRecordSet': record_set
                }
            ]
        }
    )
    print("R53 Response {}".format(response))


def create_health_check(instance_id, instance_ip):
    health_check = r53.create_health_check(
        CallerReference=instance_id,
        HealthCheckConfig={
            'IPAddress': instance_ip,
            'Type': 'HTTP'
        }
    )
    health_check_id = health_check['HealthCheck']['Id']

    r53.change_tags_for_resource(
        ResourceType='healthcheck',
        ResourceId=health_check_id,
        AddTags=[
            {
                'Key': 'Name',
                'Value': instance_id,
            }
        ]
    )
    return health_check_id


def get_instance_information(instance_id):
    instance = ec2.Instance(instance_id)
    print("Instance Public DNS: ".format(instance.public_dns_name))
    return instance.public_dns_name, instance.public_ip_address


def find_health_check_by_name(name):
    health_checks = r53.list_health_checks()['HealthChecks']
    for check in health_checks:
        if check['CallerReference'] == name:
            print("Health Record Found: {}".format(check))
            return check

    raise('No Health Check Found')
