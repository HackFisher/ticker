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

        template_values = {'token': token,
            'me': user.user_id(),
            'url': users.create_logout_url(self.request.uri),
            'url_linktext': 'Logout',
        }
        
        template = jinja_environment.get_template('index.html')
        self.response.out.write(template.render(template_values))

class SubmitPage(webapp2.RequestHandler):
    """This page is responsible for showing the ticker submit UI.
    Constant nubmer in ticker meanings: 0 means BTC, 1 means RMB"""
    
    def get(self):
        template_values = {}
        # TODO: the buy-sell settings should be show in the UI too.
        template = jinja_environment.get_template('submit.html')
        self.response.out.write(template.render(template_values))
        
    def post(self):
        ticker = {
            "0-1": [    # buy-sell, 0 means BTC, 1 means RMB
                int(round(time.time() * 1000)), #current time, seconds
                # the following number must be int, real value should be devided by 100,000,000
                self.request.get("amount_in"),
                self.request.get("amount_out"),
                self.request.get("current"),
                self.request.get("high"),
                self.request.get("low")
            ]
        }
        ticker_str = json.dumps(ticker)

        for client_id in clients:
            channel.send_message(client_id, ticker_str)
            
class Connected(webapp2.RequestHandler):
    """Post to this means that the client has connected to this channel and can receive message"""
    def post(self):
        client_id = self.request.get('from')
        print client_id + "connected"
        clients.add(client_id)

class Disconnected(webapp2.RequestHandler):
    """Post to this means that the client has disconnected from the channel."""
    def post(self):
        client_id = self.request.get('from')
        print client_id + "disconnected"
        clients.remove(client_id)
            
app = webapp2.WSGIApplication([('/', MainPage), ('/submit', SubmitPage), ('/_ah/channel/connected/', Connected), ('/_ah/channel/disconnected/', Disconnected)],
                              debug=True)
