#! /usr/bin/env python3

import os
import sys
import json

import boto3

with open('credentials.json', 'r') as fd:
    credentials = json.loads(fd.read())


def main():
    s3 = boto3.resource('s3',
                      endpoint_url=credentials['endpoint_url_dest'],
                      aws_access_key_id=credentials['access_key_dest'],
                      aws_secret_access_key=credentials['secret_key_dest'],
                      use_ssl=False)

    s3.create_bucket(Bucket="exemple")

    s3.Object('exemple', 'hello.txt').put(Body=open('/tmp/hello.txt', 'rb'))

    bucket = s3.Bucket(name='exemple')

    for object in bucket.objects.all():
        print(object)


if __name__ == '__main__':
    main()
