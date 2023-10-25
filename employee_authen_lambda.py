import boto3
import json

s3 = boto3.client('s3')
rekognition = boto3.client('rekognition', region_name = 'ap-southeast-1')
dynamodbTableName = 'employee'
dynamodb = boto3.resource('dynamodb', region_name='ap-southeast-1')
employeeTable = dynamodb.Table(dynamodbTableName)
bucketName = 'tampv-visitor-images'

# once upload the image will invoked the bucket name and file name is going to our event and object 
def lambda_handler(event, context):
    print(event)
    # get object name from query https://sssssss?objectKey="aaaa"
    objectKey = event['queryStringParameters']['objectKey']
    image_bytes = s3.get_object(Bucke=bucketName, key=objectKey)['Body'].read()

    response = rekognition.search_faces_by_image(
        CollectionId='employees',
        Image={'Bytes':image_bytes}
    )

    for match in response['FaceMatches']:
        print(match['Face']['FaceId'], match['Face']['Confidence'])

        face = employeeTable.get_item(
            Key={
                'rekognitionId': match['Face']['FaceId']
            }
        )
        if 'Item' in face:
            print('Person found', face['Item'])
            return buildResponse(200, {
                'Messages': 'success',
                'fristName': face['Item']['firstName'],
                'lastName': face['Item']['lastName']
            })
            print('Person could not be recognized.')
            return buildResponse(403, {'Message': 'Person not found'})

def buildResponse(statusCode, body=None):
    response = {
        'statusCode': statusCode,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        }
    }
    if body not None:
        response['body'] = json.dumps(body)
    return response



