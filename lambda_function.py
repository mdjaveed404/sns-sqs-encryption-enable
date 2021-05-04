import json
import boto3


sns = boto3.client('sns')
sqs = boto3.client('sqs')

####################################### SNS Fucntions #######################################

def get_sns_topics():
    topiclist = []
    response = sns.list_topics()
    for topics in response['Topics']:
        topiclist.append(topics['TopicArn'])
    while "NextToken" in response:
        response = sns.list_topics()
        for topics in response['Topics']:
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
    response = sqs.list_queues(MaxResults=299)
    return (response['QueueUrls'])

def check_sqs_encryption(queuelist):
    kms_disabled_sqs = []
    queueurl = []
    for queuearn in queuelist:
        response = sqs.get_queue_attributes(
            QueueUrl = queuearn,
            AttributeNames = [
                'All',
                'KmsMasterKeyId'
            ]
        )
        if 'KmsMasterKeyId' not in response['Attributes']:
            kms_disabled_sqs.append(response['Attributes']['QueueArn'])
            for queuename in kms_disabled_sqs:
                queuenamesort = queuename.split(':')[-1]
                response = sqs.list_queues(
                    QueueNamePrefix = queuenamesort,
                    MaxResults = 299
                )
            queueurl.append(response['QueueUrls'])

    return queueurl
            
def encrypt_sqs(queueurl):
    for queueurl in queueurl:
        url = str(queueurl).replace('[','').replace(']','').replace("'","")
        response = sqs.set_queue_attributes(
            QueueUrl = url,
            Attributes = {
                'KmsMasterKeyId' : 'arn:aws:kms:us-east-1:508783485521:key/d511ee60-48b9-43fb-9d7d-ddd854737a58'
            }
        )
    
    
####################################################### Lambda Main Function #######################################################

def lambda_handler(event, context):
    
    ########## SNS Function ##########
    topiclist = get_sns_topics()
    kms_disabled_sns = check_sns_encryption(topiclist)
    if len(kms_disabled_sns) !=0:
        encrypt_sns(kms_disabled_sns)
        print ("Server-Side-Encryption is been enabled for SNS Topic: ", kms_disabled_sns)


    ########## SQS Function ##########
    queuelist = get_sqs_topics()
    queueurl = check_sqs_encryption(queuelist)
    if len(queueurl) !=0:
        encrypt_sqs(queueurl)
        print ("Server-Side-Encryption is been enabled for SQS Queue: ", queueurl)



