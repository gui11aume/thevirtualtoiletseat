# -*- coding: utf-8 -*-
"""
"""

import sys
import traceback
import datetime

from google.appengine.api import mail
from google.appengine.ext import db

NO_PING_TIMEOUT = datetime.timedelta(seconds=7)

class ToiletSeat(db.Model):
   """Store the state of the toilet seat."""
   clean = db.BooleanProperty()


def toilet_key():
   return db.Key.from_path('ToiletSeat', '1')


class User(db.Model):
   """Store a user."""
   uid = db.StringProperty()
   first_ping = db.DateTimeProperty(auto_now_add=True)
   last_ping = db.DateTimeProperty(auto_now_add=True)


def user_key():
   return db.Key.from_path('User', '1')


def create_toilet_seat():
   """Create an instance of ToiletSeat."""
   toilet_seat = ToiletSeat(toilet_key())
   toilet_seat.clean = True
   toilet_seat.put()


def create_user(uid):
   """Create and initialize a User instance in the data store."""
   user = User(user_key())
   user.uid = uid
   user.put()
   


def mail_admin(user_mail, message=None):
   """Send a mail to admin. If no message is specified,
   send an error traceback."""

   if message is None:
      message = ''.join(traceback.format_exception(
         sys.exc_type,
         sys.exc_value,
         sys.exc_traceback
      ))

   mail.send_mail(
       ADMAIL,
       ADMAIL,
       "Euchronism report",
       "%s:\n%s" % (user_mail, message)
   )
