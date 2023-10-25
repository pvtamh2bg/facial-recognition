import boto3

s3 = boto3.client('s3')
rekognition = boto3.client('rekognition', region_name = 'ap-southeast-1')
dynamodbTableName = 'employee'
dynamodb = boto3.resource('dynamodb', region_name='ap-southeast-1')
employeeTable = dynamodb.Table(dynamodbTableName)

# once upload the image will invoked the bucket name and file name is going to our event and object 
def lambda_handler(event, context):
    print(event)
    # extract the key (1. bucket name 2. object image name)
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = event['Records'][0]['s3']['object']['key']

    try:
        response = index_employee_image(bucket, key)
        print(response)
        if response['ResponseMetadata']['HTTPStatusCode'] == 200:
            faceId = response['FaceRecords'][0]['Face']['FaceId']
            # get the image name
            name = key.split('.')[0].split('_')
            firstName = name [0]
            lastName = name[1]
            register_employee(faceId, firstName, lastName)
            return response
    except Exception as e:
        print(e)
        print('Error processing employee image {} from bucket {} .'.format(key, bucket))
        raise e

def index_employee_image(bucket, key):
    response = rekognition.index_faces(
        Image ={ 
        'S3Object':
        {
            'Bucket':bucket,
            'Name': key,
        }
        },
        CollectionId = "employees"
    )
    return response

def register_employee(faceId, firstName, lastName):
    employeeTable.put_item(
        Item={
            'rekognitionId': faceId,
            'firstName': firstName,
            'lastName': lastName,
        }
    )



