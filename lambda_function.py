import json
import boto3


sns = boto3.client('sns')
sqs = boto3.client('sqs')

###################################### SNS Fucntions #######################################

def get_sns_topics():
    topiclist = []
    paginator = sns.get_paginator('list_topics')
    response_iterator = paginator.paginate(
        PaginationConfig={
            'MaxItems': 200
            }
    )
    for res in response_iterator:
        for topics in res['Topics']:
            topiclist.append(topics['TopicArn'])
    return topiclist

def check_sns_encryption(topiclist):
    kms_disabled_sns = []
    for arn in topiclist:
        response = sns.get_topic_attributes(TopicArn=arn)
        if 'KmsMasterKeyId' not in response['Attributes']:
            kms_disabled_sns.append(response['Attributes']['TopicArn'])
    return kms_disabled_sns

def encrypt_sns(kms_disabled_sns):
    for sns_arn in kms_disabled_sns:
        response = sns.set_topic_attributes(
            TopicArn = sns_arn,
            AttributeName = 'KmsMasterKeyId',
            AttributeValue = 'alias/aws/sns'
        )

####################################### SQS Fucntions #######################################

def get_sqs_topics():
    queue_list = []
    paginator = sqs.get_paginator('list_queues')
    response_iterator = paginator.paginate(
        PaginationConfig={
            'MaxItems': 200,
        }
    )
    for res in response_iterator:
        return (res['QueueUrls'])

def check_sqs_encryption(queuelist):
    kms_disabled_sqs = []
    queueurl = []
    for url_queue in queuelist:
        response = sqs.get_queue_attributes(
            QueueUrl = url_queue,
            AttributeNames = [
                'All',
                'KmsMasterKeyId'
            ]
        )
        if 'KmsMasterKeyId' not in response['Attributes']:
            queueurl.append(url_queue)
    return queueurl

def encrypt_sqs(queueurl):
    for queueurl in queueurl:
        url = str(queueurl).replace('[','').replace(']','').replace("'","")
        response = sqs.set_queue_attributes(
            QueueUrl = url,
            Attributes = {
                'KmsMasterKeyId' : 'alias/aws/sqs'
            }
        )

# def lambda_handler(event, context):

########## SNS Function ##########
topiclist = get_sns_topics()
kms_disabled_sns = check_sns_encryption(topiclist)
if len(kms_disabled_sns) !=0:
        encrypt_sns(kms_disabled_sns)
        print ("Server-Side-Encryption is been enabled for SNS Topic: ", kms_disabled_sns)
else:
    print ("All SNS Topics are Encrypted")

########## SQS Function ##########
queuelist = get_sqs_topics()
queueurl = check_sqs_encryption(queuelist)
if len(queueurl) !=0:
        encrypt_sqs(queueurl)
        print ("Server-Side-Encryption is been enabled for SQS Queue: ", queueurl)
else:
    print ("All SQS Queues are Encrypted")
