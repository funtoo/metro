#!/usr/bin/python

import os, sys

filename = None
lineno = None

class ExpandError(Exception):
	def __init__(self, message):
		print message

class ParseError(Exception):
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
	def __init__(self,condition=None):

		global filename
		global lineno
		global cgNone

		self.filename = filename
		self.lineno = lineno
		self.parent = None
		self.parentNegated = False
		self.condition = condition

	def refine(self,condition):
		newatom = conditionAtom(condition)
		newatom.sibling = self
		return newatom
	
	def negateAndRefine(self,condition):
		if self == cgNone:
			raise ParseError("Attempt to negate the ANY condition (which would always be false)")
		newatom = conditionAtom(condition)
		newatom.parent = self
		newatom.parentNegated = True
		return newatom

	def negate(self):
		if self == cgNone:
			raise ParseError("Attempt to negate the ANY condition (which should always be false)")
		newatom = conditionAtom()
		newatom.parent = self
		newatom.parentNegated = True	
		return newatom

	def __repr__(self):
		if self.condition == None:
			return "ANY"
		out=repr(self.condition) 
		if self.parent:
			if self.parent.negated:
				out += "AND NOT ( "+repr(self.parent)+" ) "
			else:
				out += "AND ( "+repr(self.parent)+" ) "
		return out

	def isTrue(self):
		# TODO: fix
		return True

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
		# {"varname" : [ element-object(contains value):condition-group ] 
	def __getitem__(self,val):
		return self.elements[val]
	def add(self,element,cg):
		elname = element.name()
		if not self.elements.has_key(elname):
			self.elements[elname]=[]
		# Note that we do not check for duplicates and throw exceptions at this stage. The following elements
		# could be added to the namespace just fine:
		#
		# foo: bar
		# foo: oni
		#
		# or even
		#
		# foo: bar
		# foo: bar
		# 
		# we will check for dupes on evaluation, where the above values will throw an exception due to having
		# multiple definitions.
		self.elements[elname].append([element, cg])	
	def debugDump(self):
		keys=self.elements.keys()
		keys.sort()
		for key in keys:
			print key+":"
			for el, cond in self.elements[key]:
				print "\t"+repr(el)+": "+repr(cond)
	
	def expand(self,name,stack=[]):
		if not self.elements.has_key(name):
			raise ExpandError(name+" not found")
		eclist = self.elements[name]
		ectrue = None
		for el, cond in eclist:
			if cond.isTrue():
				if ectrue != None:
					raise ExpandError("multiple definitions")
				else:
					ectrue = [ el, cond ]
		# we now have a single "true" element - time to expand it.
		el, cond = ectrue
		if el.varname in stack:
			raise ExpandError("recursive reference")
		if isinstance(el,singleLineElement):
			newstr = ""
			for substr in el.getExpansion():
				if substr[0:2] != "$[":
					newstr += substr
				else:
					# TODO: handle :zap, :lax, and "?" at the end
					# we're expanding something...
					if substr in [ "$[]", "$[:]"]:
						# $[] or $[:]
						expandme = el.section
					elif substr[2] == ":":
						# $[:foo]
						expandme = el.section + "/" + substr[3:-1]
					else:
						# $[foo/bar/oni]
						expandme = substr[2:-1]
					# TODO: add the element itself rather than just its name to the stack
					# so we can do type checking against the stack.
					newstack = stack[:]
					newstack.append(el.varname)
					newstr += self.expand(expandme,newstack)
			return newstr
		elif isinstance(el,multiLineElement):
			#TODO: write the multi-line expansion
			pass
		else:
			raise ExpandError("unknown element type")

cgNone = conditionAtom()

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

		global prevlineno
		global lineno
		global curline
		global filename
		
		filename = self.filename
		lineno = 0
		prevlineno = 0

		global cgNone
		self.cg = cgNone

		# This function parses the high-level structure of the document, identifying data elements
		# and annotations, and creates appropriate internal objects and then adds them to the namespace.

		try:
			myfile=open(self.filename,"r")
		except:
			raise ParseError("can't open file")
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
				varname = mysplit[0][0:-1]
				mylines = []
				while 1:
					try:
						curline = myfile.next() 	
						lineno += 1
						mysplit = curline[:-1].strip().split(" ")
						if len(mysplit) == 1 and mysplit[0] == "]":
							# Add condition:multi-line element pair to namespace
							self.namespace.add(multiLineElement(self.section,varname,mylines),self.cg)
							break
						else:
							mylines.append(curline)
					except StopIteration:
						raise ParseError("incomplete (unclosed) multi-line block (started on line %i)" % prevlineno )

			elif mysplit[0][0]=="[" and mysplit[-1][-1]=="]":
				if len(mysplit) == 0:
					raise ParseError("empty annotation")
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
					self.cg = conditionAtom(insides)
				elif insidesplit[0] in [ "+when", "-when" ]:
					# Compound conditional annotation - create a new live object to modify, in case the old cg was used
					self.cg = self.cg.extend(insides)
				elif insidesplit[0] == "else":
					self.cg = self.cg.negate()
				elif insidesplit[0] == "collect":
					# Collect annotation
					if len(insidesplit)==2:
						self.collection.queue(insidesplit[1])	
					elif len(insidesplit)>3 and insidesplit[2] == "when":
						# special case: Conditional collect annotation
						if self.cg != cgNone:
							raise ParseError("not permitted to use conditional collect annotation from within a conditional block")
						loccg = conditionAtom(" ".join(insidesplit[2:]))
						# TODO: add collect atom to collection list to get to later
					else:
						raise ParseError("invalid collect annotation")
				elif insidesplit[0] == "section":
					# Section annotation
					# Conditions are always reset when we enter a new section, so reference our immutable empty
					# condition group.
					self.cg = cgNone
					if len(insidesplit)==2:
						self.section=insidesplit[1]
					elif len(insidesplit)>3 and insidesplit[2] == "when":
						# Special case: conditional section annotation
						self.section=insidesplit[1]
						self.cg = self.cg.extend(" ".join(insidesplit[2:]))
					else:
						raise ParseError("invalid section annotation")
				else:
					raise ParseError("invalid annotation")
			elif mysplit[0][-1] == ":":
				
				# We have found a single-line element. We will create a corresponding singleLineElement object and add it
				# to the namespace.
				varname=mysplit[0][0:-1]
				self.namespace.add(singleLineElement(self.section,varname," ".join(mysplit[1:])),self.cg)
			else:
				raise ParseError("invalid line")
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
		self.section = section
	
	def name(self):
		return self.varname
	
	def __repr__(self):
		return repr(self.rawvalue)

class singleLineElement(element):

	def __init__(self,section,varname,rawvalue):
		element.__init__(self,section,varname,rawvalue)

	def expand(self):
		gen = self.getExpansion()
		newstring = ""


	def getExpansion(self):
		pos = 0
		rv = self.rawvalue
		while pos < len(rv):
			found = rv.find("$[",pos)
			if found == -1:
				yield rv[pos:]
				break
			if rv[pos:found] != "":
				yield rv[pos:found]
			found2 = rv.find("]",pos+2)
			if pos == -1:
				# TODO: THROW EXCEPTION HERE
				break
			pos = found2 + 1
			yield(rv[found:found2+1])

class multiLineElement(element):
	def __init__(self,section,varname,rawvalue):

		global prevlineno

		self.endline = prevlineno
		element.__init__(self,section,varname,rawvalue)

if __name__ == "__main__":
	coll = metroCollection()
	try:
		for arg in sys.argv[1:]:
			coll.collect(arg)
		coll.namespace.debugDump()
	except ParseError:
		sys.exit(1)

el, cond = coll.namespace["path/cache/foo"][0]
print el
print cond
exp = el.getExpansion()
for myex in exp:
	print "*:'%s'" % myex
print coll.namespace.expand("path/cache/foo")
