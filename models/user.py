from models.database import db

class User(db.Model):
    __tablename__ = 'users' 
    
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    role = db.Column(db.String(50))
    posts = db.relationship('Post', back_populates='user')
    def __init__(self, username, role):
        self.username = username
        self.role = role

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def __repr__(self):
        return f'<User {self.username}>'
    
