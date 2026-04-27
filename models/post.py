# models/post.py
from models.database import db
from models.base import BaseModel
from datetime import datetime

class Post(BaseModel):
    __tablename__ = 'posts'
    
    # These columns inherit id, created_at, updated_at from BaseModel
    username = db.Column(db.String(80), nullable=False)
    image = db.Column(db.String(200))
    caption = db.Column(db.String(500))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    user = db.relationship('User', back_populates='posts')
    
    def __init__(self, username, image, caption):
        self.username = username
        self.image = image
        self.caption = caption
        # timestamp will auto-set from default value
    
    def __repr__(self):
        return f'<Post {self.id} by {self.username}>'
    
    # OOP Methods for better encapsulation
    def to_feed_dict(self):
        """Convert post to dictionary for feed display"""
        return {
            "username": self.username,
            "content": self.caption,
            "image_url": self.image,
            "time": self.timestamp.strftime("%I:%M %p") if self.timestamp else "",
            "type": "body"
        }
    
    def to_dict(self):
        """Convert post to complete dictionary (for API/serialization)"""
        return {
            "id": self.id,
            "username": self.username,
            "content": self.caption,
            "image_url": self.image,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
    
    def update_caption(self, new_caption):
        """Update post caption with validation"""
        if new_caption and len(new_caption) <= 500:
            self.caption = new_caption
            self.save_to_db()
            return True
        return False
    
    @classmethod
    def get_feed_posts(cls, limit=None):
        """Get all posts ordered by newest first for the feed"""
        query = cls.query.order_by(cls.timestamp.desc())
        if limit:
            query = query.limit(limit)
        return query.all()
    
    @classmethod
    def get_posts_by_user(cls, username):
        """Get posts by specific username"""
        return cls.query.filter_by(username=username).order_by(cls.timestamp.desc()).all()
    
    @classmethod
    def get_recent_posts(cls, hours=24):
        """Get posts from the last X hours"""
        from datetime import datetime, timedelta
        recent_time = datetime.utcnow() - timedelta(hours=hours)
        return cls.query.filter(cls.timestamp >= recent_time).order_by(cls.timestamp.desc()).all()
    
    def has_media(self):
        """Check if post has image/video"""
        return bool(self.image)
    
    def get_summary(self, length=100):
        """Get shortened caption for previews"""
        if len(self.caption) <= length:
            return self.caption
        return self.caption[:length] + "..."