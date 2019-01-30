import os
import datetime
import hashlib
from sqlalchemy.orm import validates
from flask import Flask
#from flask.ext.sqlalchemy import SQLAlchemy, models_committed
from flask_sqlalchemy import SQLAlchemy, models_committed
#from flask.ext.login import UserMixin
from flask_login import UserMixin
from flask_mail import Message

from serveus import app, mail, db

class UserType(db.Model):
	__tablename__ = 'usertype'

	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(80), unique=True)
	users = db.relationship('User', backref='usertype', lazy='dynamic')

	@staticmethod
	def get_administrator():
		return UserType.query.filter(UserType.name=='Administrator').first()

	@staticmethod
	def get_microscopist():
		return UserType.query.filter(UserType.name=='Medical Technologist').first()

	@staticmethod
	def get_doctor():
		return UserType.query.filter(UserType.name=='Validator').first()
	
	@staticmethod
	def get_labeler():
		return UserType.query.filter(UserType.name=='Labeler').first()
	
	@staticmethod
	def get_localadmin():
		return UserType.query.filter(UserType.name=='Local Administrator').first()
	
	def __init__(self, name=""):
		self.name = name
	
	def __repr__(self):
		return '<UserType %r>' % self.name
		
	def __str__(self):
		return self.name

class User(db.Model, UserMixin):
	__tablename__ = 'user'

	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(80), unique=True)
	password = db.Column(db.String(120))
	firstname = db.Column(db.String(100))
	lastname = db.Column(db.String(100))
	usertype_id = db.Column(db.Integer, db.ForeignKey('usertype.id'))
	case =  db.relationship('Case', backref='user', lazy='dynamic')
	contact = db.Column(db.String(80))
	email = db.Column(db.String(80), unique=True)
	chunklists = db.relationship('Chunklist', backref='user', lazy='dynamic')
	validations = db.relationship('Validation', backref='user', lazy='dynamic')
	test = db.Column(db.Boolean)

	"""
	@models_committed.connect_via(app)
	def on_models_committed(sender, changes):
		for obj, method in changes:
			if method == 'insert' and type(obj) == User:
				body = '''Greetings, %s %s! You have successfully been registered to the system. Your temporary password is <b>%s</b>.<br><br>Below are your account details:<br><br>Username: %s<br>User type: %s<br>Contact number: %s<br>Email: %s<br><br>Please login and change your password. Thank you!''' % (obj.firstname, obj.lastname, '123', obj.username, obj.usertype, obj.contact, obj.email)
				msg = Message('Outbreak Monitoring', sender="cvmig.group.23@gmail.com", recipients=['generic@mailinator.com',obj.email])
				msg.html = body
				mail.send(msg)
	"""


	@validates('password')
	def update_password(self, key, value):
		Database.query.first().modified = datetime.datetime.now()
		return value

	@staticmethod
	def hash_password(password):
		return hashlib.sha1(password).hexdigest()

	def is_administrator(self):
		return self.usertype == UserType.get_administrator()

	def is_microscopist(self):
		return self.usertype == UserType.get_microscopist()

	def is_doctor(self):
		return self.usertype == UserType.get_doctor()

	def is_labeler(self):
		return self.usertype == UserType.get_labeler()

	def is_localadmin(self):
		return self.usertype == UserType.get_localadmin()


	def __init__(self, firstname="", lastname="", username="", password="", contact="", email=""):
		self.firstname = firstname
		self.lastname = lastname
		self.username = username
		self.password = password
		self.contact = contact
		self.email = email
	def __repr__(self):
		return '<User %r %r (%r)>' % (self.firstname, self.lastname, self.username)
		
	def __str__(self):
		return self.username

# Diagnosis (aka Parasite) no longer per Case (it is per image patch now) AIM 01/2016
class Case(db.Model):
	__tablename__ = 'case'

	id = db.Column(db.Integer, primary_key=True)
	date = db.Column(db.DateTime())
	# parasite = db.Column(db.String(100))
	description = db.Column(db.String(1000))
	comment = db.Column(db.String(1000))
	lat = db.Column(db.Float)
	lng = db.Column(db.Float)
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
	images = db.relationship('Image', backref='case', lazy='dynamic')
	test = db.Column(db.Boolean)
	# partype_id = db.Column(db.Integer, db.ForeignKey('partype.id'))
	infection_id = db.Column(db.Integer, db.ForeignKey('infection.id'))
	region_id = db.Column(db.Integer, db.ForeignKey('region.id'))
	province_id = db.Column(db.Integer, db.ForeignKey('province.id'))
	municipality_id = db.Column(db.Integer, db.ForeignKey('municipality.id'))
	chunklist_id = db.Column(db.Integer, db.ForeignKey('chunklist.id'))
	parasite_validator = db.Column(db.String(100))
	description_validator = db.Column(db.String(1000))
	patient_id = db.Column(db.String(100))
	validations = db.relationship('Validation', backref='case', lazy='dynamic')

	# def __init__(self, date="", partype="", description="", lat="", lng="", test="", region="", province="", municipality="", patient_id=""):
	def __init__(self, date="", description="", lat="", lng="", test="", region="", province="", municipality="", infection=""):
		self.date = date
		self.description = description
		self.lat = lat
		self.lng = lng
		self.test = test
		if region == '':
			self.region = None
		else:
			self.region = region
		if province == '':
			self.province = None
		else:
			self.province = province
		if municipality == '':
			self.municipality = None
		else:
			self.municipality = municipality
		if infection == '':
			self.infection = None
		else:
			self.infection = infection
		
		# if partype == '':
		#	self.partype = None
		# else:
		#	self.partype = partype
		# if patient_id == '':
		#	self.patient_id = None
		# else:
		#	self.patient_id = patient_id

	def __repr__(self):
		return '<Case %r>' % self.id

	def __str__(self):
		return str(self.id)

	@property
	def code(self):
		return "%s-%s-%s" % (self.region.code, self.province.code, self.id)
	
	@property
	def duration(self):
		if self.chunklist:
			return self.chunklist.duration
		else:
			return 'Not recorded'

	@property
	def final_validation(self):
		return Validation.query.filter(Validation.final==True, Validation.case==self).first()
	
	@property
	def finalized(self):
		return self.final_validation != None

	@property
	def finalized_text(self):
		return "Done" if self.finalized else "Pending"

	@property
	def validator(self):
		validation = self.final_validation
		if validation:
			return validation.user
		return None

	@property
	def validator_contacts(self):
		validator = self.validator
		if validator:
			return "%s / %s" % (validator.contact, validator.email)
		return None


class Image(db.Model):
	__tablename__ = 'image'

	id = db.Column(db.Integer, primary_key=True)
	case_id = db.Column(db.Integer, db.ForeignKey('case.id'))
	im = db.Column(db.BLOB)
	number = db.Column(db.Integer)
	patches = db.relationship('Patch', backref='image', lazy='dynamic')
	# images are labeled/tagged by several labelers
	# is_tagged = db.Column(db.Boolean, default=False)

	'''
	def __init__(self, path="", case=""):
		with open(path, 'r') as f:
			self.im = f.read()
		self.case = case
	'''
	def create_image(self, path="", case=""):
		with open(path, 'rb') as f:
			self.im = f.read()
		self.case = case

	def __repr__(self):
		return '<Image %r>' % self.id

class Database(db.Model):
	__tablename__ = 'database'

	id = db.Column(db.Integer, primary_key=True)
	modified = db.Column(db.DateTime())

	def __init__(self):
		self.modified = datetime.datetime.now()
	
	@staticmethod
	def need_update(app_db_date):
		year, month, day, hours, minutes, seconds = map(int, app_db_date.split('-'))
		return Database.query.first().modified > datetime.datetime(year, month, day, hours, minutes, seconds)

	def __repr__(self):
		return '<Database %r>' % self.id

# ParType is now Results/Diagnosis AIM 11/2015
# Diagnosis (aka Parasite Type) per image patch AIM 01/2016
class ParType(db.Model):
    __tablename__ = 'partype'

    id = db.Column(db.Integer, primary_key=True)
    infection_id = db.Column(db.Integer, db.ForeignKey('infection.id'))
    name = db.Column(db.String(80))
    negative = db.Column(db.Boolean())
    patches = db.relationship('Patch', backref='partype', lazy='dynamic') 
    
    def __init__(self, name="", infection="", negative=0):
    	self.name = name
        self.infection = infection
        self.negative = negative
    
 
    @property
    def type(self):
        return self.name 
  
    def __repr__(self):
        return self.name
    
    def __str__(self):
    	return self.name

class Infection(db.Model):
    __tablename__ = 'infection'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))
    specimen_type = db.Column(db.String(80))
    diagnoses = db.relationship('ParType', backref='infection', lazy='dynamic')
    cases = db.relationship('Case', backref='infection', lazy='dynamic')

    def __init__(self, name, specimen_type):
        self.name = name
	self.specimen_type = specimen_type

    def __repr__(self):
        return self.name

class Patch(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	image_id = db.Column(db.Integer, db.ForeignKey('image.id'))
	xcoord = db.Column(db.Integer)
	ycoord = db.Column(db.Integer)
	radius = db.Column(db.Integer)
	partype_id = db.Column(db.Integer, db.ForeignKey('partype.id'))

	def __init__(self, image_id="", xcoord="", ycoord="", radius=""):
		self.xcoord = xcoord
		self.ycoord = ycoord
		self.radius = radius
		
	def __repr__(self):
		return '<Patch %r>' % self.id

class Key(db.Model):
	__tablename__ = 'key'

	id = db.Column(db.Integer, primary_key=True)
	private_key = db.Column(db.String(2000))
	public_key = db.Column(db.String(2000))

	def __init__(self, private_key, public_key):
		self.private_key = private_key
		self.public_key = public_key
	
	def __repr__(self):
		return str(self.public_key)

class Chunklist(db.Model):
	__tablename__ = 'chunklist'

	id = db.Column(db.Integer, primary_key=True)
	filename = db.Column(db.String(100))
	date = db.Column(db.DateTime())
	end_time = db.Column(db.DateTime())
	chunks = db.relationship('Chunk', backref='chunklist', lazy='dynamic')
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
	case = db.relationship('Case', backref='chunklist', uselist=False)

	def __init__(self, filename='', date='', user_id=''):
		self.filename = filename
		self.date = date.replace(microsecond=0)
		self.user_id = user_id
	
	def set_done(self, case):
		self.case = case
		self.end_time = datetime.datetime.now().replace(microsecond=0)
	
	@property
	def validation_filename(self):
		return '_'.join(self.filename.split('_')[:3])
	
	@property
	def duration(self):
		if self.end_time:
			return str(self.end_time - self.date)
		else:
			return "Not done"
	
	def __repr__(self):
		return self.filename

class Chunk(db.Model):
	__tablename__ = 'chunk'

	id = db.Column(db.Integer, primary_key=True)
	filename = db.Column(db.String(100))
	checksum = db.Column(db.String(50))
	done = db.Column(db.Boolean())
	chunklist_id = db.Column(db.Integer, db.ForeignKey('chunklist.id'))

	def __init__(self, filename='', checksum='', user=''):
		self.filename = filename
		self.checksum = checksum
		self.user = user
		self.done = False
		self.data = None
	
	def __repr__(self):
		return self.filename

class Region(db.Model):
	__tablename__ = 'region'

	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(50))
	code = db.Column(db.String(10))
	cases = db.relationship('Case', backref='region', lazy='dynamic')
	provinces = db.relationship('Province', backref='region', lazy='dynamic')

	def __init__(self, name='', code=''):
		self.name = name
		self.code = code
	
	def __repr__(self):
		return self.name

class Province(db.Model):
	__tablename__ = 'province'

	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(50))
	code = db.Column(db.String(10))
	cases = db.relationship('Case', backref='province', lazy='dynamic')
	municipalities = db.relationship('Municipality', backref='province', lazy='dynamic')
	region_id = db.Column(db.Integer, db.ForeignKey('region.id'))

	def __init__(self, name='', code=''):
		self.name = name
		self.code = code
	
	def __repr__(self):
		return self.name

	@property
	def serialize(self):
		return {'id': self.id, 'name': self.name}

class Municipality(db.Model):
	__tablename__ = 'municipality'

	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(50))
	cases = db.relationship('Case', backref='municipality', lazy='dynamic')
	province_id = db.Column(db.Integer, db.ForeignKey('province.id'))

	def __init__(self, name=''):
		self.name = name
	
	def __repr__(self):
		return self.name

	@property
	def serialize(self):
		return {'id': self.id, 'name': self.name}

class Validation(db.Model):
    __tablename__ = 'validation'
    
    id = db.Column(db.Integer,primary_key=True)
    diagnosis = db.Column(db.String(100))
    remarks = db.Column(db.String(1000))
    case_id = db.Column(db.Integer, db.ForeignKey('case.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    final = db.Column(db.Boolean)
    date = db.Column(db.DateTime())
    
    def __init__(self, user='', case='', diagnosis='', remarks='', final=False):
        self.user = user
        self.case = case
        self.diagnosis = diagnosis
        self.remarks = remarks
        self.final = final
        self.date = datetime.datetime.now().replace(microsecond=0)

