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

"""
What do we want the new format to look like?

foo: bar
meep: [
	#!/usr/bin/python
	allow indentation
	because it's nice.
	will be auto-outdented by default.
]

gleep:-auto: [
	#!/usr/bin/python
	this will remain indented, no auto-outdent
]

[coll foo.conf]

evaluate '$[foo]-$[bar]' [
	= spaghetti: collect foo-$[moko].conf
	# if moko is not yet defined - what to do? If we try another collect statement below, we've
	# broken ordering rules, which are important, right? If we give up and move to another eval,
	# then potentially we'll do a ton of collection. But it probably won't be that bad.
	= linguini: collect spingee.conf
	in $[oni]: coll gleep
	*: pass 
]

eval "$[wigwam]" [
	= 'funky' : collect foo.conf
	* : raise
]
"""

class element:
	def __init__(self,varname,rawvalue,context):
	
		self.filename, self.section, self.lineno = context
		
		if varname == ":":
			# Properly handle $[:]
			varname = ""
		if self.section != "":
			self.varname = self.section + "/" + varname
			if self.varname[-1] == "/":
				self.varname = self.varname[:-1]
		else:
			self.varname = varname

		self.rawvalue = rawvalue

	def name(self):
		return self.varname

	def __repr__(self):
		return repr(self.rawvalue)

class singleLineElement(element):

	def __init__(self,varname,rawvalue,context):
		element.__init__(self,varname,rawvalue,context)

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
	def __init__(self,varname,rawvalue,context):
		
		self.endline = context[-1]
		context = context[:-1]

		element.__init__(self,varname,rawvalue,context)

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


class connector:
	def __init__(self):
		pass

class collectConnector(connector):
	def __init__(self,sourcefile,celement_raw):
		self.sourcefile = sourcefile
		self.celement_raw = celement_raw

class evaluateConnector(connector):
	def __init__(self):
		pass
class dataModel:
	def __init__(self):
		self.elements={}
		self.files_processed=[]
		self.connectors=[]
		pass

	def addElement(self,element):
		elname = element.name()
		if not self.elements.has_key(elname):
			self.elements[elname]=element
		else:
			# TODO - prettier exception for duplicate definition
			raise

	def addConnector(self,connector):
		self.connectors.append(connector)

	def expandAllConnectors(self):
		connector_stats=[]
		
		current_connector=self.connectors[0]
		celement_evald = self.evaluate(current_connector.celement_raw)

	def parseFile(self,filename):

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
							self.addElement(multiLineElement(varname,mylines,[filename,section,prevlineno,lineno]))
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
						#self.collection.queue(insidesplit[1])
						print "FIXME DEBUG: found COLLECT annotation for",insidesplit[1]
					else:
						raise ParseError("invalid collect annotation")
				elif insidesplit[0] == "section":
					# Section annotation
					if len(insidesplit)==2:
						section=insidesplit[1]
					else:
						raise ParseError("invalid section annotation")
				else:
					raise ParseError("invalid annotation")
			elif mysplit[0][-1] == ":":
				# We have found a single-line element. We will create a corresponding singleLineElement object
				varname=mysplit[0][0:-1]
				self.addElement(singleLineElement(varname," ".join(mysplit[1:]),[filename,section,lineno]))
			else:
				raise ParseError("invalid line")


	def evaluate(self):
	
if __name__ == "__main__":
	obj = dataModel()
	obj.addConnector(collectConnector(None,"/usr/lib/etc/metro.conf"))
	obj.expandAllConnectors()

""" expansion of strings: 


[ "$[foo]-$[bar]" ], []
[ "$[foo]", "-", "$[bar"] ], 
[ "gleep", "-", "$[tony]", "-", "$[danza] ]


foo: $[bar]
bar: $[foo]


"$[foo]-$[bar]"
[ "$[foo]", "-", "$[bar]" ]
we are going to expand $[foo]
we look up $[foo] --> stack enqueue
we see it has the value of $[bar] --> is $[bar] on stack? no. OK, proceed.
we look up $[bar] --> stack enqueue
we see it has the value of $[foo] --> is $[foo] on stack? yes. Abort.



"""
