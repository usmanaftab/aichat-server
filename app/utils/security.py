import secrets

def generate_reset_token(length=32):
    return secrets.token_urlsafe(length)
