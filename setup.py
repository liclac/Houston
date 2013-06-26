from houston import *
from getpass import getpass

print "WARNING: If you had an existing database, it'll be wiped. Completely."
if not raw_input("Type 'y' or 'yes' to continue: ") in ['y', 'yes']:
	exit()

print "---> Setting up database..."
db.drop_all()
db.create_all()

print "---> Create an Admin account"
user = User()
user.username = raw_input("Username: ")
user.set_password(getpass("Password: "))
user.name = raw_input("Name: ")
user.email = raw_input("Email: ")
user.is_admin = True
db.session.add(user)
db.session.commit()

print "---> Done!"
