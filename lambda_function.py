import json
import boto3
from decimal import Decimal

# 1. Database Connection
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('ProductInventory')

# 2. Number Helper (Decimal ko JSON banane ke liye)
class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super(DecimalEncoder, self).default(obj)

# 3. Main Logic
def lambda_handler(event, context):
    print("Received event:", json.dumps(event))
    
    method = event.get('httpMethod')
    
    # --- GET: Data Padhna ---
    if method == 'GET':
        # Case A: Kisi ek product ko dhoondna (?productId=123)
        if event.get('queryStringParameters') and 'productId' in event['queryStringParameters']:
            p_id = event['queryStringParameters']['productId']
            response = table.get_item(Key={'productId': p_id})
            item = response.get('Item')
            if item:
                return build_response(200, item)
            else:
                return build_response(404, {'Message': 'Product nahi mila'})
        
        # Case B: Saare products dikhana
        else:
            response = table.scan()
            items = response.get('Items', [])
            return build_response(200, items)

    # --- POST: Naya Data Daalna ---
    elif method == 'POST':
        try:
            body = json.loads(event['body'])
            table.put_item(Item=body)
            return build_response(200, {'Message': 'Success! Product saved.', 'Product': body})
        except Exception as e:
            return build_response(500, {'Error': str(e)})

    else:
        return build_response(400, {'Error': 'Method not allowed'})

# 4. Response Pack Karne Wala Function
def build_response(status_code, body):
    return {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        },
        'body': json.dumps(body, cls=DecimalEncoder)
    }
