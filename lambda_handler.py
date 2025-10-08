from app import create_app
from mangum import Mangum
import os

app = create_app()
base_handler = Mangum(app, lifespan="off")


def handler(event, context):
    # Call the base handler
    response = base_handler(event, context)

    # Add CORS headers to every response
    allowed_origins = os.getenv('ALLOWED_ORIGINS', '*').split(',')
    origin = event.get('headers', {}).get(
        'origin') or event.get('headers', {}).get('Origin')

    # If request origin matches any allowed origin, use that specific origin
    if origin and '*' not in allowed_origins:
        if origin in allowed_origins:
            response['headers']['Access-Control-Allow-Origin'] = origin
    else:
        # If no matching origin or wildcard is allowed, use the first allowed origin or '*'
        response['headers']['Access-Control-Allow-Origin'] = allowed_origins[0] if allowed_origins else '*'

    response['headers']['Access-Control-Allow-Credentials'] = 'true'
    response['headers']['Access-Control-Allow-Methods'] = 'GET,POST,PUT,DELETE,OPTIONS'
    response['headers']['Access-Control-Allow-Headers'] = 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token,Access-Control-Allow-Credentials'

    return response
