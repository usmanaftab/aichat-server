from datetime import datetime, timedelta
from app import db

class RequestQuota(db.Document):
    user_id = db.StringField(required=True)
    request_count = db.IntField(default=0)
    last_reset = db.DateTimeField(default=datetime.utcnow)
    
    meta = {
        'collection': 'request_quotas',
        'indexes': [
            {'fields': ['user_id'], 'unique': True}
        ]
    }
    
    @classmethod
    def get_remaining_requests(cls, user_id: str) -> int:
        MAX_REQUESTS = 15
        quota = cls.objects(user_id=user_id).first()
        
        if not quota:
            return MAX_REQUESTS
            
        # Reset count if it's a new day
        if datetime.utcnow().date() > quota.last_reset.date():
            quota.request_count = 0
            quota.last_reset = datetime.utcnow()
            quota.save()
            
        return max(0, MAX_REQUESTS - quota.request_count)
    
    @classmethod
    def increment_request_count(cls, user_id: str) -> bool:
        MAX_REQUESTS = 15
        quota = cls.objects(user_id=user_id).first()
        
        if not quota:
            quota = cls(user_id=user_id)
            
        # Reset count if it's a new day
        if datetime.utcnow().date() > quota.last_reset.date():
            quota.request_count = 0
            quota.last_reset = datetime.utcnow()
            
        # Check if quota exceeded
        if quota.request_count >= MAX_REQUESTS:
            return False
            
        quota.request_count += 1
        quota.save()
        return True 