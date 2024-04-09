import os
import json
import boto3

ddb = boto3.resource('dynamodb', region_name = 'eu-west-1').Table('url-shortener-table')

def lambda_handler(event, context):
    short_id = event.get('short_id')

    try:
        item = ddb.get_item(Key={'short_id': short_id}) #look up the take the short id value in dynamo
        long_url = item.get('Item').get('long_url') #take the long_url value corresponding to the short id
        # increase the hit number on the db entry of the url (analytics?)
        ddb.update_item(
            Key={'short_id': short_id},
            UpdateExpression='set hits = hits + :val',
            ExpressionAttributeValues={':val': 1}
        )

    except:
        return {
            'statusCode': 301,
            'location': 'https://example.com/notfound'
        }
    
    #return long_url and the redirection http status code 301
    return {
        "statusCode": 301,
        "location": long_url
    }