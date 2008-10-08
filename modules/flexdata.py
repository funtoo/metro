#!/usr/bin/python

import sys,os,types,StringIO,string

"""
BUG: EMBEDDED PYTHON MAY EXPAND VARIABLES THAT ARE NOT DEFINED YET

This module contains Metro's parsing code. It supports the following syntax:

foo: bar

... defines key "foo" to have value "bar". Multiple whitespace-separated values can be specified after
"bar" if desired.

foo: << bar

... defines key "foo" to have the value of the contents of the file "bar" (all newlines removed)

bar: [
#!/bin/bash
ls -l /
mv $[foo] $[bar]
>> oni
<?python
print "Hello from python!"
if settings["foo"] != "bar":
	print settings["foo"]
?>
]

... defines key "bar" to have the multi-line value of a small shell script. The ">> onit" line inserts
the multi-line contents of the variable "oni". On the "mv $[foo] $[bar]" line, the variables $[foo]
and $[bar] will be expanded to the values of foo and bar, respectively.

The parser is designed to eliminate side-effects. keys can be defined only once. The order of definition
is not important, so the following snippet of code works fine:

foo: $[bar]
bar: hi there! 

The <?python and ?> tags, appearing by themselves on a line, indicate an embedded python section of the
multi-line block. Python code in this block will be executed and stdout will be appended to the result
string.

"""

class FlexDataError(Exception):
	def __init__(self, message):
		if message:
			print
			print "Metro Parser: "+message
			print
	
class collection:
	""" The collection class holds our parser.
	
	__init__() contains several important variable definitions.

	self.immutable - if set to true, the parser will throw a warning if a variable is redefined. Otherwise it will not.
	This variable can be toggled at any time, so a collection can start out in a mutable state and then be switched to
	immutable for parsing of additional files.

	self.lax = the "lax" option, if True, will allow for a undefined single-line variable to expand to the empty string.
	If lax is False, then the parser will throw an exception if an undefined single-line variable is expanded.

	"""
	def __init__(self,debug=False):
		self.clear()
		self.debug=debug
		self.pre = "$["
		self.suf = "]"
		self.immutable=False
		# lax means: if a key isn't found, pretend it exists but return the empty string.
		self.lax=True
		self.laxstring="[BLANK var=%s]"
		self.blanks={}
		# self.collected holds the names of files we've collected (parsed)
		self.collected=[]
		self.section=""
		self.sectionfor={}
	def clear(self):
		self.raw={}
		self.evaluated={}
		self.blanks={}

	def expand_all(self):
		# try to expand all variables to find any undefined elements, to record all blanks or throw an exception
		for key in self.keys():
			myvar = self[key]

	def expand(self,myvar):
		if self.evaluated.has_key(myvar):
			return self.evaluated[myvar]
		elif self.raw.has_key(myvar):
			if type(self.raw[myvar]) == types.ListType:
				return self.expandMulti(myvar)
			else:
				return self.expandString(myvar=myvar)
		elif self.lax:
			# record that we looked up an undefined element
			self.blanks[myvar]=True
			return self.laxstring % myvar
		else:
			raise FlexDataError,"Variable \""+myvar+"\" not found"

	def expandString(self,string=None,myvar=None,stack=[]):
		if self.debug:
			print "DEBUG: in expandString"
		# Expand all variables in a basic value, ie. a string 

		if string == None:
			if self.evaluated.has_key(myvar):
				return self.evaluated[myvar]
			elif self.raw.has_key(myvar):
				string = self.raw[myvar]

		if type(string) != types.StringType:
			if len(stack) >=1:
				raise FlexDataError("expandString received non-string when expanding "+repr(myvar)+" ( stack = "+repr(stack)+")")
			else:
				raise FlexDataError("expandString received non-string")

		mysplit = string.strip().split(" ")
		if len(mysplit) == 2 and mysplit[0] == "<<":
			fromfile = True
			string = " ".join(mysplit[1:])
		else:
			fromfile = False

		unex = string
		ex = ""
		while unex != "":
			varpos = unex.find(self.pre)
			if varpos == -1:
				ex += unex
				unex = ""
				continue
			ex += unex[0:varpos]
			unex = unex[varpos+len(self.pre):] # remove "$["
			endvarpos = unex.find(self.suf)
			if endvarpos == -1:
				raise KeyError,"Error expanding variable for '"+string+"'"
			varname = unex[0:endvarpos]
			self.sectionfor[varname] = self.section
			# $[] expansion
			# FIXME
			if varname == "":
				if self.sectionfor.has_key(myvar):
					varname = self.sectionfor[myvar]
				else:
					raise FlexDataError, "no section name for "+myvar+" in "+string
			unex = unex[endvarpos+len(self.suf):]
			if varname in stack:
				raise KeyError, "Circular reference of '"+varname+"' by '"+stack[-1]+"' ( Call stack: "+repr(stack)+' )'
			if self.evaluated.has_key(varname):
				# if myvar == None, we are being called from self.expand_all() and we don't care where we are being expanded from
				if myvar != None and type(self.evaluated[varname]) == types.ListType:
					raise FlexDataError,"Trying to expand multi-line value "+repr(varname)+" in single-line value "+repr(myvar)
				ex += self.evaluated[varname]
			elif self.raw.has_key(varname):
				# if myvar == None, we are being called from self.expand_all() and we don't care where we are being expanded from
				if myvar != None and type(self.raw[varname]) == types.ListType:
					raise FlexDataError,"Trying to expand multi-line value "+repr(varname)+" in single-line value "+repr(myvar)
				newstack = stack[:]
				newstack.append(varname)
				ex += self.expandString(self.raw[varname],varname,newstack)
			else:
				if not self.lax:
					raise KeyError, "Cannot find variable '"+varname+"'"
				else:
					# record variables that we attempted to expand but were blank, so we can inform the user of possible bugs
					self.blanks[varname] = True
					ex += self.laxstring % varname
		if fromfile == False:
			self.evaluated[myvar] = ex
			return ex

		#use "ex" as a filename
		try:
			myfile=open(ex,"r")
		except:
			raise FlexDataError,"Cannot open file "+ex+" specified in variable \""+varname+"\""
		outstring=""
		for line in myfile.readlines():
			outstring=outstring+line[:-1]+" "
		myfile.close()
		self.evaluated[myvar] = outstring[:-1]
		return self.evaluated[myvar] 


	def expandMulti(self,myvar,stack=[]):

		mylocals = {}
		# Expand all variables in a multi-line value. stack is used internally to detect circular references.
		if self.debug:
			print "DEBUG: in expandMulti"
		if self.evaluated.has_key(myvar):
			element = self.evaluated[myvar]
			if type(element) != types.ListType:
				raise FlexDataError("expandMulti encountered non-multi")
			return element
		if self.raw.has_key(myvar):
			multi = self.raw[myvar]
			if type(multi) != types.ListType:
				raise FlexDataError("expandMulti received non-multi")
		else:
			if self.lax:
				self.blanks[myvar] = True
				return [self.laxstring % myvar]
			else:
				raise FlexDataError("referenced variable \""+myvar+"\" not found")

		newlines=[]

		pos=0
		while pos<len(multi):
			mysplit = multi[pos].strip().split(" ")
			if len(mysplit) == 2 and mysplit[0] == ">>":
				if mysplit[1] in stack:
					raise FlexDataError,"Circular reference of '"+mysplit[1]+"' by '"+stack[-1]+"' ( Call stack: "+repr(stack)+' )'
				newstack = stack[:]
				newstack.append(mysplit[1])
				newlines += self.expandMulti(self.expandString(string=mysplit[1]),newstack)
			elif len(mysplit) >=1 and mysplit[0] == "<?python":
				sys.stdout = StringIO.StringIO()
				mycode=""
				pos += 1
				while (pos < len(multi)):
					newsplit = multi[pos].split()
					if len(newsplit) >= 1 and newsplit[0] == "?>":
						break
					else:
						mycode += multi[pos] + "\n"
						pos += 1
				exec mycode in { "settings" : self, "os": os }, mylocals
				newlines.append(sys.stdout.getvalue())
				sys.stdout = sys.__stdout__
			else:	
				newlines.append(self.expandString(string=multi[pos]))
			pos += 1
		self.evaluated[myvar] = newlines
		return newlines

	def __setitem__(self,key,value):
		if self.immutable and self.raw.has_key(key):
			raise IndexError, "Attempting to redefine "+key+" to "+value+" when immutable."
		self.raw[key]=value
		# invalidate any already-evaluated data
		self.evaluated={}

	def __delitem__(self,key):
		if self.immutable and self.raw.has_key(key):
			raise IndexError, "Attempting to delete "+key+" when immutable."
		del self.raw[key]
		self.evaluated={}

	def __getitem__(self,element):
		return self.expand(element)

	def has_key(self,key):
		return self.raw.has_key(key)

	def keys(self):
		return self.raw.keys()

	def missing(self,keylist):
		""" return list of any keys that are not defined. good for validating that we have a bunch of required things defined."""
		missing=[]
		for key in keylist:
			if not self.raw.has_key(key):
				missing.append(key)
		return missing

	def debugdump(self,desc=""):
		for key in self.keys():
			if type(self[key]) == types.ListType:
				pos = 0
				for line in self[key]:
					print key+".%04d" % pos,
					print line
					pos += 1
			else:
				print key, self[key]
		print

	def skipblock(self,openfile=None):
		while 1:
			curline=openfile.readline()
			mysplit = curline[:-1].strip().split(" ")
			if len(mysplit) == 0:
				continue
			if mysplit[0] == "}":
				return
			else:
				continue

	def parseline(self,openfile=None,dups=False):
		
		# parseline() will parse a line and return None on EOF, return [] on a blank line with no data, or will
		# return a list of string elements if there is data on the line, split along whitespace: [ "foo:", "bar", "oni" ]
		# parseline() will also remove "# comments" from a line as appropriate
		# parseline() will update self.raw with new data as it finds it.
		curline = openfile.readline()
		if curline == "": #EOF
			return None
		# get list of words separated by whitespace
		mysplit = curline[:-1].strip().split(" ")
		if len(mysplit) == 1 and  mysplit[0] == '':
			# blank line
			return []
		#strip comments
		spos = 0
		while 1:
			if spos >= len(mysplit):
				break
			if len(mysplit[spos]) == 0:
				spos += 1
				continue
			if mysplit[spos][0] == "#":
				mysplit=mysplit[0:spos]
				break
			spos += 1
		
		if len(mysplit) == 0:
			return []

		#parse elements
		if len(mysplit[0]) == 0:
			# not an element
			return []

		if len(mysplit) == 2 and mysplit[0][-1] == ":" and mysplit[1] == "[":
			if self.debug:
				print "DEBUG: MULTI-LINE BLOCK"
			# for myvar, remove trailing colon:
			myvar = mysplit[0][:-1]
			if self.section:
				myvar = self.section+"/"+myvar
			mylines = []
			while 1:
				curline = openfile.readline()
				if curline == "":
					raise KeyError,"Error - incomplete [[ multi-line block,"
				mysplit = curline[:-1].strip().split(" ")
				if len(mysplit) == 1 and mysplit[0] == "]":
					if self.debug:
						print "DEBUG: end multi-line block"
					# record value and quit
					if not dups and self.raw.has_key(myvar):
						raise FlexDataError,"Error - \""+myvar+"\" already defined."
					self.raw[myvar] = mylines
					break
				else:
					# append new line
					mylines.append(curline[:-1])
		elif mysplit[0][0]=="[" and mysplit[-1][-1]=="]":
			# possible section
			mysplit[0] = mysplit[0][1:]
			mysplit[-1] = mysplit[-1][:-1] 
			mysection=string.join(mysplit).split()
			if len(mysection) != 2:
				raise FlexDataError,"Invalid section specifier: "+curline[:-1]
			if mysection[0] != "section":
				raise FlexDataError,"Expected \"section\" in: "+curline[:-1]
			self.section = mysection[1]
		elif mysplit[0][-1] == ":":
			#basic element - rejoin all data elements with spaces and add to self.raw
			mykey = mysplit[0][:-1]
			if mykey == "":
				# ":" tag
				mykey = self.section
			elif self.section:
				mykey = self.section+"/"+mykey
			self.sectionfor[mykey]=self.section
			if not dups and self.raw.has_key(mykey):
				raise FlexDataError,"Error - \""+mykey+"\" already defined."
			self.raw[mykey] = " ".join(mysplit[1:])
		return mysplit	
	
	def collect(self,filename):
		if not os.path.exists(filename):
			raise IOError, "File '"+filename+"' does not exist."
		if not os.path.isfile(filename):
			raise IOError, "File to be parsed '"+filename+"' is not a regular file."
		openfile = open(filename,"r")
		self.section=""
		while 1:
			out=self.parseline(openfile)
			if out == None:
				break
		openfile.close()
		# add to our list of parsed files
		self.collected.append(os.path.normpath(filename))
	
if __name__ == "__main__":
	coll = collection(debug=False)
	for arg in sys.argv[1:]:
		coll.collect(arg)
	coll.debugdump()
	sys.exit(0)

