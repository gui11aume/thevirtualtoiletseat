# -*- coding: utf-8 -*-

import os
import re
import datetime
import random
try:
   import json
except ImportError:
   import simplejson as json

import app_admin

from google.appengine.ext import webapp
from google.appengine.ext import db
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import run_wsgi_app

# ------------------- Local constants ------------------- #
DIRTY = 'The virtual toilet seat is dirty.'
CLEAN = 'The virtual toilet seat is clean.'
# ------------------------------------------------------- #


def identify_from_cookie(request_handler):
   """Return the 'uid' attribute from cookie if properly defined and
   in the data-base (up-to-date), or False otherwise."""

   try:
      return app_admin.User.gql(
                   'WHERE ANCESTOR IS :1 AND uid = :2',
                   app_admin.user_key(),
                   request_handler.request.cookies.get('uid')
             )[0].uid
   except (KeyError, IndexError):
      # No cookie or no longer in the data-base, respectively.
      return False

def user_is_inside(uid):
   """Return 'True' if user has earliest 'first_ping' attribute and
   is still up-to-date, False otherwise."""

   try:
      return app_admin.User.gql(
                   'WHERE ANCESTOR IS :1 ' \
                 + 'ORDER BY first_ping ASC LIMIT 1',
                    app_admin.user_key()
             )[0].uid == uid
   except IndexError:
      return False


class QueueHandler(webapp.RequestHandler):
   """You are technically on the outside. You'll get in only upon
   pinging. Please take a cookie and be patient..."""

   def get(self):
      # There should be an instance of ToiletSeat. If not, create one.
      there_is_no_toilet_seat = app_admin.ToiletSeat.gql(
                                     'WHERE ANCESTOR IS :1',
                                     app_admin.toilet_key()
                                ).count() == 0

      if there_is_no_toilet_seat:
         app_admin.create_toilet_seat()

      # Does user already exist (has a cookie up-to-date)?
      uid = identify_from_cookie(self)
      if not uid:
         # Give user a cookie ID.
         uid = str(random.random())
         app_admin.create_user(uid)
         self.response.headers.add_header('Set-Cookie', 'uid=%s' % uid)

      dot = os.path.dirname(__file__)

      template_path = os.path.join(dot, 'thevirtualtoiletseat_template.html')
      self.response.out.write(
            # User starts pinging.
            open(template_path).read()
      )


class PingHandler(webapp.RequestHandler):
   """Handle user ping. Update 'last_ping' for user with given uid.
   This is where the content sent to the user is made."""

   def post(self):
      # Yes, who is it?
      uid = self.request.get('uid')
      now = datetime.datetime.now()

      # First update user's 'last_ping'.
      user_query = app_admin.User.gql(
                          'WHERE ANCESTOR IS :1 AND uid = :2',
                          app_admin.user_key(),
                          uid
                   )

      if user_query.count() != 1:
         self.response.out.write('Ooops!!')
      else:
         user = user_query[0]
         user.last_ping = now
         user.put()

      # Ditch users who did not ping for more more than NO_PING_TIMEOUT.
      deadline = now - app_admin.NO_PING_TIMEOUT
      ditched_users_query = app_admin.User.gql(
                               'WHERE ANCESTOR IS :1 AND last_ping < :2',
                               app_admin.user_key(),
                               deadline
                            )
      db.delete(ditched_users_query)
 

      dot = os.path.dirname(__file__)

      if user_is_inside(uid):
         # Bingo! You've been lucky or patient. Welcome inside.
         toilet_query = app_admin.ToiletSeat.gql(
                              'WHERE ANCESTOR IS :1 ',
                               app_admin.toilet_key()
                         )
         msg = CLEAN if toilet_query[0].clean else DIRTY
         template_path = os.path.join(dot, 'content', 'inside_content.html')
         template_values = {
            'state': msg,
         }
         content = template.render(template_path, template_values)
         self.response.out.write(content)
      else:
         # There is still someone else inside. See you next ping...
         self.response.out.write(open(os.path.join(
               dot,
               'content',
               'busy_content.html'
         )).read())


  
class ToiletUpdateHandler(webapp.RequestHandler):
   """Handle user action."""

   def post(self):
      # Check that user is inside.
      uid = identify_from_cookie(self)
      # Early return if this POST is forbidden.
      if not user_is_inside(uid):
         return

      toilet_query = app_admin.ToiletSeat.gql(
                           'WHERE ANCESTOR IS :1 ',
                            app_admin.toilet_key()
                      )
      toilet_data = toilet_query[0]
      user_action = self.request.get('action')
      
      if user_action in ('pee', 'poo'):
         toilet_data.clean = False
         msg = DIRTY
      elif user_action in ('flush'):
         toilet_data.clean = True
         msg = CLEAN

      # Save state.
      toilet_data.put()

      # Send response.
      self.response.out.write(msg)




application = webapp.WSGIApplication([
  ('/', QueueHandler),
  ('/update', ToiletUpdateHandler),
  ('/ping', PingHandler),
], debug=True)


def main():
   run_wsgi_app(application)


if __name__ == '__main__':
    main()
