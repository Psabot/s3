#! /usr/bin/env python3

import os
import sys
import json

import boto3

with open('credentials.json', 'r') as fd:
    credentials = json.loads(fd.read())

def initClient(endpoint, access_key, secret_key):
    return boto3.client('s3',
                      endpoint_url=endpoint,
                      aws_access_key_id=access_key,
                      aws_secret_access_key=secret_key,
                      use_ssl=False)

def listBuckets(client):
    response = client.list_buckets()
    for item in response['Buckets']:
        print(item['CreationDate'], item['Name'])

def listBucketObjects(client, bucket):
    response = client.list_objects(Bucket=bucket)
    if 'Contents' in response:
        for obj in response['Contents']:
            print(obj['Key'])
    else:
        print("Pas d'objets")

def copyBucketContent(client_src, bucket_src, client_dest, bucket_dest):
    response = client_src.list_objects(Bucket=bucket_src)
    for obj in response['Contents']:
        src_obj = client_src.get_object(Bucket=bucket_src, Key=obj['Key'])
        print(src_obj)
        client_dest.upload_fileobj(src_obj['Body'], bucket_dest, obj['Key'])

def createBucket(client, bucket_name):
    client.create_bucket(ACL='public-read-write', Bucket=bucket_name)

def main():
    s3_src = initClient(credentials['endpoint_url_src'], credentials['access_key_src'], credentials['secret_key_src'])

    binary_data = b'Hello mate'
    s3_src.put_object(Body=binary_data, Bucket='test', Key='test.txt')

    print("Objets du bucket test")
    listBucketObjects(s3_src, 'test')

    s3_dest = initClient(credentials['endpoint_url_dest'], credentials['access_key_dest'], credentials['secret_key_dest'])

    bucket_to_be_created = 'dest'
    createBucket(s3_dest, bucket_to_be_created)
    #listBuckets(s3_dest)

    print("Objets du bucket " + bucket_to_be_created)
    listBucketObjects(s3_dest, bucket_to_be_created)

    some_binary_data = b'Hello mate'
    #s3_dest.put_object(Body=some_binary_data, Bucket=bucket_to_be_created, Key='tmp/osef.txt')

    #copyBucketContent(s3_src, 'test', s3_dest, bucket_to_be_created)

    print("Objets du bucket " + bucket_to_be_created)
    listBucketObjects(s3_dest, bucket_to_be_created)


if __name__ == '__main__':
    main()
