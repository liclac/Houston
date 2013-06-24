from houston import *
from getpass import getpass

print "WARNING: If you had an existing database, it'll be wiped. Completely."
if not raw_input("Type 'y' or 'yes' to continue: ") in ['y', 'yes']:
	exit()

print "Setting up database..."
db.drop_all()
db.create_all()

print "-- Create an Admin account --"
name = raw_input("Name: ")
email = raw_input("Email: ")
username = raw_input("Username: ")
password = getpass("Password: ")
user = User(name, email, username, password)
user.is_admin = True
db.session.add(user)
db.session.commit()

print "-----------------------------"
print "--> Done!"
