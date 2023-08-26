import boto3
import dotenv
from functools import lru_cache
session = boto3.session.Session(region_name='ap-southeast-2', aws_secret_access_key=dotenv.get_key('.env', 'AWS_SECRET_ACCESS_KEY'), aws_access_key_id=dotenv.get_key('.env', 'AWS_ACCESS_KEY_ID'))
dynamodb = session.resource('dynamodb')
degree_table = dynamodb.Table('degree')
major_table = dynamodb.Table('major')
course_table = dynamodb.Table('courses')

@lru_cache
def get_major(major):
    response = major_table.get_item(
    Key={
        'major': major,
        'degree':  major[-4:]
    }
    )
    if response.get('Item') is None:
        return None
    item = response['Item']
    return item

@lru_cache
def get_course(course):
    response = course_table.get_item(
    Key={
        'course': course,
    }
    )
    if response.get('Item') is None:
        return None
    item = response['Item']
    return item
