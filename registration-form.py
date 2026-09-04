import json
import boto3

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('registration-table')

CORS_HEADERS = {
    'Content-Type': 'application/json',
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Headers': 'Content-Type',
    'Access-Control-Allow-Methods': 'OPTIONS,POST'
}


def lambda_handler(event, context):
    # API Gateway (REST API / proxy integration) sends the payload as a
    # JSON string inside event['body']. Parse that safely.
    try:
        if 'body' in event and event['body'] is not None:
            body = json.loads(event['body'])
        elif isinstance(event, str):
            body = json.loads(event)
        else:
            # Fallback: event itself is already the payload (e.g. a
            # hand-crafted test event in the Lambda console)
            body = event
    except Exception:
        return {
            'statusCode': 400,
            'headers': CORS_HEADERS,
            'body': json.dumps({'message': 'Invalid JSON in request body'})
        }

    # Validate required fields
    required_fields = [
        'email', 'first_name', 'last_name', 'class_apply', 'dob',
        'parent_first_name', 'parent_last_name', 'address', 'city',
        'region', 'postal_code', 'country', 'phone', 'signature'
    ]
    missing = [f for f in required_fields if not body.get(f)]
    if missing:
        return {
            'statusCode': 400,
            'headers': CORS_HEADERS,
            'body': json.dumps({'message': f'Missing required field(s): {", ".join(missing)}'})
        }

    # Write to DynamoDB
    try:
        table.put_item(
            Item={
                'email': body['email'],
                'first_name': body['first_name'],
                'last_name': body['last_name'],
                'class_apply': body['class_apply'],
                'dob': body['dob'],
                'parent_first_name': body['parent_first_name'],
                'parent_last_name': body['parent_last_name'],
                'address': body['address'],
                'address2': body.get('address2', ''),
                'city': body['city'],
                'region': body['region'],
                'postal_code': body['postal_code'],
                'country': body['country'],
                'phone': body['phone'],
                'signature': body['signature']
            }
        )
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': CORS_HEADERS,
            'body': json.dumps({'message': 'Failed to register user', 'error': str(e)})
        }

    return {
        'statusCode': 200,
        'headers': CORS_HEADERS,
        'body': json.dumps({'message': 'Registration successful'})
    }
