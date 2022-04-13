from datetime import datetime # for recording post time
from werkzeug.security import generate_password_hash, check_password_hash # for password hashing
from flask_2019_app import db
from flask_login import UserMixin

from flask_2019_app import login # for user_loader function

@login.user_loader # allows flask_login to know what the id is 
def load_user(id):
	"""
	Since we will
	never be accessing this intermediary table directly (SQLAlchemy will
	handle it for us transparently), we will not create a model for it but will simply
	specify a table to store the mapping
	"""
    return user.query.get(int(id))

post_tags = db.Table('post_tags',
	db.Column('tag_id', db.Integer, db.ForeignKey('tag.id')),
	db.Column('post_id', db.Integer, db.ForeignKey('posts.id'))
	)

class user(UserMixin, db.Model):
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(64), index=True, unique=True)
	email = db.Column(db.String(120), index=True, unique=True)
	password_hash = db.Column(db.String(128))
	# backref (join)
	posts = db.relationship('posts', backref='author', lazy='dynamic')

	def __repr__(self):
		return '<User {}>'.format(self.username)   

	def set_password(self, password):
		self.password_hash = generate_password_hash(password)

	def check_password(self, password):
		return check_password_hash(self.password_hash, password)

class posts(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	title = db.Column(db.String(200), unique=True)
	title_urlify = db.Column(db.String(200))
	body = db.Column(db.Text)
	ingredients = db.Column(db.Text)
	published = db.Column(db.DateTime, default=datetime.utcnow)
	modified = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
	image_url = db.Column(db.Text)
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

	"""
	By specifying lazy='dynamic', we instruct SQLAlchemy that, instead
	of it loading all the associated entries for us, we want a Query object instead.
	This joins the tag/post_tags/posts tables
	"""
	tags = db.relationship('tag', secondary=post_tags,
		backref=db.backref('posts', lazy='dynamic'))

	def __repr__(self):
		return '<Post {}>'.format(self.title)

class tag(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(200), unique=True)

	def __repr__(self):
		return '<tag {}>'.format(self.name)