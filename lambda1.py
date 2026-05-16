import json
import datetime
import boto3

sqs = boto3.client('sqs')
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('Students')

QUEUE_URL = env.QUEUE_URL   

def lambda_handler(event, context):
    headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': '*',
        'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
    }

    method = event.get('requestContext', {}).get('http', {}).get('method', 'GET')
    if method == 'OPTIONS':
        return {'statusCode': 200, 'headers': headers, 'body': ''}

    # Fetch student data
    if method == 'GET':
        student_id = event.get('queryStringParameters', {}).get('student_id', 'Student-101')
        response = table.get_item(Key={'id': student_id})
        item = response.get('Item', {'id': student_id, 'courses': []})
        return {'statusCode': 200, 'headers': headers, 'body': json.dumps(item)}

    # Enroll with DEDUPLICATION CHECK
    if method == 'POST':
        body = json.loads(event.get('body', '{}'))
        student_id = body.get('student_id', 'Student-101')
        course_name = body.get('course', 'Unknown Course')
        
        response = table.get_item(Key={'id': student_id})
        if 'Item' in response:
            existing_courses = response['Item'].get('courses', [])
            if course_name in existing_courses:
                return {
                    'statusCode': 400, 
                    'headers': headers,
                    'body': json.dumps({
                        'message': f'Error: You are already enrolled in "{course_name}".', 
                        'status': 'Duplicate'
                    })
                }

        tz_romania = datetime.timezone(datetime.timedelta(hours=3))
        current_time = datetime.datetime.now(tz_romania).strftime("%Y-%m-%d %H:%M:%S")
        
        sqs.send_message(
            QueueUrl=QUEUE_URL,
            MessageBody=json.dumps({'id': student_id, 'course': course_name, 'timestamp': current_time})
        )
        
        return {
            'statusCode': 200,
            'headers': headers,
            'body': json.dumps({
                'message': f'Enrollment request for "{course_name}" queued successfully!', 
                'status': 'Pending Async Processing'
            })
        }