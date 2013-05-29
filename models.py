import re
from datetime import datetime
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.login import UserMixin
from passlib.apps import custom_app_context as pwd_context

db = SQLAlchemy()

class User(db.Model, UserMixin):
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(15))
	password = db.Column(db.String(120))
	
	def __init__(self, username, password):
		self.username = username
		self.password = pwd_context.encrypt(password)
	
	def verify_password(self, password):
		return pwd_context.verify(password, self.password)

class Project(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	slug = db.Column(db.String(100), unique=True)
	public = db.Column(db.Boolean)
	owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))
	owner = db.relationship('User', backref=db.backref('projects', lazy='dynamic'))
	started = db.Column(db.DateTime)
	name = db.Column(db.String(100), unique=True)
	description = db.Column(db.Text())
	
	def __init__(self, owner, public, name, description):
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

class Issue(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	project_id = db.Column(db.Integer, db.ForeignKey('project.id'))
	project = db.relationship('Project', backref=db.backref('issues', lazy='dynamic'))
	spotter_id = db.Column(db.Integer, db.ForeignKey('user.id'))
	spotter = db.relationship('User', backref=db.backref('reports', lazy='dynamic'))
	spotted = db.Column(db.DateTime)
	urgency = db.Column(db.Integer())
	title = db.Column(db.String(140))
	text = db.Column(db.Text())
	
	urgencies = [
		"0 - Wishlist",
		"1 - No hurry at all",
		"2 - Not too important",
		"3 - Normal",
		"4 - Pretty important",
		"5 - ON FIRE!"
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

def get_available_projects(user):
	if user.is_anonymous():
		return Project.query.filter(Project.public == True).all()
	else:
		return Project.query.filter((Project.public==True) | (Project.owner == user)).all()
