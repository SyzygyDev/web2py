#!/usr/bin/env python
# coding: utf8
from gluon import *

class Logging:
	def __init__(self, db):
		self.db = db

	def log_activity(self, action, userID):
		self.db.staff_logs.insert(staff_id=userID, staff_action=action)