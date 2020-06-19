import random
from slugify import slugify
import string
from Social_Blog import db, login_manager
from datetime import datetime
from flask_login import UserMixin

@login_manager.user_loader
def load_user(user_id):
     return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer,primary_key=True)
    username = db.Column(db.String(20),unique=True,nullable=False)
    email = db.Column(db.String(40),unique=True,nullable=False)
    image_file = db.Column(db.String(20),nullable=False, default='default.jpg')
    bio = db.Column(db.String(120), nullable=False, default='Developer and Technical Writer')
    password = db.Column(db.String(60),nullable=False)
    posts = db.relationship('Post', backref='author', lazy=True)
     

    def __repr__(self):
        return f"User('{self.username}','{self.email}')"


class Post(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    title = db.Column(db.String(100),nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    content = db.Column(db.Text,nullable=False)
    slug = db.Column(db.String,unique=True,nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def create_slug(self):
        _ = ''.join(random.choices(string.ascii_lowercase + string.ascii_uppercase +
        string.digits, k=6))
        self.slug = '-'.join([slugify(self.title),_])
        
    def __repr__(self):
        return f"Post('{self.title}','{self.date_posted}')"
