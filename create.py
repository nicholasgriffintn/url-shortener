import os
import json
import boto3
from string import ascii_letters, digits
from random import choice, randint
from time import strftime, time
from urllib import parse

app_url = os.getenv('APP_URL') #The app_url will be your domain name, as this will be returned to the client with the short id
min_char = int(os.getenv('MIN_CHAR')) #min number of characters in short url unique string
max_char = int(os.getenv('MAX_CHAR')) #max number of characters in short url unique string
string_format = ascii_letters + digits

ddb = boto3.resource('dynamodb', region_name = 'eu-west-1').Table('url-shortener-table') #Set region and Dynamo DB table

def generate_timestamp():
    response = strftime("%Y-%m-%dT%H:%M:%S")
    return response

def expiry_date():
    response = int(time()) + int(604800) #generate expiration date for the url based on the timestamp
    return response

def check_id(short_id):
    if 'Item' in ddb.get_item(Key={'short_id': short_id}):
        response = generate_id()
    else:
        return short_id

def generate_id():
    short_id = "".join(choice(string_format) for x in range(randint(min_char, max_char))) #generate unique value for the short url
    print(short_id)
    response = check_id(short_id)
    return response

def lambda_handler(event, context):
    analytics = {}
    print(event)
    short_id = generate_id()
    short_url = app_url + short_id
    long_url = json.loads(event.get('body')).get('long_url')
    timestamp = generate_timestamp()
    ttl_value = expiry_date()

    analytics['user_agent'] = event.get('headers').get('User-Agent')
    analytics['source_ip'] = event.get('headers').get('X-Forwarded-For')
    analytics['xray_trace_id'] = event.get('headers').get('X-Amzn-Trace-Id')

    if len(parse.urlsplit(long_url).query) > 0:
        url_params = dict(parse.parse_qsl(parse.urlsplit(long_url).query))
        for k in url_params:
            analytics[k] = url_params[k]

    #put value in dynamodb table
    response = ddb.put_item(
        Item={
            'short_id': short_id,
            'created_at': timestamp,
            'ttl': int(ttl_value),
            'short_url': short_url,
            'long_url': long_url,
            'analytics': analytics,
            'hits': int(0)
        }
    )
    body_new = '{"short_id":"' +short_url+'","long_url":"'+long_url+'"}'
    return {"statusCode": 200,"body": body_new} #return the body with long and short url