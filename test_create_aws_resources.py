
import boto3
from botocore.exceptions import ClientError
session = boto3.Session(profile_name='default', region_name='us-east-2')
s3 = session.client('s3')

bucket_name = "my-unique-bucket-name-123456789Andreea" # must be globally unique
region = "us-east-2"

try:
    if region == "us-east-2":
        response = s3.create_bucket(Bucket=bucket_name)
    else:
        response = s3.create_bucket(Bucket=bucket_name, CreateBucketConfiguration={'LocationConstraint': region})
        print(f"✅ S3 bucket '{bucket_name}' created successfully.")
except ClientError as e:
    print(f"❌ Failed to create bucket: {e.response['Error']['Message']}")
except Exception as e:
    print(f"❌ Unexpected error: {e}")