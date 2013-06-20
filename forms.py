from flask.ext.wtf import Form
from wtforms import TextField, PasswordField, TextAreaField, BooleanField, SelectField, validators
from models import Issue

class LoginForm(Form):
	username = TextField(u'Username', validators=[validators.required()])
	password = PasswordField(u'Password', validators=[validators.required()])
	remember_me = BooleanField(u'Remember Me')

class RegisterForm(Form):
	name = TextField(u'Name', validators=[validators.required()])
	username = TextField(u'Username', validators=[validators.required(), validators.length(1, 20)])
	password = PasswordField(u'Password', validators=[validators.required()])
	email = TextField(u'Email', validators=[validators.required(), validators.length(1, 255), validators.email()])

class IssueForm(Form):
	title = TextField(u'Title', validators=[validators.required(), validators.length(max=140)])
	urgency = SelectField(u'Urgency', coerce=int,
							choices=[(i, "%i - %s" % (i, text)) for i, text in enumerate(Issue.urgencies)], default=3)
	text = TextAreaField(u'Text', validators=[validators.DataRequired()])
