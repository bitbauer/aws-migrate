import boto3
import botocore
import logging

stack_name = 'migration_game'
template_name = '../DatabaseMigrationWorkshop.json'
params = [
    {
        'ParameterKey': 'KeyName',
        'ParameterValue': 'hessie_DMSKeyPair'
    }
]
tags = [
    {
        'Key': 'Environment',
        'Value': 'migration_game'
    },
]
client = boto3.client('cloudformation') # for client interface
log = logging.getLogger('deploy.cf.create_or_update')

def main():
    with open(template_name) as template_fileobj:
        template = template_fileobj.read()
    client.validate_template(TemplateBody=template)

    try:
        if _stack_exists(stack_name):
            print('Updating {}'.format(stack_name))
            response = client.update_stack(
                StackName=stack_name,
                TemplateBody=template,
                Parameters=params,
                Tags=tags)
            waiter = client.get_waiter('stack_update_complete')
        else:
            print('Creating {}'.format(stack_name))
            response = client.create_stack(
                StackName=stack_name,
                TemplateBody=template,
                Parameters=params,
                Tags=tags)
            waiter = client.get_waiter('stack_create_complete')

        print("...waiting for stack to be ready...")
        waiter.wait(StackName=stack_name)

    except botocore.exceptions.ClientError as ex:
        if ex.response['Error']['Message'] == 'No updates are to be performed.':
            print("\nNo changes:")
        else:
            raise

    except botocore.exceptions.WaiterError as ex:
        stack = client.describe_stacks(StackName=stack_name)['Stacks'][0]
        print("\nStack Creation error: {} ({})".format(stack['StackStatus'], ex))
        exit(1)

    else:
        print("\nStack created as following:")

    stack = client.describe_stacks(StackName=stack_name)['Stacks'][0] or {'Outputs': [],}
    server = None
    for i in stack['Outputs']:
        print("\t{}: {}".format(i['OutputKey'], i['OutputValue']))
        if i['OutputKey'] == 'PublicIP':
            server = i['OutputValue']

    if server:
        print("\tTestCommand: py.test --hosts=ssh://ec2-user@{} test_simpleserver.py".format(server))

def _stack_exists(stack_name):
    stacks = client.list_stacks()['StackSummaries']
    for stack in stacks:
        if stack['StackStatus'] == 'DELETE_COMPLETE':
            continue
        if stack_name == stack['StackName']:
            return True
    return False

if __name__ == "__main__":
    main()
