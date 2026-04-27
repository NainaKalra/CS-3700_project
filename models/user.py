from models.database import db
from models.base import BaseModel

class User(BaseModel):
    __tablename__ = 'users' 
    
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    role = db.Column(db.String(50))
    posts = db.relationship('Post', back_populates='user')
    
    def __init__(self, username, role):
        self.username = username
        self.role = role


    def __repr__(self):
        return f'<User {self.username}>'
    



    # One idea to use encapsulation for is protecting data by preventing long bios. New function inside user class that checks length of bio.    
