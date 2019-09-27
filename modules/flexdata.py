#!/usr/bin/python

import sys,os,types,io,string

class FlexDataError(Exception):
	def __init__(self, message):
		if message:
			print()
			print("Metro Parser: "+message)
			print()

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
		self.lax=False
		self.laxvars={}
		self.blanks={}
		# self.collected holds the names of files we've collected (parsed)
		self.collected=[]
		self.section=""
		self.sectionfor={}
		self.conditional=None
		self.collector=[]
		self.collectorcond={}
	
	def clear(self):
		self.raw={}
		self.conditionals={}
		self.blanks={}
		self.definedinfile={}

	def expand_all(self):
		# try to expand all variables to find any undefined elements, to record all blanks or throw an exception
		for key in list(self.keys()):
			myvar = self[key]

	def get_condition_for(self,varname):
		if varname not in self.conditionals:
			return None
		truekeys=[]
		for cond in list(self.conditionals[varname].keys()):
			#if self.conditionOnConditional(cond):
			#	raise FlexDataError, "Not Allowed: conditional variable %s depends on condition %s which is itself a conditional variable." % ( varname, cond )
			if self.conditionTrue(cond):
				truekeys.append(cond)
			if len(truekeys) > 1:
				raise FlexDataError("Multiple true conditions exist for %s: conditions: %s" % (varname, repr(truekeys)))
		if len(truekeys) == 1:
			return self.conditionals[varname][truekeys[0]]
		elif len(truekeys) == 0:
			return None
		else:
			#shouldn't get here
			raise FlexDataError


	def expand(self,myvar,options={}):
		if myvar[-1] == "?":
			boolean = True
			myvar = myvar[:-1]
		else:
			boolean = False
		if myvar in self.raw:
			typetest = self.raw[myvar]
		elif myvar in self.conditionals:
			# test the type of the first conditional - in the future, we should ensure all conditional values are of the same type
			typetest = self.conditionals[myvar][list(self.conditionals[myvar].keys())[0]]
		# FIXME: COME BACK HERE AND FIX THIS
		elif myvar in self.laxvars and self.laxvars[myvar]:
			# record that we looked up an undefined element
			self.blanks[myvar]=True
			if boolean:
				return "no"
			else:
				return ""
		else:
			if boolean:
				return "no"
			else:
				raise FlexDataError("Variable \""+myvar+"\" not found foo")
		if type(typetest) == list:
			if boolean:
				return "yes"
			else:
				return self.expandMulti(myvar,options=options)
		else:
			return self.expandString(myvar=myvar,options=options)

	def expandString(self,mystring=None,myvar=None,stack=[],options={}):
		# Expand all variables in a basic value, ie. a string
		if mystring is None:
			if myvar[-1] == "?":
				boolean = True
				myvar = myvar[:-1]
			else:
				boolean = False
			if myvar in self.raw:
				if boolean:
					if self.raw[myvar].strip() == "":
						# blanks are considered undefined
						mystring = "no"
					else:
						mystring = "yes"
				else:
					mystring = self.raw[myvar]
			else:
				mystring = self.get_condition_for(myvar)
				if mystring is None:
					if boolean:
						mystring = "no"
					elif len(stack) and stack[-1] in self.laxvars and self.laxvars[stack[-1]]:
						mystring = ""
					else:
						raise KeyError("Variable "+repr(myvar)+" not found.")
				elif boolean:
					mystring = "yes"

		#if type(string) != types.StringType:
		#		if len(stack) >=1:
		#		raise FlexDataError("expandString received non-string when expanding "+repr(myvar)+" ( stack = "+repr(stack)+")")
		#	else:
		#		raise FlexDataError("expandString received non-string: %s" % repr(string) )

		if type(mystring) != list:
			mysplit = mystring.strip().split(" ")
		else:
			# concatenate multi-line element, then strip
			mysplit = []
			for line in mystring:
				mysplit.append(line.strip())
			mystring = " ".join(mysplit).strip()
			mysplit = mystring.split(" ")

		if len(mysplit) == 2 and mysplit[0] == "<<":
			fromfile = True
			mystring = " ".join(mysplit[1:])
		else:
			fromfile = False

		unex = mystring
		ex = ""
		while unex != "":
			varpos = unex.find(self.pre)
			if varpos == -1:
				ex += unex
				unex = ""
				continue
			if unex[varpos:varpos+len(self.pre)+1] == "$[[":
				# extra [, so it's a multi-line element .... which we just pass to the output unexpanded since it might be comented out...
				# (we don't want to throw an excption if someone put a # in front of it.
				ex += unex[0:varpos+len(self.pre)+1]
				unex = unex[varpos+len(self.pre)+1:]
				continue
			# OK, this looks like a regular single-line element
			ex += unex[0:varpos]
			unex = unex[varpos+len(self.pre):] # remove "$["
			endvarpos = unex.find(self.suf)
			if endvarpos == -1:
				raise FlexDataError("Error expanding variable for '"+mystring+"'")
			varname = unex[0:endvarpos]
			if len(varname)>0 and varname[-1] == "?":
				boolean = True
				varname = varname[:-1]
			else:
				boolean = False
			# $[] and $[:] expansion
			if varname == "" or varname == ":":
				if myvar in self.sectionfor:
					varname = self.sectionfor[myvar]
				else:
					raise FlexDataError("no section name for "+myvar+" in "+mystring)
			# NEW STUFF BELOW:
			elif varname[0] == ":":
				# something like $[:foo/bar]
				if myvar in self.sectionfor:
					varname = self.sectionfor[myvar]+"/"+varname[1:]
				else:
					raise FlexDataError("no section name for "+myvar+" in "+mystring)
			varsplit=varname.split(":")
			newoptions=options.copy()
			zapmode=False
			if len(varsplit) == 1:
				pass
			elif len(varsplit) == 2:
				if varsplit[1] == "zap":
					zapmode=True
					varname=varsplit[0]
				elif varsplit[1] == "lax":
					newoptions["lax"]=True
					varname=varsplit[0]
				else:
					raise FlexDataError("expanding variable %s - mode %s does not exist" % (varname, varsplit[1]))
			else:
				raise FlexDataError('expanding variable %s - invalid variable' % varname)
			unex = unex[endvarpos+len(self.suf):]
			if varname in stack:
				raise KeyError("Circular reference of '"+varname+"' by "+repr(myvar)+" ( Call stack: "+repr(stack)+' )')
			if varname in self.raw:
				# if myvar == None, we are being called from self.expand_all() and we don't care where we are being expanded from
				#if myvar != None and type(self.raw[varname]) == types.ListType:
				#	raise FlexDataError,"Trying to expand multi-line value "+repr(varname)+" in single-line value "+repr(myvar)
				newstack = stack[:]
				newstack.append(myvar)
				if not boolean:
					newex = self.expandString(self.raw[varname],varname,newstack,options=newoptions)
					if newex == "" and zapmode==True:
						# when expandMulti gets None, it won't add this line so we won't get a blank line even
						return None
					else:
						if newex != None:
							ex += newex
						else:
							return None
				else:
					# self.raw[varname] can be a list .. if it's a string and blank, we treat it as undefined.
					if type(self.raw[varname]) == bytes and self.raw[varname].strip() == "":
						ex += "no"
					else:
						ex += "yes"
			elif varname in self.conditionals:
				expandme = self.get_condition_for(varname)
				newstack=stack[:]
				newstack.append(myvar)
				if expandme == None:
					raise KeyError("Variable %s not found (stack: %s )" % (varname, repr(newstack)))
				if not boolean:
					ex += self.expandString(expandme,varname,newstack,options=newoptions)
				else:
					ex += "yes"
			else:
				if zapmode:
					# a ":zap" will cause the line to be deleted if there is no variable defined or the var evals to an empty string
					# when expandMulti gets None, it won't add this line so we won't get a blank line even
					return None
				if ("lax" in list(newoptions.keys())) or (len(stack) and stack[-1] in self.laxvars and self.laxvars[stack[-1]]):
					# record variables that we attempted to expand but were blank, so we can inform the user of possible bugs
					if boolean:
						ex += "no"
					else:
						self.blanks[varname] = True
						ex += ""
				else:
					if not boolean:
						raise KeyError("Cannot find variable %s (in %s)" % (varname,myvar))
					else:
						ex += "no"
		if fromfile == False:
			return ex

		#use "ex" as a filename
		try:
			myfile=open(ex,"r")
		except:
			raise FlexDataError("Cannot open file "+ex+" specified in variable \""+mystring+"\"")
		outstring=""
		for line in myfile.readlines():
			outstring=outstring+line[:-1]+" "
		myfile.close()
		return outstring[:-1]


	def expandMulti(self,myvar,stack=[],options={}):
		# TODO: ADD BOOLEAN SUPPORT HERE - NOT DONE YET
		mylocals = {}
		myvarsplit=myvar.split(":")
		# any future expansions will get our "new" options, but we don't want to pollute our current options by modifying
		# options...
		newoptions=options.copy()
		# detect and properly handle $[[foo:lax]]
		if len(myvarsplit) == 2:
			if myvarsplit[1] == "lax":
				newoptions["lax"] = True
				myvar = myvarsplit[0]
			else:
				raise FlexDataError("Invalid multi-line variable")

		# Expand all variables in a multi-line value. stack is used internally to detect circular references.
		if myvar in self.raw:
			multi = self.raw[myvar]
			if type(multi) != list:
				raise FlexDataError("expandMulti received non-multi")
		else:
			multi = self.get_condition_for(myvar)
			if multi == None:
				if ("lax" in list(newoptions.keys())) or (len(stack) and stack[-1] in self.laxvars and self.laxvars[stack[-1]]):
					self.blanks[myvar] = True
					return ""
				else:
					raise FlexDataError("referenced variable \""+myvar+"\" not found")
		newlines=[]

		pos=0
		while pos<len(multi):
			mystrip = multi[pos].strip()
			mysplit = mystrip.split(" ")
			if len(mysplit) > 0 and len(mysplit) < 3 and mystrip[0:3] == "$[[" and mystrip[-2:] == "]]":
				myref=mystrip[3:-2]
				if myref in stack:
					raise FlexDataError("Circular reference of '"+myref+"' by '"+stack[-1]+"' ( Call stack: "+repr(stack)+' )')
				newstack = stack[:]
				newstack.append(myvar)
				newlines += self.expandMulti(self.expandString(mystring=myref),newstack,options=newoptions)
			elif len(mysplit) >=1 and mysplit[0] == "<?python":
				sys.stdout = io.StringIO()
				mycode=""
				pos += 1
				while (pos < len(multi)):
					newsplit = multi[pos].split()
					if len(newsplit) >= 1 and newsplit[0] == "?>":
						break
					else:
						mycode += multi[pos] + "\n"
						pos += 1
				exec(mycode, { "os": os }, mylocals)
				newlines.append(sys.stdout.getvalue())
				sys.stdout = sys.__stdout__
			else:
				newline = self.expandString(mystring=multi[pos],options=newoptions)
				if newline != None:
					newlines.append(newline)
			pos += 1
		return newlines

	def __setitem__(self,key,value):
		if self.immutable and key in self.raw:
			raise IndexError("Attempting to redefine "+key+" to "+value+" when immutable.")
		self.raw[key]=value
		self.definedinfile[key] = "via __setitem__"

	def __delitem__(self,key):
		if self.immutable and key in self.raw:
			raise IndexError("Attempting to delete "+key+" when immutable.")
		del self.raw[key]
		if key in self.definedinfile:
			del self.definedinfile[key]

	def __getitem__(self,element):
		return self.expand(element)

	def __contains__(self,element):
		return self.has_key(element)

	def has_key(self,key):
		if key in self.raw:
			return True
		else:
			ret = self.get_condition_for(key)
		if ret != None:
			return True
		else:
			return False

	def keys(self):
		mylist=list(self.raw.keys())
		for x in self.conditionals:
			mycond = self.get_condition_for(x)
			if mycond != None:
				mylist.append(x)
		return mylist

	def missing(self,keylist):
		""" return list of any keys that are not defined. good for validating that we have a bunch of required things defined."""
		missing=[]
		for key in keylist:
			if key not in self.raw:
				missing.append(key)
		return missing

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

	def parseline(self,filename,openfile=None,origfile=None,dups=False):

		# parseline() will parse a line and return None on EOF, return [] on a blank line with no data, or will
		# return a list of string elements if there is data on the line, split along whitespace: [ "foo:", "bar", "oni" ]
		# parseline() will also remove "# comments" from a line as appropriate
		# parseline() will update self.raw with new data as it finds it.
		if type(openfile) == bytes:
			curline = openfile + '\n'
		else:
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
			# for myvar, remove trailing colon:
			myvar = mysplit[0][:-1]
			if self.section:
				myvar = self.section+"/"+myvar
				self.sectionfor[myvar] = self.section
			self.laxvars[myvar] = self.lax
			mylines = []
			while 1:
				curline = openfile.readline()
				if curline == "":
					raise KeyError("Error - incomplete [[ multi-line block,")
				mysplit = curline[:-1].strip().split(" ")
				if len(mysplit) == 1 and mysplit[0] == "]":
					# record value and quit
					# FIXME - MISSING COND HERE!?!?!?
					if self.conditional:
						if myvar not in self.conditionals:
							self.conditionals[myvar]={}
						if self.conditional in self.conditionals[myvar]:
							raise FlexDataError("Conditional element %s already defined for condition %s" % (myvar, self.conditional))
						self.conditionals[myvar][self.conditional] = mylines
					elif not dups and myvar in self.raw:
						if self.definedinfile[myvar] == filename:
							raise FlexDataError("Error - file %s was already collected, duplicate definitions." % filename)
						else:
							raise FlexDataError("Error - in parsing %s: \"%s\" already defined in %s" % (filename, myvar, self.definedinfile[myvar]))
					else:
						self.raw[myvar] = mylines
						self.definedinfile[myvar] = filename
					break
				else:
					# append new line
					mylines.append(curline[:-1])
		elif mysplit[0][0]=="[" and mysplit[-1][-1]=="]":
			# possible section
			mysplit[0] = mysplit[0][1:]
			mysplit[-1]= mysplit[-1][:-1]
			mysection=' '.join(mysplit).split()
			if mysection[0] == "section":
				self.section = mysection[1]
				if len(mysection) > 2:
					if mysection[2] != "when":
						raise FlexDataError("Expecting \"when\": "+curline[:-1])
					self.conditional=" ".join(mysection[3:])
					if self.conditional == "*":
						self.conditional = None
				elif len(mysection) == 2:
					# clear conditional:
					self.conditional = None
				else:
					raise FlexDataError("Invalid section specifier: "+curline[:-1])
			elif mysection[0] == "option":
				if mysection[1] == "parse/lax":
					self.lax = True
				elif mysection[1] == "parse/strict":
					self.lax = False
				else:
					raise FlexDataError("Unexpected option in [option ] section: %s" % mysection[1])
			elif mysection[0] == "when":
				# conditional block
				self.conditional=" ".join(mysection[1:])
				if self.conditional == "*":
					self.conditional = None
			elif mysection[0] == "collect":
				if self.conditional:
					# This part of the code handles a [collect] annotation that appears inside a [when] block - we use the [when] condition in this case
					if len(mysection)>=3:
						raise FlexDataError("Conditional collect annotations not allowed inside \"when\" annotations: %s" % repr(mysection))
					self.collectorcond[mysection[1]]=self.conditional
					# append what to collect, followed by the filename that the collect annotation appeared in. We will use this later, for
					# expanding relative paths.
					self.collector.append([mysection[1],filename]),
				elif len(mysection)>3:
					if mysection[2] == "when":
						self.collectorcond[mysection[1]]=" ".join(mysection[3:])
						# even with a conditional, we still put the thing on the main collector list:
						self.collector.append([mysection[1],filename])
						#self.collector.append(mysection[1])
					else:
						raise FlexDataError("Ow, [collect] clause seems invalid")
				elif len(mysection)==2:
					self.collector.append([mysection[1],filename])
				else:
					raise FlexDataError("Ow, [collect] expects 1 or 4+ arguments.")
			else:
				raise FlexDataError("Invalid annotation: %s in %s" % (mysection[0], curline[:-1]))
		elif mysplit[0][-1] == ":":
			#basic element - rejoin all data elements with spaces and add to self.raw
			mykey = mysplit[0][:-1]
			if mykey == "":
				# ":" tag
				mykey = self.section
			elif self.section:
				mykey = self.section+"/"+mykey
				self.sectionfor[mykey]=self.section
			self.laxvars[mykey]=self.lax
			myvalue = " ".join(mysplit[1:])
			if self.conditional:
				if mykey not in self.conditionals:
					self.conditionals[mykey]={}
				if self.conditional in self.conditionals[mykey]:
					raise FlexDataError("Conditional element %s already defined for condition %s" % (mykey, self.conditional))
				self.conditionals[mykey][self.conditional] = myvalue
			else:
				if not dups and mykey in self.raw:
					raise FlexDataError("Error - \""+mykey+"\" already defined. Value: %s. New line: %s." % ( repr(self.raw[mykey]), curline[:-1] ))
				self.raw[mykey] = myvalue
		return mysplit

	def collect(self,filename,origfile):
		if not os.path.isabs(filename):
			# relative path - use origfile (the file the collect annotation appeared in) to figure out what we are relative to
			filename=os.path.normpath(os.path.dirname(origfile)+"/"+filename)
		if not os.path.exists(filename):
			raise IOError("File '"+filename+"' does not exist.")
		if not os.path.isfile(filename):
			raise IOError("File to be parsed '"+filename+"' is not a regular file.")
		self.conditional = None
		openfile = open(filename,"r")
		self.section=""
		while 1:
			out=self.parseline(filename,openfile)
			if out == None:
				break
		openfile.close()
		# add to our list of parsed files
		if self.debug:
			sys.stdout.write("Debug: collected: %s\n" % os.path.normpath(filename))
		self.collected.append(os.path.normpath(filename))

	def conditionOnConditional(self,cond):
		"""defining a conditial var based on another conditional var is illegal. This function will tell us if we are in this mess."""
		if cond == None:
			return False
		cond=cond.split()
		if len(cond) == 1:
			if cond[0] in self.raw:
				return False
			elif cond[0] in self.conditionals:
				return True
			else:
				# undefined
				return False
		elif len(cond) == 0:
			raise FlexDataError("Condition %s is invalid" % cond)
		elif len(cond) >= 3:
			if cond[1] not in [ "is", "in"]:
				raise FlexDataError("Expecting 'is' or 'in' in %s" % cond)
			if cond[0] in self.raw:
				return False
			elif cond[0] in self.conditionals:
				return True
			else:
				# undefined
				return False


	def conditionTrue(self,cond):
		cond=cond.split()
		if len(cond) == 1:
			if cond[0] in self.raw:
				return True
			else:
				return False
		elif len(cond) == 0:
			raise FlexDataError("Condition "+repr(cond)+" is invalid")
		elif len(cond) >= 3 and cond[1] in [ "is", "in" ]:
			if cond[0] not in self.raw:
				# maybe it's not defined
				return False
			# loop over multiple values, such as "target is ~x86 x86 amd64", if one is equal, then it's true
			for curcond in cond[2:]:
				if self[cond[0]] == curcond:
					return True
			return False
		else:
			raise FlexDataError("Invalid condition")


	def runCollector(self):
		# BUG? we may need to have an expandString option that will disable the ability to go to the evaluated dict,
		# because as we parse new files, we have new data and some "lax" evals may evaluate correctly now.

		# BUG: detect if we are trying to collect a single file multiple times. :)

		# contfails means "continuous expansion failures" - if we get to the point where we are not making progress,
		# ie. contfails >= len(self.collector), then abort with a failure as we can't expand our cute little variable.
		contfails = 0
		oldlax = self.lax
		self.lax = False
		while len(self.collector) != 0 and contfails < len(self.collector):
			# grab the first item from our collector list
			try:
				myitem, origfile = self.collector[0]
			except ValueError:
				raise FlexDataError(repr(self.collector[0])+" does not appear to be good")
			if myitem in self.collectorcond:
				cond = self.collectorcond[myitem]
				if self.conditionOnConditional(cond):
					raise FlexDataError("Collect annotation %s has conditional %s that references a conditional variable, which is not allowed." % (myitem, cond))
				# is the condition true?:
				if not self.conditionTrue(cond):
					contfails += 1
					self.collector = self.collector[1:] + [self.collector[0]]
					continue
				else:
					try:
						myexpand = self.expandString(mystring=myitem)
					except KeyError:
						contfails +=1
						self.collector = self.collector[1:] + [self.collector[0]]
						continue
					self.collect(myexpand, origfile)
					self.collector=self.collector[1:]
					contfails = 0
			else:
				try:
					myexpand = self.expandString(mystring=myitem)
				except KeyError:
					contfails += 1
					# move failed item to back of list
					self.collector = self.collector[1:] + [self.collector[0]]
					continue
				# read in data:
				if myexpand not in [ "", None ]:
					# if expands to blank, with :zap, we skip it: (a silly fix for now)
					self.collect(myexpand, origfile)
				# we already parsed it, so remove filename from list:
				self.collector = self.collector[1:]
				# reset continuous fail counter, we are making progress:
				contfails = 0
		self.lax=oldlax
		# leftovers are ones that had false conditions, so we don't want to raise an exception:
		#if len(self.collector) != 0:
		#	raise FlexDataError, "Unable to collect all files - uncollected are: "+repr(self.collector)

if __name__ == "__main__":
	coll = collection(debug=False)
	for arg in sys.argv[1:]:
		coll.collect(arg)
	coll.runCollector()
	sys.exit(0)

# vim: ts=4 sw=4 noet
