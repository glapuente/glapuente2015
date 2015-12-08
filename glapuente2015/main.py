#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import webapp2
import os
import urllib
import cgi
import re


import jinja2
JINJA_ENVIRONMENT = jinja2.Environment(
	loader=jinja2.FileSystemLoader(os.path.join(os.path.dirname(__file__), 'templates')))	


class Links(webapp2.RequestHandler):
    def get(self):
		template=JINJA_ENVIRONMENT.get_template('index.html')
		self.response.write(template.render())

class MainHandler(webapp2.RequestHandler):
    def get(self):
		template=JINJA_ENVIRONMENT.get_template('saludoEN.html')
		self.response.write(template.render())

class MainHandlerES(webapp2.RequestHandler):
    def get(self):
		template=JINJA_ENVIRONMENT.get_template('saludoES.html')
		self.response.write(template.render())
		
class MainHandlerEUS(webapp2.RequestHandler):
    def get(self):
		template=JINJA_ENVIRONMENT.get_template('saludoEUS.html')
		self.response.write(template.render())
		
class LoginForm(webapp2.RequestHandler):
	def get(self):
		template=JINJA_ENVIRONMENT.get_template('login_form.html')
		self.response.write(template.render())
		
class ValidarHandle(webapp2.RequestHandler):
	def post(self):
		username = cgi.escape(self.request.get('username'),quote=True)
		email = cgi.escape(self.request.get('email'),quote=True)
		password = cgi.escape(self.request.get('password'),quote=True)
		rePassword = cgi.escape(self.request.get('rePassword'),quote=True)
		
		html_error_msg=""
		error_flag=1
		
		# Empty fields
		if(username==""):
			html_error_msg+="<h3>The username field cannot be empty</h3></hr>"
			error_flag=-1
		if(email==""):
			html_error_msg+="<h3>The email field cannot be empty</h3></hr>"
			error_flag=-1
		if(password=="" or rePassword==""):
			html_error_msg+="<h3>The password field cannot be empty</h3></hr>"
			error_flag=-1
		
		# Repeat passwords
		if(password!=rePassword):
			html_error_msg+="<h3>The passwords must match</h3></hr>"
			error_flag=-1
		
		# Password regexp - Min. 8 Max.12. At least 1 num, lower and upper
		if not re.match("((?=.*\d)(?=.*[a-z])(?=.*[A-Z]).{8,12})",password):
			html_error_msg+="<h3>The password does not comply with the pattern</h3></hr>"
			error_flag=-1
			
		if not re.match("^[a-zA-Z0-9._%-+]+@[a-zA-Z0-9._%-]+.[a-zA-Z]{2,6}$",email):
			html_error_msg+="<h3>The email does not comply with the pattern</h3></hr>"
			error_flag=-1

		tpl_vars={"username":username,"email":email}

		if(error_flag==-1):
			template=JINJA_ENVIRONMENT.get_template('login_form.html')
			self.response.write(template.render(tpl_vars))
			self.response.write(html_error_msg)
		else:
			self.response.write("<h1>Bienvenido "+username+"</h1>")
		
		

app = webapp2.WSGIApplication([
    ('/', Links),
    ('/saludaEN', MainHandler),
    ('/saludaES', MainHandlerES),
	('/saludaEUS', MainHandlerEUS),
	('/loginForm', LoginForm),
	('/validar', ValidarHandle)
], debug=True)
