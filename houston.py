import os, re
from flask import Flask, g, request
from flask import render_template, url_for, redirect, abort, flash
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.login import LoginManager, login_user, logout_user, current_user
from jinja2 import evalcontextfilter, Markup, escape
import markdown2

import relative_time
from models import User, Project, Issue, get_available_projects
from forms import LoginForm, RegisterForm, IssueForm

ROOT = os.path.abspath(os.path.dirname(__file__))
path = lambda p: os.path.join(ROOT, p)

# -- Flask
app = Flask(__name__)
app.secret_key = 'unVtpA4Brb0Vn3BuhxMd4tLTQ0EhDNLugu3wHBcs9XEwN6b36F'
#app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + path('db.sqlite')

# -- Database
from models import db
db.init_app(app)
db.app = app # Workaround for a bug in Flask-SQLAlchemy

# -- Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(userid):
	return User.query.filter_by(id=userid).first()

# -- View Misc
@app.context_processor
def inject_projects():
	return {
		'projects': get_available_projects(current_user)
	}

_paragraph_re = re.compile(r'(?:\r\n|\r|\n){2,}')
@app.template_filter()
@evalcontextfilter
def nl2br(eval_ctx, value):
	result = u'\n\n'.join(u'<p>%s</p>' % p.replace('\n', '<br>\n') \
		for p in _paragraph_re.split(escape(value)))
	if eval_ctx.autoescape:
		result = Markup(result)
	return result

@app.template_filter('markdown')
@evalcontextfilter
def markdown_filter(eval_ctx, s):
	result = markdown2.markdown(s)
	return result if not eval_ctx.autoescape \
			else Markup(result)

@app.template_filter()
def relative_timestamp(timestamp):
	return relative_time.get_age(timestamp)

# -- Views
@app.errorhandler(403)
def handle_403(e):
	return redirect(url_for('login'))

@app.route('/')
def home():
	return render_template('home.html')

@app.route('/login/', methods=['GET', 'POST'])
def login():
	form = LoginForm()
	login_error = False
	if form.validate_on_submit():
		user = User.query.filter_by(username=form.username.data).first()
		if user and user.verify_password(form.password.data):
			login_user(user, remember=form.remember_me.data)
			return redirect(url_for('home'))
		else:
			login_error = True
	return render_template('login.html', form=form, login_error=login_error)

@app.route('/register/', methods=['GET', 'POST'])
def register():
	form = RegisterForm()
	if form.validate_on_submit():
		if(User.query.filter_by(username=form.username.data).count() > 0):
			form.username.errors.append("Username is already in use")
		else:
			user = User(form.name.data, form.username.data, form.password.data, form.email.data)
			db.session.add(user)
			db.session.commit()
			login_user(user, remember=False)
			return redirect(url_for('home'))
	return render_template('register.html', form=form)

@app.route('/logout/')
def logout():
	logout_user()
	return redirect(url_for('home'))

@app.route('/users/<username>/')
def user(username):
	user = User.query.filter_by(username=username).first_or_404()
	return render_template('user.html', user=user)

@app.route('/users/<username>/projects/')
def user_projects(username):
	user = User.query.filter_by(username=username).first_or_404()
	return render_template('user_projects.html', user=user)

@app.route('/users/<username>/reports/')
def user_reports(username):
	user = User.query.filter_by(username=username).first_or_404()
	return render_template('user_reports.html', user=user)

@app.route('/projects/<slug>/')
def project(slug):
	project = Project.query.filter_by(slug=slug).first_or_404()
	return render_template('project.html', project=project)

@app.route('/projects/<slug>/<iid>/')
def project_issue(slug, iid):
	issue = Issue.query.get_or_404(iid)
	if slug != issue.project.slug:
		return redirect(url_for('issue', slug=issue.project.slug, iid=issue.id))
	if not issue.is_allowed(current_user):
		abort(403)
	return render_template('issue.html', issue=issue)

@app.route('/projects/<slug>/new/', methods=['GET', 'POST'])
def project_issue_new(slug):
	form = IssueForm()
	project = Project.query.filter_by(slug=slug).first_or_404()
	if form.validate_on_submit():
		issue = Issue(project, current_user, form.urgency.data,
						form.title.data, form.text.data)
		db.session.add(issue)
		db.session.commit()
		flash("Created issue <a href=\"%s\">#%s</a>" %
				(url_for('project_issue', slug=project.slug, iid=issue.id), issue.id))
		return redirect(url_for('project_issue_new', slug=slug))
	return render_template('issue_new.html', project=project, form=form)

@app.route('/issues/<iid>/')
def issue(iid):
	issue = Issue.query.get_or_404(iid)
	return redirect(url_for('project_issue', slug=issue.project.slug, iid=issue.id))

if __name__ == '__main__':
	app.run(debug=True)
