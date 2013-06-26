from flask.ext.login import current_user
from flask.ext.admin.contrib.sqlamodel import ModelView
from models import *

class HoustonModelView(ModelView):
	model = None
	
	def __init__(self, session):
		super(HoustonModelView, self).__init__(self.model, session)
	
	def is_accessible(self):
		return current_user.is_authenticated() and current_user.is_admin

class ProjectAdminView(HoustonModelView):
	model = Project
	column_exclude_list = ['slug']

class UserAdminView(HoustonModelView):
	model = User
	column_exclude_list = ['password']

class IssueAdminView(HoustonModelView):
	model = Issue
