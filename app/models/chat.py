from mongoengine import Document, StringField, ListField, DictField, DateTimeField
from datetime import datetime

class Chat(Document):
    user_id = StringField(required=True)
    context_id = StringField(required=True)
    messages = ListField(DictField(), default=[])
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)
    ttl = DateTimeField(default=datetime.utcnow)

    meta = {
        'collection': 'chats',
        'indexes': [
            {'fields': ['ttl'], 'expireAfterSeconds': 0}
        ]
    }
