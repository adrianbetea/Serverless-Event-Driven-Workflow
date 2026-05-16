import json
import boto3
from botocore.exceptions import ClientError

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('Students')

def lambda_handler(event, context):
    for record in event['Records']:
        payload = json.loads(record['body'])
        student_id = payload['id']
        course = payload['course']
        timestamp = payload['timestamp']
        
        try:
            table.update_item(
                Key={'id': student_id},
                UpdateExpression="SET courses = list_append(if_not_exists(courses, :empty_list), :course), LastUpdated = :time",
                ConditionExpression="attribute_not_exists(courses) OR NOT contains(courses, :course_str)",
                ExpressionAttributeValues={
                    ':course': [course],
                    ':course_str': course,  
                    ':empty_list': [],
                    ':time': timestamp
                }
            )
            print(f"Success: Enrolled {student_id} in {course}")
            
        except ClientError as e:
            if e.response['Error']['Code'] == 'ConditionalCheckFailedException':
                print(f"DUPLICATE BLOCKED: {student_id} is already in {course}. Ignored.")
            else:
                raise e
        
    return {'statusCode': 200, 'body': 'Success'}