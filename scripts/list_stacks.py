import boto3
import botocore

client = boto3.client('cloudformation') # for client interface
stacks = client.list_stacks()['StackSummaries']

for i in stacks:
    if i['StackStatus'] != 'DELETE_COMPLETE':
        print("\t{}: {}".format(i['StackName'], i['StackStatus']))