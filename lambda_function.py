import awsgi
from app import create_app

app = create_app()


def lambda_handler(event, context):
    """AWS Lambda entry point for the Flask application."""
    return awsgi.response(app, event, context)
