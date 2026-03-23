from models.database import db
from sqlalchemy import UniqueConstraint, func

class Post(db.Model):
    __tablename__ = 'posts' 
    __table_args__ = (UniqueConstraint('username', 'timestamp', name='primary_key'),)
    user = db.relationship('User', back_populates='posts')


    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(80),db.ForeignKey('users.username'), nullable=False)
    timestamp = db.Column(db.DateTime, default=func.now(), nullable=False)
    image = db.Column(db.String(200), nullable=False)
    caption = db.Column(db.String(200), nullable=False)
    def __init__(self, username, image, caption):
        self.username = username
        self.image = image
        self.caption = caption

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def __repr__(self):
        return f'<post {self.username}>'
