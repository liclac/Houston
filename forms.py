from flask.ext.wtf import Form
from wtforms import TextField, PasswordField, TextAreaField, BooleanField, SelectField, validators
from models import Issue

class LoginForm(Form):
	username = TextField(u'Username', validators=[validators.required()])
	password = PasswordField(u'Password', validators=[validators.required()])
	remember_me = BooleanField(u'Remember Me')

class IssueForm(Form):
	title = TextField(u'Title', validators=[validators.required(), validators.length(max=140)])
	urgency = SelectField(u'Urgency', coerce=int,
							choices=[(i, text) for i, text in enumerate(Issue.urgencies)], default=3)
	text = TextAreaField(u'Text', validators=[validators.DataRequired()], default=
			"Please describe the issue in as much detail as possible.\n"
			"Make sure to include:\n"
			"\n"
			"* Steps to reproduce\n"
			"* OS, browser, etc., with version where applicable\n"
			"\n"
			"Markdown is supported.")
