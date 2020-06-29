import random
from slugify import slugify
import string
from Social_Blog import db, login_manager
from datetime import datetime
from flask_login import UserMixin

@login_manager.user_loader
def load_user(user_id):
     return User.query.get(int(user_id))


class Follow(db.Model):
    __tablename__ = 'follows'
    follower_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    followed_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class User(db.Model, UserMixin):
    id = db.Column(db.Integer,primary_key=True)
    username = db.Column(db.String(20),unique=True,nullable=False)
    email = db.Column(db.String(40),unique=True,nullable=False)
    image_file = db.Column(db.String(20),nullable=False, default='default.jpg')
    bio = db.Column(db.String(120), nullable=False, default='Developer and Technical Writer')
    password = db.Column(db.String(60),nullable=False)
    posts = db.relationship('Post', backref='author', lazy=True)
    followed = db.relationship('Follow',foreign_keys=[Follow.follower_id],
                                backref=db.backref('follower',lazy='joined'),
                                lazy='dynamic',cascade='all, delete-orphan')
    followers = db.relationship('Follow',foreign_keys=[Follow.followed_id],
                                backref=db.backref('followed',lazy='joined'),
                                lazy='dynamic',cascade='all, delete-orphan')
    comments = db.relationship('Comment',backref='author',lazy='dynamic')
    
    def follow(self, user):
        if not self.is_following(user):
            f = Follow(follower=self, followed=user)
            db.session.add(f)
            db.session.commit()
            
    def unfollow(self,user):
        f = self.followed.filter_by(followed_id=user.id).first()
        if f:
            db.session.delete(f)
            db.session.commit()
    def is_followed_by(self, user):
        return self.followers.filter_by(follower_id=user.id).first() is not None
    def is_following(self, user):
        return self.followed.filter_by(followed_id=user.id).first() is not None

    
    @property
    def followed_posts(self):
            followed = Post.query.join(Follow, Follow.followed_id == Post.user_id).filter(Follow.follower_id == self.id)
            own = Post.query.filter_by(user_id=self.id)
            return followed.union(own)
    
     

    def __repr__(self):
        return f"User('{self.username}','{self.email}')"




class Post(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    title = db.Column(db.String(100),nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    content = db.Column(db.Text,nullable=False)
    slug = db.Column(db.String,unique=True,nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    comments = db.relationship('Comment',backref='post',lazy='dynamic')
    

    def create_slug(self):
        _ = ''.join(random.choices(string.ascii_lowercase + string.ascii_uppercase +
        string.digits, k=6))
        self.slug = '-'.join([slugify(self.title),_])
        
    def __repr__(self):
        return f"Post('{self.title}','{self.date_posted}')"

class Comment(db.Model):
    __tablename__ = 'comments'
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text)
    date_posted = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    disabled = db.Column(db.Boolean)
    author_id = db.Column(db.Integer,db.ForeignKey('user.id'))
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'))

    def __repr__(self):
        return f"Comment('{self.author_id}','{self.date_posted}')"