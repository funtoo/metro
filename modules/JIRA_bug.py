#!/usr/bin/env python3

import json
import datetime, os, sys, socket
from bug_utils import JIRA

class JIRAHook(object):

	def __init__(self, jira_url, jira_user, jira_pass, settings):
		self.settings = settings
		self.jira = JIRA(jira_url, jira_user, jira_pass)

	def _bugSubject(self):
		# helper method -- return a subject for this particluar bug.
		return "Metro QA: %s (%s) failure on %s" % ( self.settings["target/build"], self.settings["target/subarch"], self.hostname() )

	def hostname(self):
		return socket.gethostname()

	def info(self):
		out = {}
		for x in [ "build", "arch_desc", "subarch", "version" ]:
			k = "target/" + x
			if self.settings.has_key(k):
				out[x] = self.settings[k]
		if "target" in self.settings:
			out["target"] = self.settings["target"]
		if "path/mirror/target/path" in self.settings:
			out["path"] = self.settings["path/mirror/target/path"]
			err_fn = out["path"] + "/log/errors.json"
			if os.path.exists(err_fn):
				a = open(err_fn,"r")
				out["failed_ebuilds"] = json.loads(a.read())
				a.close()
		if "success" in self.settings:
			out["success"] = self.settings["success"]
		return out

	def _allMatching(self):
		i = self.jira.getAllIssues({'jql' : 'Summary ~ "\\"%s\\"" and project = QA and status != closed' % self._bugSubject(), 'maxresults' : 1000 })
		if i != None and "issues" in i:
			return i["issues"]
		else:
			return []

	def _existingBug(self):
		# helper method -- does an existing bug for this build failure exist?
		return len(self._allMatching()) != 0

	def onFailure(self):
		matching = self._allMatching()
		if not matching:
			print("no matching issues... creating one.")
			# If one doesn't exist, create a new issue...
			jira_key = self.jira.createIssue(
				project='QA',
				title= self._bugSubject(),
				description="A build failure has occurred. Details below:\n{code}\n" +
				json.dumps(self.info(), indent=4, sort_keys=True) + "\n{code}\n"
			)
			print(jira_key)
		else:
			print("found a matching issue.")
			# Update comment with new build failure info, to avoid creating a brand new bug.
			for match in matching:
				print("processing issue (comment)")
				self.jira.commentOnIssue(match,"Another build failure has occurred. Details below:\n{code}\n" + 
					json.dumps(self.info(), indent=4, sort_keys=True) + "\n{code}\n"
				)

	def onSuccess(self):
		for i in self._allMatching():
			print("Closing matching issue %s" % i['key'])	
			self.jira.commentOnIssue(i,"Build completed successfully. Closing. Details below:\n{code}\n" +
				json.dumps(self.info(), indent=4, sort_keys=True) + "\n{code}\n"
			)
			self.jira.closeIssue(i)

	def run(self):
		if self.settings["success"] == "yes":
			return self.onSuccess()
		else:
			return self.onFailure()

# vim: ts=4 sw=4 noet
