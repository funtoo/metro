#!/usr/bin/python

import os, sys

filename = None
lineno = None

class ExpandError(Exception):
	def __init__(self, message=None,els=[]):
		out="\nExpansion exception: %s\n" % message
		if len(els) == 0:
			pass
		else:
			out += "\n"
			for el in els:
				out += "\tfile '%s', line %i: '%s'\n" % ( el.filename, el.lineno, el.rawvalue )
		print out

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

class collection:
	def __init__(self):
		self.filelist=[]
		self.namespace = nameSpace()
		self.cq=[]
	def collect(self,filename):
		self.filelist.append(metroParsedFile(filename,self))
	def queue(self,filename):
		self.cq.append(filename)
	def debugDump(self):
		self.namespace.debugDump()
		print self.cq

class nameSpace:
	def __init__(self):
		self.elements={}
		# Structure of self.elements is:
		# {"varname" : [ element-object, element-object ]
	def __getitem__(self,val):
		return self.elements[val]

	def add(self,element):
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
		self.elements[elname].append(element)

	def debugDump(self):
		keys=self.elements.keys()
		keys.sort()
		for key in keys:
			print key+":"
			for el in self.elements[key]:
				print "\t"+repr(el)

	def find(self,name,strict=False):
		# STEP 1: FIND LITERAL DATA TO EXPAND
		if not self.elements.has_key(name):
			return None
		eclist = self.elements[name]
		ectrue = []
		for el in elist:
			if cond.isTrue():
				ectrue.append([el,cond])
		if len(ectrue) == 0:
			if strict:
				raise ExpandError("no true definitions of '%s' in:" % name, els=[x[0] for x in eclist])
			else:
				return None
		elif len(ectrue) == 1:
			el, cond = ectrue[0]
			return el
		else:
			raise ExpandError("multiple true definitions of '%s':" % name,els=[x[0] for x in ectrue])


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
							self.namespace.add(multiLineElement(self.section,varname,self.namespace,mylines))
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

				if insidesplit[0] == "collect":
					# Collect annotation
					if len(insidesplit)==2:
						self.collection.queue(insidesplit[1])
					else:
						raise ParseError("invalid collect annotation")
				elif insidesplit[0] == "section":
					# Section annotation
					if len(insidesplit)==2:
						self.section=insidesplit[1]
					else:
						raise ParseError("invalid section annotation")
				else:
					raise ParseError("invalid annotation")
			elif mysplit[0][-1] == ":":

				# We have found a single-line element. We will create a corresponding singleLineElement object and add it
				# to the namespace.
				varname=mysplit[0][0:-1]
				self.namespace.add(singleLineElement(self.section,varname,self.namespace," ".join(mysplit[1:])))
			else:
				raise ParseError("invalid line")

class stringLiteral():

	def __init__(self,value,parent):
		self.value = value
		self.parent = parent

	def getExpansion(self):
		pos = 0
		while pos < len(rv):
			found = self.value.find("$[",pos)
			if found == -1:
				yield self.value[pos:]
				break
			if self.value[pos:found] != "":
				yield rv[pos:found]
			found2 = self.value.find("]",pos+2)
			if pos == -1:
				# TODO: THROW EXCEPTION HERE
				break
			pos = found2 + 1
			yield(self.value[found:found2+1])

	def expand(self,stack=[]):
		newstr = ""
		for substr in self.getExpansion():
			# reset "mods" so we don't pass "lax" or "zap" to new evaluations (sibling or child (resursive))
			mods = []
			bool = None
			if substr[0:2] != "$[":
				newstr += substr
				continue

			# we're expanding something...
			if substr in [ "$[]", "$[:]"]:
				# $[] or $[:]
				expandme = parent.section
			elif substr[2] == ":":
				# $[:foo]
				expandme = parent.section + "/" + substr[3:-1]
			else:
				# $[foo/bar/oni]
				if parent.section:
					expandme = parent.section + "/" + substr[2:-1]
				else:
					expandme = substr[2:-1]

			# handle modifiers
			if expandme[-4:] == ":zap":
				mods.append("zap")
				expandme = expandme[:-4]
			elif expandme[-4:] == ":lax":
				mods.append("lax")
				expandme = expandme[:-4]

			# handle ? at end - this code allows $[foo:lax?] and $[bar:zap?]

			if expandme[-1] == "?":
				expandme = expandme[:-1]
				if self.parent.namespace.find(expandme):
					newstr += "yes"
				else:
					newstr += "no"
				continue

			newstack = stack[:]
			newstack.append(self.parent)
			newel = self.parent.namespace.find(expandme,strict=False)


			for otherel in stack:
				if otherel.varname == newel.varname:
					raise ExpandError("recursive reference of '%s'" % el.varname ,els=[el])

			if newel == None:
				if "lax" in mods:
					newstr += "(lax-not-found-%s)" % expandme
					continue
				else:
					# This will throw an exception and give us a nice error message:
					self.parent.namespace.find(expandme,strict=True)
			else:
				exp = newel.expand(newstack)
				if ("zap" in mods) and (exp == None):
					return ""
				else:
					newstr += exp
		return newstr

class element:
	def __init__(self,section,varname,namespace):
		global filename
		global lineno
		self.filename = filename
		self.lineno = lineno
		self.section = section
		self.varname = varname
		self.namespace = namespace

	def name(self):
		if self.section != "":
			return self.section + "/" + self.varname
		else:
			return self.varname

class singleLineElement(element):

	def __init__(self,section,varname,namespace,rawvalue):
		self.rawvalue=rawvalue
		self.literal=stringLiteral(self.rawvalue,self)
		element.__init__(self,section,varname,namespace)

	def expand(self):
		return self.literal.expand()

	def __repr__(self):
		return repr(self.rawvalue)


class multiLineElement(element):
	def __init__(self,section,varname,namespace,mylines):

		global prevlineno
		self.lines=mylines
		self.endline = prevlineno
		element.__init__(self,section,varname,namespace)
	def __repr__(self):
		return repr(self.lines)

if __name__ == "__main__":
	coll = collection()
	coll.collect(sys.argv[1])
	coll.debugDump()
