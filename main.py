import boto3
from botocore.exceptions import NoCredentialsError, ClientError

profile_name = 'default'
region_name = 'us-east-2'
s3_bucket_name = "bucket-from-boto3-andreeaghe"

# Define the security group name and description
security_group_name = 'securityGroupForEC2'
description = 'Security group allowing SSH access'

# Define parameters for the EC2 instance
ami_id = 'ami-0c55b159cbfafe1f0'  # Example: Replace with your preferred AMI ID (Amazon Linux 2)
instance_type = 't2.micro'  # Choose the instance type
key_name = 'key-pair-for-ssh-in-ec2'  # Your existing key pair
security_group_ids = ['sg-0123456789abcdef0']  # Security group ID (Ensure the security group allows SSH access)


def validate_credentials():
    try:
        session = boto3.Session(profile_name=profile_name)
        sts = session.client("sts")
        identity = sts.get_caller_identity()
        print("Credentials are working!")
        print(identity)
    except NoCredentialsError:
        print("No credentials found.")
    except ClientError as e:
        print("AWS client error:", e)


def create_s3_bucket():
    session = boto3.Session(profile_name=profile_name, region_name=region_name)
    s3 = session.client('s3')

    bucket_name = s3_bucket_name  # must be globally unique
    region = region_name

    try:
        if region == "us-east-1":
            response = s3.create_bucket(Bucket=s3_bucket_name)
        else:
            response = s3.create_bucket(Bucket=s3_bucket_name, CreateBucketConfiguration={'LocationConstraint': region})
            print(f"S3 bucket '{s3_bucket_name}' created successfully.")
    except ClientError as e:
        print(f"Failed to create bucket: {e.response['Error']['Message']}")
    except Exception as e:
        print(f"Unexpected error: {e}")


def create_security_group():
    # Session using default profile
    session = boto3.Session(profile_name=profile_name, region_name=region_name)  # Ensure region is correct
    ec2 = session.client('ec2')

    try:
        # Create the security group
        response = ec2.create_security_group(
            GroupName=security_group_name,
            Description=description
        )

        security_group_id = response['GroupId']
        print(f"Security Group '{security_group_name}' created successfully with ID: {security_group_id}")

        # Add an inbound rule to allow SSH access on port 22 from anywhere (0.0.0.0/0)
        ec2.authorize_security_group_ingress(
            GroupId=security_group_id,
            IpPermissions=[
                {
                    'IpProtocol': 'tcp',
                    'FromPort': 22,
                    'ToPort': 22,
                    'IpRanges': [{'CidrIp': '0.0.0.0/0'}]  # Allows SSH from anywhere
                }
            ]
        )

        print(f"Inbound rule added: Allow SSH (port 22) from 0.0.0.0/0")

        return security_group_id

    except ClientError as e:
        print(f"Failed to create security group or add rules: {e.response['Error']['Message']}")


def create_ec2_instance_with_security_group(security_group_id):
    # Session using default profile
    session = boto3.Session(profile_name=profile_name, region_name=region_name)  # Ensure region is correct
    ec2 = session.client('ec2')

    try:
        # Launch an EC2 instance with the security group
        response = ec2.run_instances(
            ImageId=ami_id,
            InstanceType=instance_type,
            KeyName=key_name,
            SecurityGroupIds=[security_group_id],  # Add the newly created security group
            MinCount=1,
            MaxCount=1,
            TagSpecifications=[{
                'ResourceType': 'instance',
                'Tags': [{'Key': 'Name', 'Value': 'MyTestEC2'}]
            }]
        )

        # Get the Instance ID
        instance_id = response['Instances'][0]['InstanceId']
        print(f"EC2 instance created successfully! Instance ID: {instance_id}")
        return instance_id

    except ClientError as e:
        print(f"Failed to create EC2 instance: {e.response['Error']['Message']}")


def delete_ec2_instance_with_security_group(instance_id):
    # Session using default profile
    session = boto3.Session(profile_name=profile_name, region_name=region_name)  # Ensure region is correct
    ec2 = session.client('ec2')

    try:
        response = ec2.terminate_instances(InstanceIds=[instance_id])
        print(f"Termination initiated for instance: {instance_id}")
        print("Response:", response)
    except Exception as e:
        print(f" Failed to terminate instance: {e}")


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    # validate_credentials()
    # create_s3_bucket()
    # create_security_group()
    security_group_id = create_security_group()
    # Create the security group
    if security_group_id:
        instance_id = create_ec2_instance_with_security_group(security_group_id)

        # Delete EC2 instance
        if instance_id:
            delete_ec2_instance_with_security_group(instance_id)
