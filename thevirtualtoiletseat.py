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


class ToiletSeatHandler(webapp.RequestHandler):
   """Welcome to the toilet seat!!"""

   def get(self):
      # There should be an instance of ToiletSeat. If not, create one.
      there_is_no_toilet_seat = app_admin.ToiletSeat.gql(
                                     'WHERE ANCESTOR IS :1',
                                     app_admin.toilet_key()
                                ).count() == 0

      if there_is_no_toilet_seat:
         app_admin.create_toilet_seat()

      # Give user an ID
      uid = str(random.random())
      app_admin.create_user(uid)
      self.response.headers.add_header('Set-Cookie', 'uid=%s' % uid)

      dot = os.path.dirname(__file__)

      template_path = os.path.join(dot, 'thevirtualtoiletseat_template.html')
      template_values = {
         'page_title': 'Welcome to the virtual toilet seat',
         'page_content': open(os.path.join(
                                  dot,
                                  'content',
                                  'inside_content.html'
                             )).read()
      }

      # ... and send!
      self.response.out.write(
            template.render(template_path, template_values)
      )


class ToiletUpdateHandler(webapp.RequestHandler):
   """Handle user action."""

   def post(self):
      query_result = app_admin.ToiletSeat.gql(
                 'WHERE ANCESTOR IS :1',
                 app_admin.toilet_key()
             )
      toilet_data = query_result[0]
      user_action = self.request.get('action')
      
      if user_action in ('pee', 'poo'):
         toilet_data.clean = False
         msg = 'The virtual toilet seat is dirty.'
      elif user_action in ('flush'):
         toilet_data.clean = True
         msg = 'The virtual toilet seat is clean.'

      # Save state.
      toilet_data.put()

      # Send response.
      self.response.out.write(msg)


class Ping(webapp.RequestHandler):
   """Handle user ping. Update 'last_ping' for user with given uid."""

   def post(self):
      uid = self.request.get('uid')
      query_result = app_admin.User.gql(
                 'WHERE ANCESTOR IS :1 AND uid = :2',
                 app_admin.user_key(),
                 uid
             )
      user_data = query_result[0]
      user_data.last_ping = datetime.datetime.now()
      user_data.put()

      # Send response.
      self.response.out.write('OK')


application = webapp.WSGIApplication([
  ('/', ToiletSeatHandler),
  ('/update', ToiletUpdateHandler),
], debug=True)


def main():
   run_wsgi_app(application)


if __name__ == '__main__':
    main()
