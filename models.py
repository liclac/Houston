import re
from datetime import datetime
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.login import UserMixin
from passlib.apps import custom_app_context as pwd_context

db = SQLAlchemy()

project_members = db.Table('project_members',
	db.Column('project_id', db.Integer, db.ForeignKey('project.id')),
	db.Column('user_id', db.Integer, db.ForeignKey('user.id'))
)

class User(db.Model, UserMixin):
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(15), unique=True)
	password = db.Column(db.String(120))
	name = db.Column(db.String(20))
	email = db.Column(db.String(255))
	
	is_admin = db.Column(db.Boolean())
	
	def __init__(self, username='', password='', name='', email=''):
		self.username = username
		self.set_password(password)
		self.name = name
		self.email = email
	
	def set_password(self, password):
		self.password = pwd_context.encrypt(password)
	
	def verify_password(self, password):
		return pwd_context.verify(password, self.password)
	
	def __str__(self):
		return "@%s" % self.username

class Project(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	
	name = db.Column(db.String(100), unique=True)
	slug = db.Column(db.String(100), unique=True)
	description = db.Column(db.Text())
	public = db.Column(db.Boolean)
	started = db.Column(db.DateTime)
	
	owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))
	owner = db.relationship('User', backref=db.backref('created_projects', lazy='dynamic'))
	members = db.relationship('User', secondary=project_members, backref=db.backref('projects', lazy='dynamic'))
	
	def __init__(self, owner='', public='', name='', description=''):
		self.public = public
		self.owner = owner
		self.started = datetime.now()
		self.name = name
		self.description = description
		self.generate_slug()
	
	def generate_slug(self):
		self.slug = re.sub("[^ \w]", '', self.name).replace(' ', '-').lower()
	
	def is_allowed(self, user):
		return self.public or self.owner == user
	
	def __str__(self):
		return self.name

class Issue(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	
	title = db.Column(db.String(140))
	text = db.Column(db.Text())
	urgency = db.Column(db.Integer())
	
	project_id = db.Column(db.Integer, db.ForeignKey('project.id'))
	project = db.relationship('Project', backref=db.backref('issues', lazy='dynamic'))
	spotter_id = db.Column(db.Integer, db.ForeignKey('user.id'))
	spotter = db.relationship('User', backref=db.backref('reports', lazy='dynamic'))
	spotted = db.Column(db.DateTime)
	
	urgencies = [
		"Wishlist",
		"No hurry at all",
		"Not too important",
		"Normal importance",
		"Pretty important",
		"ON FIRE!"
	]
	
	def __init__(self, project, spotter, urgency, title, text):
		self.project = project
		self.spotter = spotter
		self.spotted = datetime.now()
		self.urgency = urgency
		self.title = title
		self.text = text
	
	def is_allowed(self, user):
		return self.project.is_allowed(user)
	
	def __str__():
		return "#%s" % self.id

def get_available_projects(user):
	if user.is_anonymous():
		return Project.query.filter(Project.public == True).all()
	else:
		return Project.query.filter((Project.public==True) | (Project.owner == user)).all()
