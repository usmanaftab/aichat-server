from app import db
from datetime import datetime
from passlib.hash import pbkdf2_sha256

class User(db.Document):
    email = db.EmailField(required=True, unique=True)
    password_hash = db.StringField()
    first_name = db.StringField(max_length=50)
    last_name = db.StringField(max_length=50)
    is_active = db.BooleanField(default=True)
    created_at = db.DateTimeField(default=datetime.utcnow)
    reset_password_token = db.StringField()
    reset_password_expires = db.DateTimeField()
    oauth_provider = db.StringField()
    oauth_id = db.StringField()

    def set_password(self, password):
        self.password_hash = pbkdf2_sha256.hash(password)

    def check_password(self, password):
        return pbkdf2_sha256.verify(password, self.password_hash)

    def to_dict(self):
        return {
            'id': str(self.id),
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'created_at': self.created_at.isoformat()
        }
