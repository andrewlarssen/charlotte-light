import json

def lambda_handler(event, context):
    return {
        'statusCode': 200,
        'body': json.dumps({
            "access_token":"Atza|TOKEN12345",
            "token_type":"bearer",
            "expires_in":3600,
            "refresh_token":"Atzr|REFRESH12345"
        })
    }