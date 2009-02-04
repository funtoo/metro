#!/usr/bin/python

import os, sys

class FlexDataError(Exception):
	def __init__(self, message):
		if message:
			print
			print "Metro Parser: "+message
			print
	
class metroCollection:
	def __init__(self):
		self.filelist=[]
		self.namespace = metroNameSpace()
	def collect(self,filename):
		self.filelist.append(metroParsedFile(filename,self))

class metroNameSpace:
	def __init__(self):
		self.elements={}
		# Structure of self.elements is:
		# {"varname" : { element-object:[condition-list] } 
		# Condition-list of [] means no conditions.
		# Now would be a good time to add "else" clauses.....
	def add(self,element,conditionlist):
		if not self.elements.has_key(element.name()):
			self.elements[element.name()]={}
		self.elements[element.name()][element] = conditionlist	
	def debugDump(self):
		for key in self.elements.keys():
			print key, self.elements[key]

class metroParsedFile:
	def __init__(self,filename,collection):
		self.filename = os.path.normpath(filename)
		self.namespace = collection.namespace
		self.collection = collection
		self.conditionlist = []
		self.lineno=0

		self.curline=None
		self.parse()
	
	def prettyLoc(self):
		# Pretty-print the filename and line number
		return "%s, Line %i: '%s'" % (self.filename, self.lineno, self.curline)

	def name(self):
		return self.filename

	def parse(self):
	
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
				self.curline = myfile.next()[:-1]
				self.lineno += 1
			except StopIteration:
				break
			mysplit = self.curline.strip().split(" ")

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
				
				prevlineno = self.lineno
				varname = mysplit[0:-1]
				mylines = []
				while 1:
					try:
						self.curline = myfile.next() 	
						self.lineno += 1
						mysplit = self.curline[:-1].strip().split(" ")
						if len(mysplit) == 1 and mysplit[0] == "]":
							# Add condition:multi-line element pair to namespace
							self.namespace.add(multiLineElement(self.section,varname,self.conditionlist,mylines,filename=self.filename,startline=prevlineno,endline=self.lineno))
						else:
							mylines.append(self.curline)
					except StopIteration:
						raise FlexDataError,"%s: incomplete (unclosed) multi-line block (started on line %i)" % ( self.prettyLoc(), self.prevlineno )

			elif mysplit[0][0]=="[" and mysplit[-1][-1]=="]":
				if len(mysplit) == 1:
					insides == mysplit[0][1:-1]
				else:
					insides = mysplit[0][1:] + " " + " ".join(mysplit[1:-1]) + " " + mysplit[-1][:-1]
				insidesplit = insides.split()

				# We have found an annotation. We will perform appropriate processing to handle the annotation correctly.

				if insidesplit[0] == "when":
					# Conditional annotation
					self.conditionlist=[condition(insides,filename=self.filename,lineno=self.lineno)]
				elif insidesplit[0] in [ "+when", "-when" ]:
					# Compound conditional annotation
					self.conditionlist.append(condition(insides,filename=self.filename,line=self.lineno))
				elif insidesplit[0] == "else":
					# TODO
					pass
				elif insidesplit[0] == "collect":
					# Collect annotation
					if len(insidesplit)==2:
						self.collection.collect(insidesplit[1])	
					elif len(insidesplit)>3 and insidesplit[2] == "when":
						# special case: Conditional collect annotation
						self.conditionlist=[condition(" ".join(insidesplit[2:]),filename=self.filename,lineno=self.lineno)]
						# TODO
					else:
						raise FlexDataError,"%s: invalid collect annotation" % self.prettyLoc()
				elif insidesplit[0] == "section":
					# Section annotation
					# Conditions are always reset when we enter a new section:
					self.conditionlist=[]
					if len(insidesplit)==2:
						self.section=insidesplit[1]
					elif len(insidesplit)>3 and insidesplit[2] == "when":
						# Special case: conditional section annotation
						self.section=insidesplit[1]
						self.conditionlist=[condition(" ".join(insidesplit[2:]),filename=self.filename,lineno=self.lineno)]
					else:
						raise FlexDataError,"%s: invalid section annotation" % self.prettyLoc()
				else:
					raise FlexDataError,"%s: invalid annotation" % self.prettyLoc()
			elif mysplit[0][-1] == ":":
				
				# We have found a single-line element. We will create a corresponding singleLineElement object and add it
				# to the namespace.
				varname=mysplit[0][0:-1]
				self.namespace.add(singleLineElement(self.section,varname," ".join(mysplit[1:]),filename=self.filename,lineno=self.lineno),self.conditionlist)
			else:
				raise FlexDataError, "%s: invalid line: '%s'" % ( self.prettyLoc(), self.curline )

class condition:
	def __init__(self,value,filename,lineno):
		# This filename and line records the line at which the condition was applied, not defined
		self.value=value
		self.filename=filename
		self.lineno=lineno
	def __repr__(self):
		return self.value

class element:
	def __init__(self,section,varname,rawvalue,filename,lineno):
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
	def __init__(self,section,varname,rawvalue,filename,lineno):
		element.__init__(self,section,varname,rawvalue,filename,lineno)
	def __repr__(self):
		return "'"+self.rawvalue+"'"

class multiLineElement(element):
	def __init__(self,section,varname,rawvalue,filename,lineno,endline):
		self.endline = endline
		element.__init__(self,section,varname,rawvalue,filename,lineno)
	def __repr__(self):
		return "'"+self.rawvalue+"'"

if __name__ == "__main__":
	coll = metroCollection()
	for arg in sys.argv[1:]:
		coll.collect(arg)
	coll.namespace.debugDump()
	sys.exit(0)


