import boto3

S3client = boto3.client('s3')
s3 = boto3.resource('s3')

def main(event, context):
    for bucket in s3.buckets.all():
        print(bucket.name)
        
    return {
        'statusCode': 200,
        'body': 'Hello, from lambda'
    }