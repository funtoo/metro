#!/usr/bin/python

import sys,os

class collection:
	def __init__(self,debug=False):
		self.clear()
		self.debug=debug
		self.pre = "$["
		self.suf = "]"
		self.immutable=False
		# lax means: if a key isn't found, pretend it exists but return the empty string.
		self.lax=True

	def clear(self):
		self.raw={}

		# self.evaluated holds our already-evaluated variables

		self.evaluated={}

	def expand(self,element,stack=[]):

		# expand() performs variable expansion but does not update the self.evaluated dictionary.
		# it just performs variable expansion on a string based on the data in self.raw and self.evaluated
		# and returns the result.

		fromfile=False
		
		if element[0:3] == "<< ":
			# strip the "<< ", expand our variable, and then use it as a filename and try to grab data from it before we return
			fromfile=True
			element=element[3:]

		unex = element
		ex = ""
		while unex != "":
			varpos = unex.find(self.pre)
			if varpos == -1:
				ex += unex
				unex = ""
				continue
			ex += unex[0:varpos]
			unex = unex[varpos+len(self.pre):] # remove "${"
			endvarpos = unex.find(self.suf)
			if endvarpos == -1:
				raise KeyError,"Error expanding variable for '"+element+"'"
			varname = unex[0:endvarpos]
			unex = unex[endvarpos+len(self.suf):]
			if varname in stack:
				raise KeyError, "Circular reference of '"+varname+"' by '"+stack[-1]+"' ( Call stack: "+repr(stack)+' )'
			if self.evaluated.has_key(varname):
				ex += self.evaluated[varname]
			elif self.raw.has_key(varname):
				newstack = stack[:]
				newstack.append(varname)
				ex += self.expand(self.raw[varname],newstack)
			else:
				raise KeyError, "Cannot find variable '"+varname+"'"
		if not fromfile:
			return ex
		else:
			#use "ex" as a filename
			try:
				myfile=open(ex,"r")
			except:
				return "(CANNOTOPEN:"+ex+")"
			outstring=""
			for line in myfile.readlines():
				outstring=outstring+line[:-1]+" "
			myfile.close()
			return outstring[:-1]

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
		#eval() will try to return the value of "element", performing variable expansion and updating self.evaluated on success
		if self.evaluated.has_key(element):
			return self.evaluated[element]
		elif self.raw.has_key(element):
			self.evaluated[element]=self.expand(self.raw[element])
			return self.evaluated[element]
		elif self.lax:
			return ""
		else:
			raise KeyError, "Cannot find element '"+element+"'"
	
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
		print
		print "DEBUG flexdata: "+desc
		print "RAW:"
		print self.raw
		print "EVAL:"
		for key in self.keys():
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

	def parseline(self,openfile=None):
		
		# parseline() will parse a line and return None on EOF, return [] on a blank line with no data, or will
		# return a list of string elements if there is data on the line, split along whitespace: [ "foo:", "bar", "oni" ]
		# parseline() will also remove "# comments" from a line as appropriate
		# parseline() will update self.raw with new data as it finds it.
		curline = openfile.readline()
		if curline == "": #EOF
			return None
		# get list of words separated by whitespace
		mysplit = curline[:-1].strip().split(" ")
		if len(mysplit) == 1:
			if mysplit[0] == '':
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

		if mysplit[0][-1] == ":":
			#basic element - rejoin all data elements with spaces and add to self.raw
			self.raw[mysplit[0][:-1]] = " ".join(mysplit[1:])
		elif len(mysplit) >=3 and mysplit[0] == "?" and mysplit[-1] == "{":
			if self.debug:
				print "DEBUG: CONDITIONAL"
			#conditional block
			if len(mysplit) == 3:
				# we found something in this format:
				# ? foo {
				# (which means: "if foo has been defined to be anything, then evaluate this block...
				if self.raw.has_key(mysplit[1]):
					#yes! it is defined
					while mysplit[0] != "}":
						mysplit=self.parseline(openfile)
				else:
					#otherwise, skip this block
					self.skipblock(openfile)
			elif len(mysplit) >= 4:
				if self.debug:
					print "DEBUG: LEN MYSPLIT 4"
				# we found something in this format:
				# ? foo bar {
				# or
				# ? foo bar oni {
				# (which means: "if foo is defined and evaluates to the string "bar" or "bar oni", then evaluate this block...
				if not self.raw.has_key(mysplit[1]):
					if self.debug:
						print "SKIPPING BLOCK 1"
					self.skipblock(openfile)
				elif self[mysplit[1]] != " ".join(mysplit[2:len(mysplit)-1]):
					if self.debug:
						print "SKIPPING BLOCK 2", " ".join(mysplit[2:len(mysplit)-1])
					self.skipblock(openfile)
				else:
					if self.debug:
						print "DEBUG: EVALUATING BLOCK"
					#we're good - evaluate the block
					while mysplit[0] != "}":
						mysplit=self.parseline(openfile)
			else:
				raise KeyError, "Error parsing line "+repr(mysplit)
		return mysplit	

	def collect(self,filename):
		if not os.path.exists(filename):
			raise IOError, "File '"+filename+"' does not exist."
		if not os.path.isfile(filename):
			raise IOError, "File to be parsed '"+filename+"' is not a regular file."
		openfile = open(filename,"r")

		while 1:
			out=self.parseline(openfile)
			if out == None:
				break
		openfile.close()
