#!/usr/bin/python

import os, sys

filename = None
lineno = None

class FlexDataError(Exception):
	def __init__(self, message, type="" ):
		if type:
			out="\nParser %s exception" % type
		else:
			out="\nParser exception"

		global filename
		global lineno
		global curline

		if filename:
			out += ", file '%s'" % filename
			if lineno:
				out += ", line %i:" % lineno
		if curline:
			out += "\n\tLine literal: '%s'" % curline
		if message:
			out += "\n\tReason: %s\n" % message
		else:
			out += "\n"
		print out

class conditionAtom:
	def __init__(self,value):
		# This filename and line records the line at which the condition was applied, not defined

		global filename
		global lineno

		self.value=value

		self.filename=filename
		self.lineno=lineno
		self.negated = False

	def negate(self):
		# For conditionAtoms, "negate" is a toggle
		self.negated = not self.negated
	
	def __repr__(self):
		if self.negated:
			return "cond: NOT '%s'" % self.value
		else:
			return "cond: '%s'" % self.value

class conditionGroup:
	def __init__(self,immutable=False):
		self.immutable=False
		self.clear()
		self.immutable=immutable
	def replace(self,catom):
		if self.immutable:
			raise FlexDataError
		self.list=[catom]
	def add(self,catom):
		if self.immutable:
			raise FlexDataError
		self.list.append(catom)
	def isEmpty(self):
		return self.list == []
	def clear(self):
		if self.immutable:
			raise FlexDataError
		self.list=[]
		self.negated=False
	def copy(self,immutable=False):
		newcg = conditionGroup()
		newcg.list = self.list
		newcg.negated = self.negated
		newcg.immutable=immutable
		return newcg
	def negate(self):
		# A negated condition is used for else: clauses - it negates the entire condition group.
		# There is currently no functionality to "un-negate" a condition as this isn't required
		# by Metro right now.
		if self.immutable:
			raise FlexDataError
		if self.negated:
			raise FlexDataError("Condition double-negation",type="internal")
		self.negated=True
	def __repr__(self):
		out = "cg:"
		if self.negated:
			out += " NOT ( "
		else:
			out += " ( "
		if len(self.list) == 0:
			out += "EMPTY"
		elif len(self.list) >= 1:
			out += repr(self.list[0])
			if len(self.list) >1:
				for item in self.list[1:]:
					out += " AND "+repr(item)
		return out+" )"

# we use this as the default "empty" condition group
cgempty = conditionGroup(immutable=True)

class metroCollection:
	def __init__(self):
		self.filelist=[]
		self.namespace = metroNameSpace()
		self.cq=[]
	def collect(self,filename):
		self.filelist.append(metroParsedFile(filename,self))
	def queue(self,filename):
		self.cq.append(filename)
class metroNameSpace:
	def __init__(self):
		self.elements={}
		# Structure of self.elements is:
		# {"varname" : { element-object:condition-group } 
		# Now would be a good time to add "else" clauses.....
	def add(self,element,cg):
		if not self.elements.has_key(element.name()):
			self.elements[element.name()]={}
		self.elements[element.name()][element] = cg	
	def debugDump(self):
		keys=self.elements.keys()
		keys.sort()
		for key in keys:
			print key+":"
			elkeys=self.elements[key].keys()
			for elkey in elkeys:
				print "\t"+repr(elkey)+": "+repr(self.elements[key][elkey])

class metroParsedFile:
	def __init__(self,filename,collection):
		self.filename = os.path.normpath(filename)
		self.namespace = collection.namespace
		self.collection = collection

		self.parse()
	
	def name(self):
		return self.filename

	def parse(self):

		# Using globals isn't always the best programming practice, but in our case of a single-threaded
		# parser, it is a handy way to allow various parts of the parser to access relevant information
		# without passing arguments all over the place.

		global cgempty
		global prevlineno
		global lineno
		global curline
		global filename
		
		filename = self.filename
		lineno = 0
		prevlineno = 0

		# By default, set our conditions to empty by referencing the default "empty" live conditiongroup object

		self.cg = cgempty

		# This function parses the high-level structure of the document, identifying data elements
		# and annotations, and creates appropriate internal objects and then adds them to the namespace.

		try:
			myfile=open(self.filename,"r")
		except:
			print "DEBUG: can't open file %s" % self.filename
			return
			#raise FlexDataError("Cannot open file %s" % self.filename)
		section = ""
		while 1:	
			try:
				curline = myfile.next()[:-1]
				lineno += 1
			except StopIteration:
				break
			mysplit = curline.strip().split(" ")

			# 1. Detect blank lines and skip them.

			if len(mysplit) == 1 and mysplit[0] == '':
				continue
			
			# 2. Detect comments and truncate mysplit appropriately
			
			spos = 0
			while spos < len(mysplit):
				if len(mysplit[spos]) and mysplit[spos][0] == "#":
					mysplit=mysplit[0:spos]
					break
				spos += 1
			
			# 3. If the line just included comments, move on to next line

			if len(mysplit) == 0:
				continue

			# 4. Identify and parse elements

			if len(mysplit) == 2 and mysplit[0][-1] == ":" and mysplit[1] == "[":
				
				# We have found a multi-line element. We will grab all the lines of this element and create a new multiLineElement object,
				# and add it to the namespace.
				
				prevlineno = lineno
				varname = mysplit[0:-1]
				mylines = []
				while 1:
					try:
						curline = myfile.next() 	
						lineno += 1
						mysplit = curline[:-1].strip().split(" ")
						if len(mysplit) == 1 and mysplit[0] == "]":
							# Add condition:multi-line element pair to namespace
							self.namespace.add(multiLineElement(self.section,varname,mylines),self.cg)
						else:
							mylines.append(curline)
					except StopIteration:
						raise FlexDataError("incomplete (unclosed) multi-line block (started on line %i)" % prevlineno )

			elif mysplit[0][0]=="[" and mysplit[-1][-1]=="]":
				if len(mysplit) == 0:
					raise FlexDataError("empty annotation")
				elif len(mysplit) == 1:
					insides = mysplit[0][1:-1]
				elif len(mysplit) == 2:
					insides = mysplit[0][1:] + " " + mysplit[1][:-1]
				else:
					insides = mysplit[0][1:] + " " + " ".join(mysplit[1:-1]) + " " + mysplit[-1][:-1]
				insidesplit = insides.split()

				# We have found an annotation. We will perform appropriate processing to handle the annotation correctly.

				if insidesplit[0] == "when":
					# Conditional annotation - create new live object, don't modify the old one!
					self.cg = conditionGroup()
					self.cg.add(conditionAtom(insides))
					self.cg.immutable = True
				elif insidesplit[0] in [ "+when", "-when" ]:
					# Compound conditional annotation - create a new live object to modify, in case the old cg was used
					self.cg = self.cg.copy()
					self.cg.add(conditionAtom(insides))
					self.cg.immutable = True
				elif insidesplit[0] == "else":
					self.cg = self.cg.copy()
					self.cg.negate()
					self.cg.immutable = True
				elif insidesplit[0] == "collect":
					# Collect annotation
					if len(insidesplit)==2:
						self.collection.queue(insidesplit[1])	
					elif len(insidesplit)>3 and insidesplit[2] == "when":
						# special case: Conditional collect annotation
						if not self.cg.isEmpty():
							raise FlexDataError("not permitted to use conditional collect annotation from within a conditional block")
						loccg = conditionGroup()
						loccg.add(conditionAtom(" ".join(insidesplit[2:])))
						loccg.immutable = True
						# TODO: add collect atom to collection list to get to later
					else:
						raise FlexDataError("invalid collect annotation")
				elif insidesplit[0] == "section":
					# Section annotation
					# Conditions are always reset when we enter a new section, so reference our immutable empty
					# condition group.
					self.cg = cgempty
					if len(insidesplit)==2:
						self.section=insidesplit[1]
					elif len(insidesplit)>3 and insidesplit[2] == "when":
						# Special case: conditional section annotation
						self.section=insidesplit[1]
						self.cg = conditionGroup()
						self.cg.add(conditionAtom(" ".join(insidesplit[2:])))
						self.cg.immutable = True
					else:
						raise FlexDataError("invalid section annotation")
				else:
					raise FlexDataError("invalid annotation")
			elif mysplit[0][-1] == ":":
				
				# We have found a single-line element. We will create a corresponding singleLineElement object and add it
				# to the namespace.
				varname=mysplit[0][0:-1]
				self.namespace.add(singleLineElement(self.section,varname," ".join(mysplit[1:])),self.cg)
			else:
				raise FlexDataError("invalid line")
class element:
	def __init__(self,section,varname,rawvalue):

		global filename
		global lineno

		if varname == ":":
			# Properly handle $[:]
			varname = ""
		if section != "":
			self.varname = section + "/" + varname
			if self.varname[-1] == "/":
				self.varname = self.varname[:-1]
		else:
			self.varname = varname
		
		self.rawvalue = rawvalue
		
		self.filename = filename
		self.lineno = lineno
	
	def name(self):
		return self.varname

class singleLineElement(element):
	def __init__(self,section,varname,rawvalue):
		element.__init__(self,section,varname,rawvalue)
	def __repr__(self):
		return "'"+self.rawvalue+"'"

class multiLineElement(element):
	def __init__(self,section,varname,rawvalue):

		global prevlineno

		self.endline = prevlineno
		element.__init__(self,section,varname,rawvalue)
	def __repr__(self):
		return "'"+self.rawvalue+"'"

if __name__ == "__main__":
	coll = metroCollection()
	try:
		for arg in sys.argv[1:]:
			coll.collect(arg)
		coll.namespace.debugDump()
	except:
		sys.exit(1)
	sys.exit(0)


