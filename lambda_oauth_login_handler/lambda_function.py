import json
import os

def lambda_handler(event, context):
    # print(event)
    # print(os.environ)
    # print(context)

    state = event['queryStringParameters']['state']

    skill_link_id = os.environ.get('skill_link_id')
    skill_code = os.environ.get('skill_code')

    url = f'https://layla.amazon.com/api/skill/link/{skill_link_id}?state={state}&code={skill_code}'
    return {
        'statusCode': 301,
        'body': f'<a href="{url}">redirect</a>',
        'headers': {
            'Location': url
        }
    }
