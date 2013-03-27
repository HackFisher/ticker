import jinja2
import os
import time

jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))

import cgi
import webapp2
import json

from google.appengine.api import users
from google.appengine.api import channel
from sets import Set

clients = Set()

class MainPage(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        if not user:
            self.redirect(users.create_login_url(self.request.uri))
            return
		
        client_id = user.user_id() + str(int(round(time.time() * 1000)))
        token = channel.create_channel(client_id)
        clients.add(client_id)

        template_values = {'token': token,
		    'me': user.user_id(),
            'url': users.create_logout_url(self.request.uri),
            'url_linktext': 'Logout',
        }
		
        template = jinja_environment.get_template('index.html')
        self.response.out.write(template.render(template_values))

class SubmitPage(webapp2.RequestHandler):
    def get(self):
        template_values = {}
        template = jinja_environment.get_template('submit.html')
        self.response.out.write(template.render(template_values))

class SendTicker(webapp2.RequestHandler):
    def post(self):
        ticker = {}
        ticker['amout_in'] = self.request.get("amount_in")
        ticker['amount_out'] = self.request.get("amount_out")
        ticker['current'] = self.request.get("current")
        ticker['high'] = self.request.get("high")
        ticker['low'] = self.request.get("low")
        ticker_str = json.dumps(ticker)

        for client_id in clients:
            channel.send_message(client_id, ticker_str)
		
app = webapp2.WSGIApplication([('/', MainPage), ('/send', SendTicker), ('/submit', SubmitPage)],
                              debug=True)
