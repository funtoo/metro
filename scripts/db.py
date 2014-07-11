#!/usr/bin/python3

'''

This module is a fourth attempt at some clean design patterns for encapsulating
SQLAlchemy database objects, so that they can more easily be embedded in other
objects. This code takes advantage of the SQLAlchemy ORM but purposely DOES NOT
USE SQLAlchemy's declarative syntax.  This is intentional because I've come to
the conclusion (after using declarative for a long time) that it's a pain in
the butt, not well documented, and hides a lot of the power of SQLAlchemy, so
it's a liability to use it.

Instead of using a declarative_base, database objects are simply derived from
object,and contain a _mapTable() method.  This method creates the Table object
and maps this new table to the class. This method is called by the Database
object when it is initialized:

orm = Database([User])

Above, we create a new Database object (to hold metadata, engine and session
information,) and we pass it a list or tuple of all objects to include as part
of our Database. Above, when Database's __init__() method is called, it will ensure
that the User class' _mapTable() method is called, so that the User table is
associated with our Database, and that these tables are created in the underlying
metadata.

This design pattern is created to allow for the creation of a library of
different kinds of database-aware objects, such as our user object. Then, other
code can import this code, and create a database schema with one or more of
these objects very easily:

orm = Database([Class1, Class2, Class3])

Classes that should be part of the Database can be included, and those that we
don't want can be omitted.

We could also create two or more schemas:

user_db = Database([User])
user_db.associate(engine="sqlite:///users.db")

product_db = Database([Product, ProductID, ProductCategory])
product_db.associate(engine="sqlite:///products.db")

tmp_db = Database([TmpObj, TmpObj2])
tmp_db.associate(engine="sqlite:///:memory:")

Or two different types of User objects:

class OtherUser(User):
	pass

user_db = Database([User])
other_user_db = Database([OtherUser])

Since all the session, engine and metadata stuff is encapsulated inside the
Database instances, this makes it a lot easier to use multiple database engines
from the same source code. At least, it provides a framework to make this a lot
less confusing:

for u in userdb.session.Query(User).all():
	print u

'''
import logging
from sqlalchemy import *
from sqlalchemy.orm import *
from sqlalchemy.ext.orderinglist import ordering_list

logging.basicConfig(level=logging.DEBUG)

class DatabaseError(Exception):
	def __init__(self, value):
		self.value = value
	def __str__(self):
		return self.value

'''
dbobject is a handy object to use as a base class for your database-aware objects. However,
using it is optional. It is perfectly OK to subclass a standard python new-style object.
'''

class dbobject(object):
	def __init__(self,id=None):
		self.id = id
	def __repr__(self):
		return "%s(%s)" % (self.__class__.__name__, self.id)
	@classmethod
	def _mapTable(cls,db):
		mapper(cls, cls.__table__, primary_key=[cls.__table__.c.id])

class Database(object):

	def __init__(self,objs=[],engine=None):
		self._dbobj = objs 
		self._tables = {}
		self.engine = None
		self._session = None
		self._autodict = {}
		self.metadata = MetaData()
		self.sessionmaker = None
		if engine != None:
			self.associate(engine)

	def autoName(self,name):
		if name not in self._autodict:
			self._autodict[name] = 0
		self._autodict[name] += 1
		return name % self._autodict[name]
	
	def IntegerPrimaryKey(self,name):
		return Column(name, Integer, Sequence(self.autoName("id_seq_%s"), optional=True), primary_key=True)

	def UniqueString(self,name,length=80,index=True, nullable=False):
		return Column(name, String(length), unique=True, index=index, nullable=nullable)

	def associate(self,engine="sqlite:///:memory:"):
		self.engine = create_engine(engine)
		self.metadata.bind = self.engine
		self.initORM()
		self.initSession()
		self.createDatabaseTables()

	def initORM(self):
		for cls in self._dbobj:
			cls._makeTable(self)
		for cls in self._dbobj:
			cls._mapTable(self)

	def createDatabaseTables(self):
		self.metadata.create_all()

	def initSession(self):
		self.sessionmaker = sessionmaker(bind=self.engine)

	@property
	def session(self):
		if self.sessionmaker == None:
			raise DatabaseError("Database not associated with engine")
		if self._session == None:
			self._session = scoped_session(self.sessionmaker)
		return self._session

