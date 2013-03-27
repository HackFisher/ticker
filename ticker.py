import jinja2
import os
import time

jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))

import cgi
import webapp2

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
        token = channel.create_channel(user.user_id())
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

    def post(self):
        amount_in = self.request.get("amount_in")
        amount_out = self.request.get("amount_out")
        current = self.request.get("current")
        high = self.request.get("high")
        low = self.request.get("low")

class TickerPage(webapp2.RequestHandler):
    def post(self):
        self.response.out.write('<html><body>You wrote:<pre>')
        self.response.out.write(cgi.escape(self.request.get('content')))
        self.response.out.write('</pre></body></html>')
		
		
app = webapp2.WSGIApplication([('/', MainPage), ('/ticker', TickerPage), ('/submit', SubmitPage)],
                              debug=True)